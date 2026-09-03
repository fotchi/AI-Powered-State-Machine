"""
orchestrateur_langgraph.py
============================

Boucle micro du pipeline FLYNC : cycle de génération/exécution/évaluation
d'un scénario unique, implémenté comme un ``StateGraph`` LangGraph strict à
3 noeuds :

    Développeur -> Exécuteur -> Évaluateur
                       ^              |
                       |   FAIL & retry < N
                       +--------------+

Routage conditionnel après l'Évaluateur :
    - PASS                    -> fin du scénario (SUCCESS)
    - FAIL et retry < N       -> retour au Développeur avec le feedback d'erreur
    - FAIL et retry >= N      -> fin du scénario (FAILURE)

Le noeud Développeur s'appuie sur l'API Anthropic (SDK officiel `anthropic`)
pour générer/corriger le code Python associé au scénario et à la classe
cible résolue par le ``ScenarioVerifier``. Le noeud Exécuteur exécute ce
code dans un sous-processus isolé (``subprocess``) avec timeout, et capture
stdout/stderr/traceback pour nourrir la boucle de feedback.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

logger = logging.getLogger("flync.orchestrateur_langgraph")

DEFAULT_MAX_RETRIES = 3
DEFAULT_EXECUTION_TIMEOUT_SECONDS = 30


# --------------------------------------------------------------------------- #
# État du graphe
# --------------------------------------------------------------------------- #

class AgentState(TypedDict, total=False):
    """
    État partagé et transmis entre les noeuds du ``StateGraph`` pour un
    scénario unique.
    """

    scenario_id: str
    scenario_text: str
    target_class_name: str
    target_class_context: str
    confidence: str

    generated_code: str
    code_history: List[str]

    execution_stdout: str
    execution_stderr: str
    execution_success: bool
    error_feedback: str

    evaluation_passed: bool
    evaluation_notes: str

    retry_count: int
    max_retries: int
    status: str  # "RUNNING" | "SUCCESS" | "FAILURE"


# --------------------------------------------------------------------------- #
# Client LLM (Développeur)
# --------------------------------------------------------------------------- #

@dataclass
class LLMGenerationResult:
    code: str
    raw_response: str = ""


class AnthropicDeveloperClient:
    """
    Client LLM du noeud Développeur, basé sur l'API Anthropic officielle.

    La clé d'API est lue depuis la variable d'environnement
    ``ANTHROPIC_API_KEY``. Le modèle par défaut est configurable via le
    paramètre ``model``.
    """

    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 4096) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

    def _ensure_client(self):
        if self._client is not None:
            return self._client
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError(
                "Le package 'anthropic' est requis pour le noeud Développeur. "
                "Installez-le avec: pip install anthropic"
            ) from exc

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "La variable d'environnement ANTHROPIC_API_KEY doit être définie "
                "pour utiliser AnthropicDeveloperClient."
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

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
        Génère (ou corrige) le code Python pour un scénario donné, en tenant
        compte du feedback d'erreur d'exécution éventuel de la tentative
        précédente.
        """
        client = self._ensure_client()

        system_prompt = textwrap.dedent(
            """\
            Tu es un développeur Python senior spécialisé dans les systèmes
            embarqués automobiles (AUTOSAR, SOME/IP, réseaux CAN/LIN/TSN).
            Tu génères UNIQUEMENT du code Python exécutable, complet, sans
            aucun texte explicatif hors des commentaires de code. Le code
            doit être autonome (aucune dépendance non standard sauf si
            strictement nécessaire) et doit s'exécuter sans erreur.
            Réponds uniquement avec un unique bloc de code ```python ... ```.
            """
        )

        user_prompt_parts = [
            f"Scénario à implémenter :\n{scenario_text}",
            f"\nContexte de la classe cible réelle du code source :\n{target_class_context}",
        ]
        if previous_code:
            user_prompt_parts.append(f"\nCode précédemment généré :\n```python\n{previous_code}\n```")
        if error_feedback:
            user_prompt_parts.append(
                f"\nCe code a échoué à l'exécution avec l'erreur suivante, "
                f"corrige-le :\n{error_feedback}"
            )
        user_prompt = "\n".join(user_prompt_parts)

        response = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        )
        code = self._extract_code_block(raw_text)
        return LLMGenerationResult(code=code, raw_response=raw_text)


