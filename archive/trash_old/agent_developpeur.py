
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from agent_lecteur_analyste import AgentLecteurAnalyste, ClassInfo, FieldInfo
from kb_pointers import FLYNC_KB
from scenario_verifier import KBIndex, resolve_submodel_field, verify_scenario


# ---------------------------------------------------------------------------
# Inference de valeurs placeholder (meme logique que flync_static_agent.py,
# consolidee ici pour rester autonome)
# ---------------------------------------------------------------------------

def infer_placeholder(field_info: FieldInfo, class_name: str) -> tuple[str, Optional[str]]:
    """Retourne (valeur, commentaire_optionnel) -- jamais combines dans la
    meme chaine : un commentaire inline avant la virgule de fin d'argument
    avalerait cette virgule et casserait la syntaxe (bug reel rencontre et
    corrige ici, ex: SC-SOMEIP-001)."""
    t = field_info.type_str.strip()

    if t.startswith("Literal["):
        inner = t[len("Literal["):-1]
        return inner.split(",")[0].strip(), None
    if t.startswith("Optional["):
        return "None", None
    if t.startswith("List[") or t.startswith("list["):
        return "[]", None
    if t == "str":
        return f'"demo_{field_info.name}"', None
    if t == "int":
        return "1", None
    if t == "float":
        return "1.0", None
    if t == "bool":
        return "False", None
    return "None", f"TODO: fournir une instance de type {t} (non résolu automatiquement)"


def resolve_all_fields(class_info: ClassInfo, class_lookup: dict) -> list[FieldInfo]:
    """Fusionne les champs propres a la classe avec ceux herites de ses
    classes de base (recursivement), tant que la base est elle-meme connue
    dans class_lookup (les bases externes type FLYNCBaseModel/BaseModel/
    RootModel s'arretent naturellement la, puisqu'elles ne sont pas des
    classes du modele FLYNC analysees par AST).

    BUG CORRIGE : l'extraction AST d'origine ne capturait que les champs
    declares directement dans le corps de CHAQUE classe (class_node.body),
    jamais ceux herites -- ex: CANFrame(CANFrameBase) qui elle-meme herite
    de Frame(FLYNCBaseModel) perdait le champ 'name' de Frame, rendant les
    scripts generes invalides (name manquant, requis mais absent)."""
    seen_names: set[str] = set()
    all_fields: list[FieldInfo] = []

    def _walk(ci: ClassInfo) -> None:
        for base_name in ci.bases:
            base_info = class_lookup.get(base_name)
            if base_info is not None:
                _walk(base_info)  # les bases d'abord, pour un ordre naturel
        for f in ci.fields:
            if f.name not in seen_names:
                seen_names.add(f.name)
                all_fields.append(f)

    _walk(class_info)
    return all_fields


def build_construction_snippet(class_info: ClassInfo, var_name: str, class_lookup: dict) -> list[str]:
    lines = [f"{var_name} = {class_info.name}("]
    for f in resolve_all_fields(class_info, class_lookup):
        if not f.required:
            continue
        value, comment = infer_placeholder(f, class_info.name)
        if comment:
            lines.append(f"    # {comment}")
        lines.append(f"    {f.name}={value},")
    lines.append(")")
    return lines


# ---------------------------------------------------------------------------
# Génération TEMPLATE (déterministe, sans LLM)
# ---------------------------------------------------------------------------

GAP_KEYWORDS_BY_HINT = {
    "frame": "aucun validator connu ne verifie la coherence Frame <-> PDU",
    "count": "aucun validator connu ne verifie de plafond numerique",
}


