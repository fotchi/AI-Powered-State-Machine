"""
scenario_verifier.py
=====================

ScenarioVerifier du pipeline FLYNC.

Associe chaque scénario textuel à une classe réelle du référentiel de
connaissance (KnowledgeBase) via une résolution en cascade :

    1. Matching EXACT (regex sur les noms de classes réels, insensible à la
       casse, avec délimitation de mots).
    2. Matching par table d'ALIAS (couvrant les 12 modules FLYNC).
    3. Fallback RAG via ``kb_retriever.HybridKBRetriever`` :
         - RAG_HIGH si score >= rag_high_threshold,
         - RAG_LOW  si score >= rag_low_threshold,
         - UNRESOLVED sinon.

La table d'alias est validée programmatiquement au démarrage par
``validate_alias_map()``, qui vérifie que chaque alias pointe bien vers une
classe existante dans le ``class_lookup`` réel de la KnowledgeBase, et
signale/filtre les noms de classes trop courts (< 4 caractères, ex: "App")
qui produiraient trop de faux positifs en matching regex libre.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from kb_retriever import HybridKBRetriever, RetrievalResult
from module_analyzer import ClassMetadata, KnowledgeBase

logger = logging.getLogger("flync.scenario_verifier")

MIN_SAFE_CLASS_NAME_LENGTH = 4


class ConfidenceLevel(str, Enum):
    """Niveau de confiance de la résolution scénario -> classe."""

    EXACT = "EXACT"
    ALIAS = "ALIAS"
    RAG_HIGH = "RAG_HIGH"
    RAG_LOW = "RAG_LOW"
    UNRESOLVED = "UNRESOLVED"


@dataclass
class ResolutionResult:
    """Résultat de résolution d'un scénario vers une classe réelle."""

    scenario_text: str
    resolved_class: Optional[ClassMetadata]
    confidence: ConfidenceLevel
    matched_via: str = ""
    score: float = 0.0
    alternatives: List[ClassMetadata] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def is_resolved(self) -> bool:
        return self.resolved_class is not None and self.confidence != ConfidenceLevel.UNRESOLVED


# --------------------------------------------------------------------------- #
# Table d'alias couvrant les 12 modules FLYNC
# --------------------------------------------------------------------------- #
#
# Chaque entrée mappe un alias en langage naturel / jargon métier vers le
# nom de classe canonique attendu dans le code réel du module correspondant.
# Cette table est délibérément large : ``validate_alias_map`` filtrera au
# démarrage les entrées qui ne correspondent à aucune classe réellement
# présente dans la KnowledgeBase, sans faire échouer le pipeline.

ALIAS_TABLE: Dict[str, Dict[str, str]] = {
    "app": {
        "application": "App",
        "app principale": "App",
        "conteneur applicatif": "AppContainer",
        "cycle de vie applicatif": "AppLifecycle",
        "configuration app": "AppConfig",
    },
    "bus": {
        "bus can": "CanBus",
        "bus lin": "LinBus",
        "bus de communication": "Bus",
        "trame bus": "BusFrame",
        "controleur de bus": "BusController",
        "reseau bus": "BusNetwork",
    },
    "communication": {
        "canal de communication": "CommunicationChannel",
        "endpoint de communication": "CommunicationEndpoint",
        "matrice de communication": "CommunicationMatrix",
        "session de communication": "CommunicationSession",
        "pile de communication": "CommunicationStack",
    },
    "someip": {
        "service someip": "SomeIpService",
        "methode someip": "SomeIpMethod",
        "evenement someip": "SomeIpEvent",
        "champ someip": "SomeIpField",
        "someip sd": "SomeIpServiceDiscovery",
        "decouverte de service": "SomeIpServiceDiscovery",
        "instance de service someip": "SomeIpServiceInstance",
        "eventgroup someip": "SomeIpEventGroup",
    },
    "topology": {
        "topologie reseau": "NetworkTopology",
        "noeud de topologie": "TopologyNode",
        "lien de topologie": "TopologyLink",
        "segment reseau": "NetworkSegment",
        "cluster topologique": "TopologyCluster",
    },
    "ecu": {
        "calculateur": "Ecu",
        "unite de controle": "Ecu",
        "configuration ecu": "EcuConfig",
        "reseau d ecus": "EcuNetwork",
        "partition ecu": "EcuPartition",
    },
    "metadata": {
        "metadonnee": "Metadata",
        "descripteur de metadonnees": "MetadataDescriptor",
        "schema de metadonnees": "MetadataSchema",
        "version de metadonnees": "MetadataVersion",
    },
    "nm": {
        "gestion de reseau": "NetworkManagement",
        "message nm": "NmMessage",
        "etat nm": "NmState",
        "machine a etats nm": "NmStateMachine",
        "coordinateur nm": "NmCoordinator",
    },
    "security": {
        "cle de securite": "SecurityKey",
        "politique de securite": "SecurityPolicy",
        "certificat": "SecurityCertificate",
        "gestionnaire de cles": "KeyManager",
        "module de chiffrement": "CryptoModule",
        "authentification": "AuthenticationHandler",
    },
    "signal": {
        "signal reseau": "Signal",
        "groupe de signaux": "SignalGroup",
        "definition de signal": "SignalDefinition",
        "mapping de signal": "SignalMapping",
        "unite de signal": "SignalUnit",
    },
    "tsn": {
        "reseau tsn": "TsnNetwork",
        "flux tsn": "TsnStream",
        "planificateur tsn": "TsnScheduler",
        "fenetre temporelle tsn": "TsnTimeWindow",
        "gate tsn": "TsnGateControl",
    },
    "safety": {
        "niveau de securite fonctionnelle": "SafetyLevel",
        "mecanisme de securite": "SafetyMechanism",
        "surveillance de securite": "SafetyMonitor",
        "asil": "AsilLevel",
        "diagnostic de securite": "SafetyDiagnostic",
    },
}