# --------------------------------------------------------------------------- #
# Exécuteur
# --------------------------------------------------------------------------- #

class SubprocessExecutor:
    """
    Exécute un fragment de code Python dans un sous-processus isolé, avec
    timeout, et capture stdout/stderr pour construire le feedback d'erreur
    consommé par le noeud Développeur lors de la prochaine itération.
    """

    def __init__(self, timeout_seconds: int = DEFAULT_EXECUTION_TIMEOUT_SECONDS) -> None:
        self.timeout_seconds = timeout_seconds

    def execute(self, code: str) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name

        try:
            completed = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            return {
                "success": completed.returncode == 0,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "success": False,
                "stdout": exc.stdout or "",
                "stderr": f"Timeout d'exécution dépassé ({self.timeout_seconds}s).",
                "returncode": None,
                "timed_out": True,
            }
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


# --------------------------------------------------------------------------- #
# Évaluateur
# --------------------------------------------------------------------------- #

class SimpleEvaluator:
    """
    Évaluateur du résultat d'exécution : PASS si le code s'est exécuté sans
    erreur (returncode 0, pas de timeout) et sans traceback dans stderr,
    FAIL sinon.
    """

    def evaluate(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        success = bool(execution_result.get("success"))
        stderr = execution_result.get("stderr", "") or ""
        has_traceback = "Traceback (most recent call last)" in stderr

        passed = success and not has_traceback
        notes = "Exécution réussie sans erreur." if passed else "Échec d'exécution détecté."
        if execution_result.get("timed_out"):
            notes = "Timeout d'exécution : le code n'a pas terminé dans le délai imparti."

        return {"passed": passed, "notes": notes}


# --------------------------------------------------------------------------- #
# Noeuds LangGraph
# --------------------------------------------------------------------------- #

class ScenarioLangGraphOrchestrator:
    """
    Construit et exécute le ``StateGraph`` LangGraph à 3 noeuds pour un
    scénario FLYNC unique : Développeur -> Exécuteur -> Évaluateur, avec
    boucle de correction conditionnelle bornée par ``max_retries``.
    """

    def __init__(
        self,
        developer_client: Optional[AnthropicDeveloperClient] = None,
        executor: Optional[SubprocessExecutor] = None,
        evaluator: Optional[SimpleEvaluator] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self.developer_client = developer_client or AnthropicDeveloperClient()
        self.executor = executor or SubprocessExecutor()
        self.evaluator = evaluator or SimpleEvaluator()
        self.max_retries = max_retries
        self._compiled_graph = self._build_graph()

    # ------------------------------------------------------------------ #
    # Définition des noeuds
    # ------------------------------------------------------------------ #

    def developpeur_node(self, state: AgentState) -> AgentState:
        """
        Noeud Développeur : génère (première tentative) ou corrige (retry)
        le code Python associé au scénario, en s'appuyant sur le feedback
        d'erreur d'exécution de la tentative précédente le cas échéant.
        """
        logger.info(
            "[%s] Noeud Développeur (tentative %d/%d)",
            state.get("scenario_id", "?"),
            state.get("retry_count", 0) + 1,
            state.get("max_retries", self.max_retries),
        )

        previous_code = state.get("generated_code") or None
        error_feedback = state.get("error_feedback") or None

        generation = self.developer_client.generate_code(
            scenario_text=state["scenario_text"],
            target_class_context=state.get("target_class_context", ""),
            previous_code=previous_code,
            error_feedback=error_feedback,
        )

        history = list(state.get("code_history", []))
        history.append(generation.code)

        new_state: AgentState = dict(state)  # type: ignore[assignment]
        new_state["generated_code"] = generation.code
        new_state["code_history"] = history
        new_state["status"] = "RUNNING"
        return new_state

    def executeur_node(self, state: AgentState) -> AgentState:
        """
        Noeud Exécuteur : exécute le code généré dans un sous-processus
        isolé et capture stdout/stderr pour l'étape d'évaluation.
        """
        logger.info("[%s] Noeud Exécuteur", state.get("scenario_id", "?"))

        result = self.executor.execute(state.get("generated_code", ""))

        new_state: AgentState = dict(state)  # type: ignore[assignment]
        new_state["execution_stdout"] = result["stdout"]
        new_state["execution_stderr"] = result["stderr"]
        new_state["execution_success"] = result["success"]
        if not result["success"]:
            new_state["error_feedback"] = result["stderr"] or "Erreur d'exécution inconnue."
        else:
            new_state["error_feedback"] = ""
        return new_state

    def evaluateur_node(self, state: AgentState) -> AgentState:
        """
        Noeud Évaluateur : détermine si l'exécution constitue un PASS ou un
        FAIL, et incrémente le compteur de tentatives.
        """
        logger.info("[%s] Noeud Évaluateur", state.get("scenario_id", "?"))

        execution_result = {
            "success": state.get("execution_success", False),
            "stdout": state.get("execution_stdout", ""),
            "stderr": state.get("execution_stderr", ""),
            "timed_out": "Timeout d'exécution dépassé" in (state.get("execution_stderr") or ""),
        }
        evaluation = self.evaluator.evaluate(execution_result)

        new_state: AgentState = dict(state)  # type: ignore[assignment]
        new_state["evaluation_passed"] = evaluation["passed"]
        new_state["evaluation_notes"] = evaluation["notes"]
        new_state["retry_count"] = state.get("retry_count", 0) + (
            0 if evaluation["passed"] else 1
        )

        if evaluation["passed"]:
            new_state["status"] = "SUCCESS"
        elif new_state["retry_count"] >= state.get("max_retries", self.max_retries):
            new_state["status"] = "FAILURE"
        else:
            new_state["status"] = "RUNNING"

        return new_state

    # ------------------------------------------------------------------ #
    # Routage conditionnel
    # ------------------------------------------------------------------ #

    def _route_apres_evaluation(self, state: AgentState) -> str:
        """
        Fonction de routage conditionnel appelée après le noeud Évaluateur.

        Retourne :
            - "success" si PASS,
            - "retry" si FAIL et retry_count < max_retries,
            - "failure" si FAIL et retry_count >= max_retries.
        """
        if state.get("evaluation_passed"):
            return "success"

        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", self.max_retries)
        if retry_count < max_retries:
            return "retry"
        return "failure"

    # ------------------------------------------------------------------ #
    # Construction du graphe
    # ------------------------------------------------------------------ #

    def _build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("developpeur", self.developpeur_node)
        graph.add_node("executeur", self.executeur_node)
        graph.add_node("evaluateur", self.evaluateur_node)

        graph.set_entry_point("developpeur")
        graph.add_edge("developpeur", "executeur")
        graph.add_edge("executeur", "evaluateur")

        graph.add_conditional_edges(
            "evaluateur",
            self._route_apres_evaluation,
            {
                "success": END,
                "retry": "developpeur",
                "failure": END,
            },
        )

        return graph.compile()

    # ------------------------------------------------------------------ #
    # Exécution d'un scénario
    # ------------------------------------------------------------------ #

    def run_scenario(
        self,
        scenario_id: str,
        scenario_text: str,
        target_class_name: str,
        target_class_context: str,
        confidence: str,
        max_retries: Optional[int] = None,
    ) -> AgentState:
        """
        Exécute la boucle LangGraph complète pour un scénario unique et
        retourne l'état final (SUCCESS ou FAILURE) avec l'historique complet
        des tentatives de code générées.
        """
        initial_state: AgentState = {
            "scenario_id": scenario_id,
            "scenario_text": scenario_text,
            "target_class_name": target_class_name,
            "target_class_context": target_class_context,
            "confidence": confidence,
            "generated_code": "",
            "code_history": [],
            "execution_stdout": "",
            "execution_stderr": "",
            "execution_success": False,
            "error_feedback": "",
            "evaluation_passed": False,
            "evaluation_notes": "",
            "retry_count": 0,
            "max_retries": max_retries if max_retries is not None else self.max_retries,
            "status": "RUNNING",
        }

        # La limite de récursion de LangGraph doit couvrir
        # 3 noeuds * (max_retries + 1) itérations, avec une marge.
        recursion_limit = 3 * (initial_state["max_retries"] + 1) + 5
        final_state = self._compiled_graph.invoke(
            initial_state, config={"recursion_limit": recursion_limit}
        )
        return final_state  # type: ignore[return-value]