def generate_template_script(
    scenario: dict,
    matched_class: Optional[ClassInfo],
    validators: list[str],
    class_lookup: dict,
) -> str:
    scenario_id = scenario["id"]
    scenario_type = scenario["type"]
    func_name = re.sub(r"[^a-z0-9_]", "_", scenario_id.lower())

    header = (
        f'"""\n'
        f"Scénario {scenario_id} ({scenario_type})\n"
        f"{scenario['title']}\n\n"
        f"{scenario['description']}\n"
        f'"""\n'
        f"import pytest\n"
    )

    if matched_class is None:
        return header + (
            f"\n\n@pytest.mark.skip(reason="
            f'"Aucune classe connue trouvée pour ce scénario — analyse manuelle requise.")\n'
            f"def test_{func_name}():\n    pass\n"
        )

    module_name = matched_class.file  # meilleur indice disponible localement
    import_line = f"# from flync.model.<module> import {matched_class.name}  # TODO: ajuster le chemin exact\n"

    # Cas 1 : positif -> construction valide + assertion
    if scenario_type == "Positive":
        constructor_lines = "\n".join(
            "    " + l for l in build_construction_snippet(matched_class, matched_class.name.lower(), class_lookup)
        )
        return (
            header + import_line +
            f"\n\ndef test_{func_name}():\n"
            f"{constructor_lines}\n"
            f"    assert {matched_class.name.lower()} is not None\n"
        )

    # Cas 2 : boundary -> reutilise la construction, laisse un TODO sur la valeur limite
    if scenario_type == "Boundary":
        constructor_lines = "\n".join(
            "    " + l for l in build_construction_snippet(matched_class, matched_class.name.lower(), class_lookup)
        )
        return (
            header + import_line +
            f"\n\ndef test_{func_name}_at_limit():\n"
            f"{constructor_lines}\n"
            f"    # TODO: ajuster les champs ci-dessus à la valeur limite exacte du scénario\n"
            f"    assert {matched_class.name.lower()} is not None\n\n\n"
            f"def test_{func_name}_beyond_limit():\n"
            f"    with pytest.raises(Exception):\n"
            f"        {matched_class.name}(\n"
            f"            # TODO: mêmes champs que ci-dessus, en dépassant la limite\n"
            f"        )\n"
        )

    # Cas 3 : negatif -> verifier d'abord si un gap est connu (Agent Verificateur)
    injected_fault = (scenario.get("injected_fault") or "").lower()
    gap_reason = None
    if not validators:
        gap_reason = f"{matched_class.name} n'a aucun validator connu — impossible de tester '{injected_fault}' honnêtement."
    else:
        for keyword, reason in GAP_KEYWORDS_BY_HINT.items():
            if keyword in injected_fault or keyword in scenario["expected_result"].lower():
                if not any(keyword in v.lower() for v in validators):
                    gap_reason = f"{reason} (validators réels trouvés: {validators})."
                    break

    if gap_reason:
        return header + import_line + (
            f"\n\n@pytest.mark.skip(reason=\"GAP DÉTECTÉ : {gap_reason} "
            f"À clarifier avec KPIT avant de coder ce test.\")\n"
            f"def test_{func_name}():\n    pass\n"
        )

    # Validator plausible trouve -> scaffold a completer manuellement
    constructor_lines = "\n".join(
        "        " + l for l in build_construction_snippet(matched_class, matched_class.name.lower(), class_lookup)
    )
    return (
        header + import_line +
        f"\n\ndef test_{func_name}():\n"
        f"    # Validators réels sur {matched_class.name}: {validators}\n"
        f"    # TODO: modifier un des champs ci-dessous pour déclencher : {injected_fault}\n"
        f"    with pytest.raises(Exception):\n"
        f"{constructor_lines}\n"
    )


# ---------------------------------------------------------------------------
# Génération LLM (optionnelle)
# ---------------------------------------------------------------------------

def get_llm(backend: Optional[str] = None):
    import os

    # Choix explicite via --llm-backend, sinon auto-detection par variables
    # d'environnement disponibles, sinon mock.
    if backend == "ollama" or (backend is None and _ollama_reachable()):
        from langchain_ollama import ChatOllama
        model = os.environ.get("OLLAMA_MODEL", "llama3.1")
        print(f"[agent-dev] Ollama détecté en local -> ChatOllama(model='{model}'). "
              f"Aucune clé API nécessaire, tourne entièrement sur ta machine.")
        return ChatOllama(model=model, temperature=0)

    if os.environ.get("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        print("[agent-dev] ANTHROPIC_API_KEY trouvée -> ChatAnthropic réel.")
        return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        print("[agent-dev] GEMINI_API_KEY trouvée -> ChatGoogleGenerativeAI réel.")
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=key)

    print("[agent-dev] Aucune clé ni Ollama local trouvé -> MOCK LLM (prouve le flux, pas le contenu).")
    from langchain_core.messages import AIMessage
    from langchain_core.runnables import RunnableLambda

    def _mock(prompt_value):
        return AIMessage(content=(
            '{"file_name": "test_mock.py", "content": '
            '"def test_mock():\\n    assert True\\n", "imports_required": [], "covers_targets": []}'
        ))

    return RunnableLambda(_mock)