def _normalize(text: str) -> str:
    """Normalise un texte pour comparaison (minuscule, espaces compressés)."""
    text = text.lower().strip()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def validate_alias_map(
    alias_map: Dict[str, Dict[str, str]],
    class_lookup: Dict[str, ClassMetadata],
) -> Dict[str, Dict[str, str]]:
    """
    Valide programmatiquement la table d'alias contre le ``class_lookup``
    réel de la KnowledgeBase.

    Règles appliquées :
      - Un alias dont la classe cible canonique n'existe pas dans
        ``class_lookup`` est retiré et journalisé (avertissement), car il
        référence une classe qui n'a pas été trouvée dans le code source
        analysé.
      - Un nom de classe canonique de longueur < ``MIN_SAFE_CLASS_NAME_LENGTH``
        (ex: "App") est conservé dans la table (l'alias reste valide) mais
        marqué comme "court" : il sera exclu du *matching regex libre* dans
        ``ScenarioVerifier._match_exact`` afin d'éviter les faux positifs
        (le mot "app" apparaissant dans une phrase quelconque ne doit pas
        matcher trivialement la classe ``App``).

    :param alias_map: table d'alias brute (module -> alias -> classe).
    :param class_lookup: dictionnaire nom-de-classe/qualified-name -> ClassMetadata.
    :return: une copie filtrée et validée de la table d'alias.
    """
    validated: Dict[str, Dict[str, str]] = {}
    total_aliases = 0
    dropped_aliases = 0
    short_class_names: List[str] = []

    for module, aliases in alias_map.items():
        validated_module: Dict[str, str] = {}
        for alias, canonical_class in aliases.items():
            total_aliases += 1
            exists = canonical_class in class_lookup or any(
                cls.class_name == canonical_class for cls in class_lookup.values()
            )
            if not exists:
                dropped_aliases += 1
                logger.warning(
                    "Alias invalide ignoré : module='%s' alias='%s' -> classe "
                    "canonique '%s' introuvable dans la KnowledgeBase.",
                    module,
                    alias,
                    canonical_class,
                )
                continue

            if len(canonical_class) < MIN_SAFE_CLASS_NAME_LENGTH:
                short_class_names.append(canonical_class)

            validated_module[_normalize(alias)] = canonical_class

        if validated_module:
            validated[module] = validated_module

    if short_class_names:
        logger.info(
            "Classes canoniques courtes (< %d caractères) détectées, matching "
            "regex libre désactivé pour : %s",
            MIN_SAFE_CLASS_NAME_LENGTH,
            sorted(set(short_class_names)),
        )

    logger.info(
        "Validation de la table d'alias terminée : %d/%d aliases valides "
        "(%d rejetés) sur %d modules.",
        total_aliases - dropped_aliases,
        total_aliases,
        dropped_aliases,
        len(validated),
    )
    return validated


