"""Test fonctionnel de bout en bout, sans appel LLM réel (mode template + mock)."""
import os
import sys
import logging
from pathlib import Path

# Injection dynamique de 'src' et de la racine dans le chemin Python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO)

try:
    from flync_pipeline.agent_maitre import FlyncMasterAgent, DispatchMode, ModeDispatchHeuristic, DEFAULT_TEMPLATES
    from flync_pipeline.orchestrateur_langgraph import AnthropicDeveloperClient, LLMGenerationResult
except ModuleNotFoundError:
    from src.flync_pipeline.agent_maitre import FlyncMasterAgent, DispatchMode, ModeDispatchHeuristic, DEFAULT_TEMPLATES
    from src.flync_pipeline.orchestrateur_langgraph import AnthropicDeveloperClient, LLMGenerationResult


class MockDeveloperClient(AnthropicDeveloperClient):
    """Client LLM mocké pour le test (aucun appel réseau réel)."""

    def generate_code(self, scenario_text, target_class_context, previous_code, error_feedback):
        code = (
            "print('Scénario exécuté avec succès')\n"
            f"print({scenario_text!r})\n"
        )
        return LLMGenerationResult(code=code, raw_response=code)


FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_fixture")


def main():
    agent = FlyncMasterAgent(
        search_paths=[FIXTURE_DIR],
        modules=("app", "bus", "communication", "someip", "topology", "ecu",
                 "metadata", "nm", "security", "signal", "tsn", "safety"),
        max_retries_per_scenario=2,
        developer_client=MockDeveloperClient(),
    )

    scenarios = [
        "Créer une instance de SomeIpService pour le diagnostic moteur",
        "Configurer un calculateur ecu id principal",
        "Application principale du véhicule",
        "Un scénario totalement hors sujet sans rapport",
    ]

    report = agent.run(scenarios)
    print(report.summary())
    print()
    for outcome in report.outcomes:
        print(f"- {outcome.scenario_id}: classe={outcome.resolved_class_name} "
              f"confiance={outcome.confidence} mode={outcome.dispatch_mode} "
              f"status={outcome.status}")

    assert report.total_modules_analyzed == 12
    assert report.total_classes_indexed >= 4
    print("\nTEST OK")


if __name__ == "__main__":
    main()