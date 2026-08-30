"""
ollama_developer_client.py
============================

Client LLM alternatif pour le noeud Développeur de la boucle micro
LangGraph (``orchestrateur_langgraph.py``), basé sur un modèle Qwen exécuté
localement via Ollama (ex: ``qwen2.5-coder``), au lieu de l'API Anthropic.

Respecte exactement l'interface attendue par
``ScenarioLangGraphOrchestrator`` : une méthode
``generate_code(scenario_text, target_class_context, previous_code, error_feedback)
-> LLMGenerationResult``. Il est donc directement substituable à
``AnthropicDeveloperClient`` sans modifier ``orchestrateur_langgraph.py``
ni ``agent_maitre.py``.

Utilisation :

    from ollama_developer_client import OllamaDeveloperClient
    from agent_maitre import FlyncMasterAgent

    agent = FlyncMasterAgent(
        search_paths=["./flync_src"],
        developer_client=OllamaDeveloperClient(model="qwen2.5-coder:7b"),
    )
"""

from __future__ import annotations

import logging
import textwrap
from typing import Optional

from flync_pipeline.orchestrateur_langgraph import LLMGenerationResult

logger = logging.getLogger("flync.ollama_developer_client")

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_QWEN_MODEL = "qwen2.5-coder:7b"


