"""
kb_retriever.py
================

Retriever Hybride du pipeline FLYNC.

Combine deux signaux de pertinence pour retrouver la classe la plus adaptée
à un scénario textuel donné :

    1. Un signal lexical TF-IDF (scikit-learn) calculé sur un corpus
       constitué du nom de classe, des docstrings, des noms de champs, des
       noms de bases et des noms de méthodes de chaque classe indexée.
    2. Un signal structurel AST (correspondances exactes/substring sur les
       noms de classes, champs et alias), utilisé pour "booster" le score
       lexical.

Un backend vectoriel optionnel (Ollama, modèle ``qwen3-embedding`` par
défaut) peut être activé pour remplacer/compléter le signal TF-IDF par une
similarité cosinus sur des embeddings denses, utile lorsque le scénario est
formulé en langage naturel très éloigné du vocabulaire du code.
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Le package 'numpy' est requis par kb_retriever.py. "
        "Installez-le avec: pip install numpy"
    ) from exc

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Le package 'scikit-learn' est requis par kb_retriever.py. "
        "Installez-le avec: pip install scikit-learn"
    ) from exc

from flync_pipeline.etape2_lecteur.agent_lecteur_analyste import ClassInfo

logger = logging.getLogger("flync.kb_retriever")

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _camel_to_tokens(identifier: str) -> List[str]:
    """Découpe un identifiant CamelCase/snake_case en tokens lexicaux."""
    spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", identifier)
    spaced = spaced.replace("_", " ")
    return [tok.lower() for tok in _TOKEN_RE.findall(spaced) if tok]


@dataclass
class RetrievalCandidate:
    """Une classe candidate avec son score de similarité et son détail."""

    class_metadata: ClassInfo
    score: float
    tfidf_score: float = 0.0
    ast_boost: float = 0.0
    embedding_score: float = 0.0
    matched_tokens: List[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    """Résultat complet d'une requête de récupération."""

    query: str
    best_candidate: Optional[RetrievalCandidate]
    candidates: List[RetrievalCandidate]

    @property
    def best_class(self) -> Optional[ClassInfo]:
        return self.best_candidate.class_metadata if self.best_candidate else None

    @property
    def best_score(self) -> float:
        return self.best_candidate.score if self.best_candidate else 0.0