def _ollama_reachable(host: str = "http://localhost:11434") -> bool:
    """Verifie si un serveur Ollama tourne localement, sans lever d'exception
    si ce n'est pas le cas (ex: dans un sandbox sans Ollama installe)."""
    import urllib.request

    try:
        urllib.request.urlopen(f"{host}/api/tags", timeout=1)
        return True
    except Exception:
        return False


def generate_llm_script(scenario: dict, matched_class: Optional[ClassInfo], validators: list[str], llm) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    class_desc = "aucune classe résolue localement" if matched_class is None else (
        f"{matched_class.name} (fichier {matched_class.file}), champs: "
        f"{[(f.name, f.type_str, f.required) for f in matched_class.fields]}, "
        f"validators réels: {validators}"
    )

    system = (
        "Tu es un ingénieur de test Python écrivant des scripts pytest pour le "
        "framework FLYNC (modèles Pydantic v2). Génère UNIQUEMENT du code Python "
        "valide, sans balises markdown, sans texte hors du code. N'invente "
        "JAMAIS un champ ou un validator qui n'est pas listé ci-dessous. Si la "
        "règle métier décrite ne correspond à aucun validator réel listé, génère "
        "un test marqué @pytest.mark.skip avec la raison exacte plutôt que "
        "d'inventer une assertion qui ne teste rien de réel."
    )
    human = (
        f"Scénario : {scenario['id']} ({scenario['type']})\n"
        f"Titre : {scenario['title']}\n"
        f"Description : {scenario['description']}\n"
        f"Fault injecté : {scenario.get('injected_fault')}\n"
        f"Résultat attendu : {scenario['expected_result']}\n\n"
        f"Classe(s) disponible(s) : {class_desc}"
    )

    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=human)])
    return response.content


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Développeur Python — génère les scripts de test.")
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--mode", choices=["template", "llm"], default="template")
    parser.add_argument("--llm-backend", choices=["ollama", "anthropic", "gemini"], default=None,
                         help="Force un backend LLM précis ; sinon auto-détection (Ollama local > clés API > mock).")
    parser.add_argument("--output-dir", default="./generated_tests")
    args = parser.parse_args()

    scenarios_data = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
    scenarios = scenarios_data["scenarios"]

    print("[agent-dev] Analyse de la KB via l'Agent Lecteur/Analyste ...")
    agent = AgentLecteurAnalyste(FLYNC_KB)
    full_report = agent.run()

    class_lookup: dict = {}
    for module_analysis in full_report.modules.values():
        for class_name, class_info in module_analysis.classes.items():
            class_lookup.setdefault(class_name, class_info)

    kb_index = KBIndex(agent.repo_dir)
    kb_index.build_from_model(agent, full_report)
    kb_index.build_from_sdk()

    llm = get_llm(args.llm_backend) if args.mode == "llm" else None

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    for scenario in scenarios:
        verdict = verify_scenario(scenario, kb_index, class_lookup)
        matched_class = None
        if verdict.entities_found_in_model:
            matched_class = class_lookup.get(verdict.entities_found_in_model[0])
        validators = verdict.validators_on_matched_classes.get(
            verdict.entities_found_in_model[0], []
        ) if verdict.entities_found_in_model else []
        validators = [v for v in validators if v != "(aucun validator)"]

        if verdict.classification == "REQUIRES_SDK":
            content = (
                f'"""Scénario {scenario["id"]} : hors périmètre KB actuel '
                f'(nécessite src/flync/sdk). Voir cahier des charges Phase 1."""\n'
            )
        elif args.mode == "template":
            content = generate_template_script(scenario, matched_class, validators, class_lookup)
        else:
            content = generate_llm_script(scenario, matched_class, validators, llm)

        func_id = re.sub(r"[^a-z0-9_]", "_", scenario["id"].lower())
        out_path = output_dir / f"test_{func_id}.py"
        out_path.write_text(content, encoding="utf-8")
        print(f"[agent-dev] {scenario['id']} ({verdict.classification}) -> {out_path}")

    print(f"\n[agent-dev] Terminé. Scripts dans {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())