class ScenarioVerifier:
    """
    Résout un scénario textuel vers une classe réelle du code FLYNC en
    appliquant, dans l'ordre, un matching exact, un matching par alias, puis
    un fallback RAG hybride.
    """

    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        retriever: Optional[HybridKBRetriever] = None,
        alias_table: Optional[Dict[str, Dict[str, str]]] = None,
        rag_high_threshold: float = 0.5,
        rag_low_threshold: float = 0.15,
    ) -> None:
        self.kb = knowledge_base
        self.rag_high_threshold = rag_high_threshold
        self.rag_low_threshold = rag_low_threshold

        raw_alias_table = alias_table if alias_table is not None else ALIAS_TABLE
        self.alias_table = validate_alias_map(raw_alias_table, self.kb.class_lookup)

        # Ensemble des classes dont le nom est "sûr" pour un matching regex
        # exact libre (longueur suffisante pour éviter les faux positifs).
        self._safe_exact_classes: Dict[str, ClassMetadata] = {
            cls.class_name: cls
            for cls in self.kb.all_classes()
            if len(cls.class_name) >= MIN_SAFE_CLASS_NAME_LENGTH
        }
        self._exact_pattern = self._build_exact_pattern(self._safe_exact_classes.keys())

        if retriever is not None:
            self.retriever = retriever
        else:
            self.retriever = HybridKBRetriever()
            self.retriever.index_classes(self.kb.all_classes())

    @staticmethod
    def _build_exact_pattern(class_names) -> Optional[re.Pattern]:
        names = sorted({n for n in class_names if n}, key=len, reverse=True)
        if not names:
            return None
        escaped = [re.escape(n) for n in names]
        return re.compile(r"\b(" + "|".join(escaped) + r")\b")

    # ------------------------------------------------------------------ #
    # Étapes de résolution
    # ------------------------------------------------------------------ #

    def _match_exact(self, scenario_text: str) -> Optional[ClassMetadata]:
        """
        Matching EXACT : recherche des noms de classes réels (longueur >= 4)
        présents littéralement dans le texte du scénario, délimités par des
        frontières de mots, en tolérant la casse.
        """
        if self._exact_pattern is None:
            return None
        for name, cls in self._safe_exact_classes.items():
            pattern = re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)
            if pattern.search(scenario_text):
                return cls
        return None

    def _match_alias(self, scenario_text: str) -> Optional[ClassMetadata]:
        """
        Matching par table d'ALIAS : recherche si une expression alias
        connue (normalisée) apparaît comme sous-chaîne du scénario normalisé.
        En cas de correspondances multiples, l'alias le plus long (le plus
        spécifique) l'emporte.
        """
        normalized_scenario = _normalize(scenario_text)
        best_alias: Optional[str] = None
        best_class_name: Optional[str] = None

        for module_aliases in self.alias_table.values():
            for alias, canonical_class in module_aliases.items():
                if alias in normalized_scenario:
                    if best_alias is None or len(alias) > len(best_alias):
                        best_alias = alias
                        best_class_name = canonical_class

        if best_class_name is None:
            return None

        cls = self.kb.class_lookup.get(best_class_name)
        if cls is None:
            for candidate in self.kb.all_classes():
                if candidate.class_name == best_class_name:
                    cls = candidate
                    break
        return cls

    def _fallback_rag(self, scenario_text: str) -> RetrievalResult:
        return self.retriever.retrieve_relevant_classes(
            scenario_text, top_k=5, min_score=self.rag_low_threshold
        )

    # ------------------------------------------------------------------ #
    # API publique
    # ------------------------------------------------------------------ #

    def resolve(self, scenario_text: str) -> ResolutionResult:
        """
        Résout un scénario textuel vers une classe réelle en suivant la
        cascade EXACT -> ALIAS -> RAG (HIGH/LOW) -> UNRESOLVED.

        :param scenario_text: description en langage naturel du scénario.
        :return: un :class:`ResolutionResult` détaillant la classe résolue,
            le niveau de confiance et la méthode ayant produit le match.
        """
        if not scenario_text or not scenario_text.strip():
            return ResolutionResult(
                scenario_text=scenario_text,
                resolved_class=None,
                confidence=ConfidenceLevel.UNRESOLVED,
                notes=["Scénario vide."],
            )

        exact_match = self._match_exact(scenario_text)
        if exact_match is not None:
            return ResolutionResult(
                scenario_text=scenario_text,
                resolved_class=exact_match,
                confidence=ConfidenceLevel.EXACT,
                matched_via=f"regex_exact:{exact_match.class_name}",
                score=1.0,
            )

        alias_match = self._match_alias(scenario_text)
        if alias_match is not None:
            return ResolutionResult(
                scenario_text=scenario_text,
                resolved_class=alias_match,
                confidence=ConfidenceLevel.ALIAS,
                matched_via=f"alias_table:{alias_match.class_name}",
                score=0.9,
            )

        rag_result = self._fallback_rag(scenario_text)
        if rag_result.best_candidate is None:
            return ResolutionResult(
                scenario_text=scenario_text,
                resolved_class=None,
                confidence=ConfidenceLevel.UNRESOLVED,
                matched_via="rag_fallback",
                score=0.0,
                notes=["Aucun candidat RAG au-dessus du seuil minimal."],
            )

        best = rag_result.best_candidate
        confidence = (
            ConfidenceLevel.RAG_HIGH
            if best.score >= self.rag_high_threshold
            else ConfidenceLevel.RAG_LOW
        )
        alternatives = [c.class_metadata for c in rag_result.candidates[1:]]

        return ResolutionResult(
            scenario_text=scenario_text,
            resolved_class=best.class_metadata,
            confidence=confidence,
            matched_via="rag_fallback",
            score=best.score,
            alternatives=alternatives,
            notes=[f"matched_tokens={best.matched_tokens}"] if best.matched_tokens else [],
        )

    def resolve_batch(self, scenarios: List[str]) -> List[ResolutionResult]:
        """Résout une liste de scénarios en conservant leur ordre d'origine."""
        return [self.resolve(scenario) for scenario in scenarios]