class OllamaEmbeddingBackend:
    """
    Backend d'embeddings optionnel s'appuyant sur un serveur Ollama local
    (par défaut ``http://localhost:11434``) et le modèle ``qwen3-embedding``.

    Ce backend est chargé paresseusement : l'import de ``requests`` et la
    connexion réseau ne sont tentés qu'à la première utilisation, afin de ne
    jamais bloquer le pipeline si Ollama n'est pas disponible.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3-embedding",
        timeout_seconds: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import requests  # noqa: F401

            resp = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout_seconds)
            self._available = resp.status_code == 200
        except Exception as exc:  # pragma: no cover - dépend de l'environnement
            logger.debug("Backend Ollama indisponible: %s", exc)
            self._available = False
        return self._available

    def embed(self, texts: Sequence[str]) -> Optional[np.ndarray]:
        """Retourne une matrice (n_texts, dim) d'embeddings ou None en cas d'échec."""
        if not self.is_available():
            return None
        try:
            import requests

            vectors: List[List[float]] = []
            for text in texts:
                resp = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=self.timeout_seconds,
                )
                resp.raise_for_status()
                payload = resp.json()
                vectors.append(payload["embedding"])
            return np.array(vectors, dtype=np.float64)
        except Exception as exc:  # pragma: no cover - dépend de l'environnement
            logger.warning("Échec de la génération d'embeddings via Ollama: %s", exc)
            return None


class HybridKBRetriever:
    """
    Retriever hybride combinant un index TF-IDF sur le corpus lexical des
    classes indexées et un boost structurel basé sur la correspondance AST
    directe (nom de classe, champs, bases).

    Utilisation typique::

        retriever = HybridKBRetriever()
        retriever.index_classes(kb.all_classes())
        result = retriever.retrieve_relevant_classes("envoyer un message SOME/IP")
    """

    def __init__(
        self,
        use_embeddings: bool = False,
        embedding_backend: Optional[OllamaEmbeddingBackend] = None,
        ast_boost_weight: float = 0.35,
        embedding_weight: float = 0.5,
    ) -> None:
        self._classes: List[ClassInfo] = []
        self._corpus: List[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._tfidf_matrix = None
        self._class_tokens: List[set] = []
        self._embedding_matrix: Optional[np.ndarray] = None

        self.use_embeddings = use_embeddings
        self.embedding_backend = embedding_backend or OllamaEmbeddingBackend()
        self.ast_boost_weight = ast_boost_weight
        self.embedding_weight = embedding_weight

    # ------------------------------------------------------------------ #
    # Indexation
    # ------------------------------------------------------------------ #

    def _build_document_for_class(self, cls: ClassInfo) -> str:
        parts: List[str] = []
        parts.extend(_camel_to_tokens(cls.name))
        parts.extend(_camel_to_tokens(cls.module))
        for base in cls.bases:
            parts.extend(_camel_to_tokens(base.split(".")[-1]))
        if cls.docstring:
            parts.extend(_TOKEN_RE.findall(cls.docstring.lower()))
        for f in cls.fields:
            parts.extend(_camel_to_tokens(f.name))
            parts.extend(_camel_to_tokens(f.type_str.split("[")[0]))
        # ClassInfo n'a pas de liste generale de methodes (contrairement a
        # l'ancien ClassMetadata) : on utilise les signaux disponibles a la
        # place, pertinents pour le retrieval semantique.
        for v in cls.validators:
            parts.extend(_camel_to_tokens(v.method_name))
        if cls.is_enum:
            parts.append("enum")
            for member in cls.enum_members:
                parts.extend(_camel_to_tokens(member))
        return " ".join(parts)

    def index_classes(self, classes: Sequence[ClassInfo]) -> None:
        """
        Construit l'index TF-IDF (et, si activé, l'index vectoriel) à partir
        de la liste de classes fournie. Doit être appelée avant tout appel à
        :meth:`retrieve_relevant_classes`.
        """
        self._classes = list(classes)
        if not self._classes:
            logger.warning("index_classes() appelée avec une liste de classes vide.")
            self._corpus = []
            self._vectorizer = None
            self._tfidf_matrix = None
            self._class_tokens = []
            self._embedding_matrix = None
            return

        self._corpus = [self._build_document_for_class(cls) for cls in self._classes]
        self._class_tokens = [set(doc.split()) for doc in self._corpus]

        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            token_pattern=r"(?u)\b[a-zA-Z0-9_]+\b",
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=1,
        )
        self._tfidf_matrix = self._vectorizer.fit_transform(self._corpus)

        if self.use_embeddings:
            embeddings = self.embedding_backend.embed(self._corpus)
            if embeddings is not None:
                self._embedding_matrix = embeddings
            else:
                logger.info(
                    "Backend d'embeddings indisponible : repli sur TF-IDF seul."
                )

        logger.info(
            "Index hybride construit : %d classes, %d documents.",
            len(self._classes),
            len(self._corpus),
        )

    # ------------------------------------------------------------------ #
    # Récupération
    # ------------------------------------------------------------------ #

    def _ast_boost(self, query_tokens: set, class_index: int) -> float:
        """
        Calcule un boost structurel [0, 1] en fonction du recouvrement exact
        entre les tokens de la requête et les tokens lexicaux de la classe
        (nom de classe, champs, bases).
        """
        cls = self._classes[class_index]
        class_name_tokens = set(_camel_to_tokens(cls.name))
        field_tokens = set()
        for f in cls.fields:
            field_tokens.update(_camel_to_tokens(f.name))

        exact_class_match = 1.0 if class_name_tokens and class_name_tokens.issubset(query_tokens) else 0.0
        partial_class_match = len(class_name_tokens & query_tokens) / max(len(class_name_tokens), 1)
        field_match = len(field_tokens & query_tokens) / max(len(field_tokens), 1) if field_tokens else 0.0

        boost = 0.5 * exact_class_match + 0.35 * partial_class_match + 0.15 * field_match
        return min(boost, 1.0)

    def retrieve_relevant_classes(
        self,
        scenario_text: str,
        top_k: int = 3,
        min_score: float = 0.15,
    ) -> RetrievalResult:
        """
        Retourne les classes les plus pertinentes pour un texte de scénario.

        :param scenario_text: description en langage naturel du scénario.
        :param top_k: nombre maximum de candidats retournés.
        :param min_score: score minimal (après fusion des signaux) pour
            qu'un candidat soit conservé dans le résultat.
        :return: un :class:`RetrievalResult` contenant la meilleure classe,
            ses métadonnées, et la liste ordonnée des candidats.
        """
        if not self._classes or self._vectorizer is None or self._tfidf_matrix is None:
            logger.warning("retrieve_relevant_classes() appelée avant index_classes().")
            return RetrievalResult(query=scenario_text, best_candidate=None, candidates=[])

        query_vec = self._vectorizer.transform([scenario_text])
        tfidf_scores = cosine_similarity(query_vec, self._tfidf_matrix).flatten()

        embedding_scores = np.zeros_like(tfidf_scores)
        if self._embedding_matrix is not None:
            query_embedding = self.embedding_backend.embed([scenario_text])
            if query_embedding is not None:
                embedding_scores = cosine_similarity(
                    query_embedding, self._embedding_matrix
                ).flatten()

        query_tokens = set(_TOKEN_RE.findall(scenario_text.lower()))
        query_tokens.update(_camel_to_tokens(scenario_text))

        candidates: List[RetrievalCandidate] = []
        for idx, cls in enumerate(self._classes):
            tfidf_score = float(tfidf_scores[idx])
            ast_boost = self._ast_boost(query_tokens, idx)
            emb_score = float(embedding_scores[idx]) if self._embedding_matrix is not None else 0.0

            if self._embedding_matrix is not None:
                lexical_weight = 1.0 - self.embedding_weight
                fused = (
                    lexical_weight * tfidf_score
                    + self.embedding_weight * emb_score
                    + self.ast_boost_weight * ast_boost
                )
            else:
                fused = (1.0 - self.ast_boost_weight) * tfidf_score + self.ast_boost_weight * ast_boost

            fused = max(0.0, min(1.0, fused))
            matched = sorted(query_tokens & self._class_tokens[idx])

            candidates.append(
                RetrievalCandidate(
                    class_metadata=cls,
                    score=fused,
                    tfidf_score=tfidf_score,
                    ast_boost=ast_boost,
                    embedding_score=emb_score,
                    matched_tokens=matched,
                )
            )

        candidates.sort(key=lambda c: c.score, reverse=True)
        filtered = [c for c in candidates if c.score >= min_score][:top_k]

        best = filtered[0] if filtered else None
        return RetrievalResult(query=scenario_text, best_candidate=best, candidates=filtered)

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #

    @property
    def indexed_class_count(self) -> int:
        return len(self._classes)

    def is_ready(self) -> bool:
        return self._vectorizer is not None and self._tfidf_matrix is not None


def cosine_similarity_manual(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Similarité cosinus manuelle (utilitaire de secours sans scikit-learn)."""
    norm_a = math.sqrt(float(np.dot(vec_a, vec_a)))
    norm_b = math.sqrt(float(np.dot(vec_b, vec_b)))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b)) / (norm_a * norm_b)