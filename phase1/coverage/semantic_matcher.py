"""
Second pass de vérification de couverture, au-dessus du matching littéral
de matcher.py -- celui-ci comprend le SENS d'un scénario au lieu de
chercher un seul mot abstrait (ex: "fields") verbatim dans son texte.

Un scénario réel décrit "MDI/MII configuration is present" pour couvrir
la règle "ecu.fields" sans jamais écrire le mot "field" -- le matching
littéral rate systématiquement ce genre de cas (voir matcher.py). Ici, on
donne à un LLM (1 seul appel par machine, pas par cas) la liste des
checkpoints non trouvés par le matching littéral + la liste complète des
scénarios existants, et on lui demande de juger la couverture par le sens.

Best-effort : si l'appel LLM échoue (pas de clé, réseau, réponse
imparsable), retourne None -- l'appelant (matcher.coverage_report) se
rabat alors sur le résultat du matching littéral seul, sans planter.
"""
from __future__ import annotations

import os
import re
from typing import Any, Optional


def _load_groq_keys() -> list[str]:
    multi = os.environ.get("GROQ_API_KEYS")
    if multi:
        keys = [k.strip() for k in multi.split(",") if k.strip()]
        if keys:
            return keys
    single = os.environ.get("GROQ_API_KEY")
    return [single] if single else []


def case_key(case: dict[str, str]) -> str:
    return f"{case['tag']}|{case['expected_outcome']}"


def _describe_case(case: dict[str, str]) -> str:
    obj, field = case["tag"].split(".", 1)
    readable = field.replace("_", " ")
    outcome = case["expected_outcome"]
    if outcome == "PASS":
        return f"the '{readable}' rule for {obj} (pipeline state {case['state']}) is satisfied -- a valid/successful case"
    return (
        f"the '{readable}' rule for {obj} (pipeline state {case['state']}) is violated, "
        f"triggering failure mode {outcome}"
    )


def _build_prompt(machine_id: str, cases: list[dict[str, str]], existing: list[dict[str, Any]]) -> str:
    lines = [
        f"You are verifying test coverage for the '{machine_id}' validation pipeline.",
        "",
        "Below are validation checkpoints (a specific rule enforced at one step of the pipeline). "
        "For each, decide whether ANY of the scenarios listed further below already tests that exact "
        "checkpoint and outcome. Judge by MEANING, not literal keyword overlap -- e.g. a scenario "
        "describing 'MDI/MII configuration is present' DOES satisfy a checkpoint about required-field "
        "validation, even though it never uses the word 'field'.",
        "",
        "Checkpoints:",
    ]
    for i, case in enumerate(cases, 1):
        lines.append(f"{i}. key=\"{case_key(case)}\" -- checks that {_describe_case(case)}.")
    lines.append("")
    lines.append("Existing scenarios:")
    for s in existing:
        text = f"{s.get('title', '')} -- {s.get('description', '')} Expected: {s.get('expected_result', '')}"
        if s.get("injected_fault"):
            text += f" Injected fault: {s['injected_fault']}"
        lines.append(f"- {s.get('id', '?')}: {text}")
    lines.append("")
    lines.append(
        "Return ONLY a JSON object mapping each checkpoint's exact \"key\" string to true "
        "(an existing scenario already covers it) or false (none do). No other text, no markdown fences."
    )
    return "\n".join(lines)


def _extract_json_object(text: str) -> str:
    """Same defensive extraction as llm_router.py's _normalize_content --
    strips markdown code fences and any leading/trailing prose the model
    added despite instructions not to."""
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return text[start:end + 1]
    return text.strip()


def judge_coverage_via_llm(
    machine_id: str, cases: list[dict[str, str]], existing: list[dict[str, Any]],
) -> Optional[dict[str, bool]]:
    """One LLM call covering every case at once. Returns {case_key: bool},
    or None if the call couldn't be made or parsed (caller falls back to
    literal-only matching -- never raises)."""
    if not cases or not existing:
        return {}

    keys = _load_groq_keys()
    if not keys:
        return None

    try:
        from langchain_groq import ChatGroq
        import json_repair
    except ImportError:
        return None

    model = os.environ.get("GROQ_CRITIC_MODEL", "openai/gpt-oss-120b")
    prompt = _build_prompt(machine_id, cases, existing)

    try:
        llm = ChatGroq(model=model, api_key=keys[0], temperature=0, request_timeout=25)
        response = llm.invoke(prompt)
        content = getattr(response, "content", str(response))
        raw = _extract_json_object(content if isinstance(content, str) else str(content))
        verdicts = json_repair.loads(raw)
        if not isinstance(verdicts, dict):
            return None
        return {str(k): bool(v) for k, v in verdicts.items()}
    except Exception as exc:  # noqa: BLE001 -- best-effort, caller falls back
        print(f"[semantic_matcher] LLM coverage check failed ({exc}); falling back to keyword-only matching.")
        return None