class OllamaDeveloperClient:
    """
    Noeud Développeur basé sur un modèle Qwen servi localement par Ollama.

    :param model: tag du modèle Ollama à utiliser (ex: "qwen2.5-coder:7b",
        "qwen2.5-coder:32b", "qwen3:14b"). Doit avoir été préalablement
        récupéré via ``ollama pull <model>``.
    :param base_url: URL du serveur Ollama local.
    :param timeout_seconds: timeout de la requête HTTP vers Ollama.
    :param temperature: température de génération (0.0 = déterministe).
    """

    def __init__(
        self,
        model: str = DEFAULT_QWEN_MODEL,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        timeout_seconds: float = 120.0,
        temperature: float = 0.1,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature
        self._checked_availability = False

    def _ensure_model_available(self) -> None:
        """Vérifie que le serveur Ollama répond et journalise si le modèle
        n'apparaît pas dans la liste locale (ne bloque pas l'appel, car la
        liste peut être incomplète selon la version d'Ollama)."""
        if self._checked_availability:
            return
        try:
            import requests

            resp = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout_seconds)
            resp.raise_for_status()
            tags = [m.get("name", "") for m in resp.json().get("models", [])]
            if tags and not any(self.model in t or t in self.model for t in tags):
                logger.warning(
                    "Le modèle '%s' n'apparaît pas dans 'ollama list' (%s). "
                    "Exécutez 'ollama pull %s' si l'appel échoue.",
                    self.model,
                    tags,
                    self.model,
                )
        except Exception as exc:
            raise RuntimeError(
                f"Impossible de joindre le serveur Ollama sur {self.base_url}. "
                f"Vérifiez qu'Ollama est lancé ('ollama serve'). Détail: {exc}"
            ) from exc
        finally:
            self._checked_availability = True

    @staticmethod
    def _extract_code_block(text: str) -> str:
        """Extrait le contenu du premier bloc de code Python d'une réponse LLM."""
        markers = ["```python", "```py", "```"]
        for marker in markers:
            if marker in text:
                start = text.index(marker) + len(marker)
                end = text.find("```", start)
                if end != -1:
                    return text[start:end].strip()
        return text.strip()

    def generate_code(
        self,
        scenario_text: str,
        target_class_context: str,
        previous_code: Optional[str],
        error_feedback: Optional[str],
    ) -> LLMGenerationResult:
        """
        Génère (ou corrige) le code Python via Qwen/Ollama, avec la même
        sémantique que ``AnthropicDeveloperClient.generate_code``.
        """
        self._ensure_model_available()

        system_prompt = textwrap.dedent(
        """\
        Tu es un développeur Python senior spécialisé dans les systèmes
        embarqués automobiles, AUTOSAR, SOME/IP, CAN, LIN, Ethernet et TSN.

        Ta mission est de générer un SCRIPT PYTHON DE CONSTRUCTION qui réalise
        réellement le scénario demandé à partir des classes réelles fournies
        dans le contexte.

        RÈGLES ABSOLUES :

        1. Utilise uniquement les classes, modules, champs, constructeurs,
        méthodes et relations présents dans le contexte fourni.

        2. NE PAS inventer de classes, méthodes, attributs ou API.

        3. Si le scénario nécessite plusieurs composants, construis-les
        explicitement.

        4. IMPORTANT :
        La simple création de deux objets NE constitue PAS une connexion.

        INCORRECT :
            controller = Controller(...)
            interface = EthernetInterface(...)

        CORRECT :
            controller = Controller(...)
            interface = EthernetInterface(...)
            # puis utiliser l'API réelle de la KB pour relier
            # interface au controller.

        5. Pour chaque relation indiquée dans le contexte de topologie,
        cherche dans les champs, constructeurs ou méthodes fournis
        l'API réelle permettant d'établir cette relation.

        6. Respecte l'ordre des dépendances :
        construire d'abord les composants dont dépendent les autres,
        puis construire les composants parents.

        7. Si un objet doit être passé au constructeur d'un autre objet,
        fais-le réellement.

        8. Si une relation doit être ajoutée via une liste, un dictionnaire,
        une méthode ou une propriété existante, effectue réellement cette
        opération.

        9. Ne simule jamais une connexion avec un commentaire ou un print.

        INCORRECT :
            # controller connected to interface
            print("connected")

        Une connexion doit être matérialisée par une opération Python
        réelle utilisant l'API connue.

        10. Ne remplace pas une relation réelle par une variable fictive.

        11. Le script doit être autonome et exécutable.

        12. Le script doit construire les objets demandés et leurs relations
            réelles.

        13. Ne génère PAS de pytest.
            Ne génère PAS de tests unitaires.
            Ne génère PAS de assert comme mécanisme principal de construction.

        14. À la fin du script, affiche les objets construits afin de rendre
            le résultat observable.

        15. Réponds UNIQUEMENT avec un bloc de code Python.
        """
    )

        user_prompt_parts = [
        f"""
    === SCÉNARIO ===

    {scenario_text}
    """,

        f"""
    === CONTEXTE COMPLET DE LA KB ===

    {target_class_context}
    """,

        """
    === OBJECTIF DE CONSTRUCTION ===

    Produis le script Python qui réalise réellement le scénario.

    Tu dois :

    1. Identifier les composants nécessaires.
    2. Construire les composants dans l'ordre approprié.
    3. Utiliser les classes réelles de la KB.
    4. Utiliser les constructeurs réels.
    5. Utiliser les champs ou méthodes réels.
    6. Établir réellement les relations entre les composants.
    7. Ne pas simplement créer les objets séparément.
    8. Ne pas inventer d'API.
    9. Ne pas remplacer une connexion par un commentaire ou un print.
    10. Retourner un script Python exécutable.

    Avant de générer le code, raisonne implicitement sur :

        dépendances
            ↓
        composants nécessaires
            ↓
        ordre de construction
            ↓
        relations
            ↓
        construction finale

    Le résultat final doit représenter le scénario demandé avec les
    relations réelles disponibles dans la KB.
    """,
    
    ]
        
        if previous_code:
            user_prompt_parts.append(f"\nCode précédemment généré :\n```python\n{previous_code}\n```")
        if error_feedback:
            user_prompt_parts.append(
                f"\nCe code a échoué à l'exécution avec l'erreur suivante, "
                f"corrige-le :\n{error_feedback}"
            )
        user_prompt = "\n".join(user_prompt_parts)

        try:
            import requests
        except ImportError as exc:
            raise RuntimeError(
                "Le package 'requests' est requis par OllamaDeveloperClient. "
                "Installez-le avec: pip install requests"
            ) from exc

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": self.temperature},
        }

        response = requests.post(
            f"{self.base_url}/api/chat", json=payload, timeout=self.timeout_seconds
        )
        response.raise_for_status()
        data = response.json()

        raw_text = data.get("message", {}).get("content", "")
        if not raw_text:
            raise RuntimeError(
                f"Réponse vide reçue d'Ollama pour le modèle '{self.model}'. "
                f"Réponse brute: {data}"
            )

        code = self._extract_code_block(raw_text)
        return LLMGenerationResult(code=code, raw_response=raw_text)