from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from agent_lecteur_analyste import AgentLecteurAnalyste
from kb_pointers import FLYNC_KB
from scenario_verifier import KBIndex, verify_scenario, resolve_submodel_field

EXPECTED_MODULES = {
    "flync_4_app", "flync_4_bus", "flync_4_communication", "flync_4_ecu",
    "flync_4_metadata", "flync_4_nm", "flync_4_safety", "flync_4_security",
    "flync_4_signal", "flync_4_someip", "flync_4_topology", "flync_4_tsn",
}

_TEST_CACHE_DIR = str(Path(tempfile.gettempdir()) / "flync_test_kb_cache")


def setup_module(module):
    shutil.rmtree(_TEST_CACHE_DIR, ignore_errors=True)


@pytest.fixture(scope="module")
def agent() -> AgentLecteurAnalyste:
    return AgentLecteurAnalyste(FLYNC_KB, repo_cache_dir=_TEST_CACHE_DIR)


@pytest.fixture(scope="module")
def full_report(agent: AgentLecteurAnalyste):
    return agent.run()


@pytest.fixture(scope="module")
def kpit_scenarios() -> dict:
    path = Path("kpit_scenarios.json")
    assert path.exists(), "kpit_scenarios.json doit être présent à la racine pour ce test"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def kb_index(agent: AgentLecteurAnalyste, full_report) -> KBIndex:
    index = KBIndex(agent.repo_dir)
    index.build_from_model(agent, full_report)
    index.build_from_sdk()
    return index


@pytest.fixture(scope="module")
def class_lookup(full_report) -> dict:
    lookup = {}
    for module_analysis in full_report.modules.values():
        for class_name, class_info in module_analysis.classes.items():
            lookup.setdefault(class_name, class_info)
    return lookup


class TestPhase1KB:
    def test_all_12_modules_discovered(self, full_report):
        discovered = set(full_report.modules.keys())
        assert discovered == EXPECTED_MODULES, (
            f"Modules découverts différents de l'attendu.\n"
            f"Manquants: {EXPECTED_MODULES - discovered}\n"
            f"En trop: {discovered - EXPECTED_MODULES}"
        )

    def test_no_analysis_errors(self, full_report):
        assert full_report.errors == {}, f"Modules en échec: {full_report.errors}"

    def test_all_modules_have_classes(self, full_report):
        empty = [name for name, m in full_report.modules.items() if m.n_classes == 0]
        assert not empty, f"Module(s) sans aucune classe détectée (suspect): {empty}"

    def test_class_count_non_regression(self, full_report):
        assert full_report.total_classes >= 190, (
            f"Total de classes ({full_report.total_classes}) sous le seuil attendu "
            f"(~205) — possible regression de l'extraction AST."
        )

    def test_ecu_is_the_most_connected_module(self, full_report):
        ecu = full_report.modules["flync_4_ecu"]
        others_class_counts = [
            m.n_classes for name, m in full_report.modules.items() if name != "flync_4_ecu"
        ]
        assert ecu.n_classes > max(others_class_counts), (
            "flync_4_ecu n'est plus le module avec le plus de classes — "
            "vérifier si le dépôt a changé significativement."
        )

    def test_targeted_subset_mode_matches_full_run(self, agent: AgentLecteurAnalyste, full_report):
        subset_report = agent.run(target_modules=["flync_4_someip", "flync_4_safety"])
        assert subset_report.errors == {}
        expected_classes = (
            full_report.modules["flync_4_someip"].n_classes
            + full_report.modules["flync_4_safety"].n_classes
        )
        actual_classes = sum(m.n_classes for m in subset_report.modules.values())
        assert actual_classes == expected_classes


class TestPhase2ScenarioVerification:
    def test_kpit_json_schema(self, kpit_scenarios: dict):
        assert "metadata" in kpit_scenarios
        assert "scenarios" in kpit_scenarios
        assert kpit_scenarios["metadata"]["total_scenarios"] == len(kpit_scenarios["scenarios"])
        for s in kpit_scenarios["scenarios"]:
            for key in ("id", "submodel", "type", "title", "description", "expected_result"):
                assert key in s, f"Scénario {s.get('id', '?')} : champ '{key}' manquant"

    def test_cross_module_submodel_parses(self):
        result = resolve_submodel_field("cross_module (flync_4_signal + flync_4_ecu + flync_4_communication)")
        assert result == ["flync_4_signal", "flync_4_ecu", "flync_4_communication"]

    def test_simple_submodel_parses(self):
        assert resolve_submodel_field("flync_4_bus") == ["flync_4_bus"]

    def test_every_scenario_gets_a_verdict(self, kpit_scenarios, kb_index, class_lookup):
        verdicts = [
            verify_scenario(s, kb_index, class_lookup) for s in kpit_scenarios["scenarios"]
        ]
        assert len(verdicts) == len(kpit_scenarios["scenarios"])
        for v in verdicts:
            assert v.classification in {"MODEL_ONLY", "REQUIRES_SDK", "UNRESOLVED"}

    def test_no_false_positive_from_nested_methods(self, kb_index: KBIndex):
        assert "source" not in kb_index.entities or kb_index.entities["source"].layer != "sdk", (
            "Régression : une méthode interne générique est de nouveau indexée "
            "comme entité SDK de haut niveau."
        )

    @pytest.mark.parametrize("scenario_id,matched_class,expected_validators,gap_keyword_absent", [
        ("SC-SIGNAL-002", "StandardPDU", ["validate_signals_fit_in_pdu"], "frame"),
        ("SC-SOMEIP-002", "SOMEIPServiceConsumer", [], None),
        ("SC-SECURITY-002", "Firewall", ["check_duplicate_rules"], "count"),
    ])
    def test_known_validator_sets_stay_stable(
        self, kpit_scenarios, kb_index, class_lookup,
        scenario_id, matched_class, expected_validators, gap_keyword_absent,
    ):
        scenario = next(s for s in kpit_scenarios["scenarios"] if s["id"] == scenario_id)
        verdict = verify_scenario(scenario, kb_index, class_lookup)

        assert matched_class in verdict.entities_found_in_model, (
            f"{scenario_id}: '{matched_class}' devrait toujours être détecté dans le texte du scénario"
        )
        actual_validators = [
            v for v in verdict.validators_on_matched_classes.get(matched_class, [])
            if v != "(aucun validator)"
        ]
        assert actual_validators == expected_validators, (
            f"{scenario_id}/{matched_class}: validators={actual_validators}, "
            f"attendu={expected_validators} -- le dépôt a peut-être évolué, "
            f"ou l'extraction AST a régressé."
        )
        if gap_keyword_absent:
            assert not any(gap_keyword_absent in v.lower() for v in actual_validators), (
                f"{scenario_id}: un validator contenant '{gap_keyword_absent}' est apparu — "
                f"le gap identifié pourrait être comblé, à vérifier avec KPIT."
            )


def teardown_module(module):
    shutil.rmtree(_TEST_CACHE_DIR, ignore_errors=True)