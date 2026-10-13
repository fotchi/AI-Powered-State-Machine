import json
import re
import json_repair

from phase1.schemas.scenario_schema import Scenario, validate_scenario, ScenarioValidationError
from phase1.knowledge_base.domain_rules import get_rules_for
from phase1.retriever.doc_retriever import get_relevant_chunks

GENERATOR_PROMPT_TEMPLATE = """You are a senior test engineer writing test scenarios for the
FLYNC automotive network configuration model. You focus ONLY on the submodel "{submodel}".

Submodel focus areas:
{focus}

Relevant documentation excerpts:
{doc_context}

QUALITY BAR:
{{
  "id": "SC-SIGNAL-001",
  "submodel": "flync_4_signal",
  "type": "Positive",
  "title": "Valid UINT16 Signal with Matching Bit Length",
  "description": "A Signal is configured with data_type UINT16 and bit_length 16, which equals the natural bit width of UINT16, with a linear scaling factor of 0.1 and unit 'km/h'.",
  "injected_fault": null,
  "expected_result": "Validation succeeds; the Signal's bit_length matches the natural bit width of its declared data_type and the linear conversion parameters are accepted."
}}

TASK: Generate exactly {n_scenarios} Positive test scenarios ONLY for "{submodel}":
- ONLY "Positive" type
- Each scenario must target a DIFFERENT class/field
- Every "description" must reference specific values
- "injected_fault" must always be null

Return ONLY a JSON array matching this shape:
[
  {{
    "id": "SC-{submodel_upper}-001",
    "submodel": "{submodel}",
    "type": "Positive",
    "title": "string",
    "description": "string",
    "injected_fault": null,
    "expected_result": "string"
  }}
]
"""

CRITIC_PROMPT_TEMPLATE = """You are a strict technical auditor AND mutation-test designer
reviewing draft Positive test scenarios for the FLYNC submodel "{submodel}".

Documentation excerpts:
{doc_context}

Domain rules:
- Networking: {networking_rules}
- Automotive: {automotive_rules}
- Fault patterns available for mutation: {fault_patterns}

Draft Positive scenarios to process:
{draft_json}

STEP A -- Audit the Positive scenario (Fix errors or drop invalid ones).
STEP B -- Mutate into a paired Negative scenario (Inject one concrete fault).

Return ONLY the combined JSON array of Positive and paired Negative scenarios.
"""

MAX_DOC_CONTEXT_CHARS = 6000

def _truncate(text: str, max_chars: int = MAX_DOC_CONTEXT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated ...]"


class ModuleAgent:
    def __init__(self, submodel_name: str, focus: str, llm_router):
        self.submodel_name = submodel_name
        self.focus = focus
        self.llm_router = llm_router

    def _build_generator_prompt(self, n_scenarios: int, custom_requirement: str | None = None) -> str:
        doc_context = _truncate(get_relevant_chunks(self.submodel_name))
        prompt = GENERATOR_PROMPT_TEMPLATE.format(
            submodel=self.submodel_name,
            submodel_upper=self.submodel_name.replace("flync_4_", "").upper(),
            focus=self.focus,
            doc_context=doc_context,
            n_scenarios=n_scenarios,
        )
        if custom_requirement:
            prompt += (
                "\n\nUSER-SUBMITTED REQUIREMENT (prioritize this over generic coverage -- "
                "at least one generated scenario MUST directly address it):\n"
                f"{custom_requirement}\n"
            )
        return prompt

    def _build_critic_prompt(self, draft_raw: str) -> str:
        doc_context = _truncate(get_relevant_chunks(self.submodel_name))
        rules = get_rules_for(self.focus)
        return CRITIC_PROMPT_TEMPLATE.format(
            submodel=self.submodel_name,
            doc_context=doc_context,
            networking_rules=rules["networking"],
            automotive_rules=rules["automotive"],
            fault_patterns=rules["fault_patterns"],
            draft_json=draft_raw,
        )

    def _extract_and_repair_json(self, raw_text: str) -> list[dict]:
        if not raw_text:
            return []
        text = re.sub(r"```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text).strip()
        
        start_arr, end_arr = text.find("["), text.rfind("]")
        if start_arr != -1 and end_arr > start_arr:
            text = text[start_arr : end_arr + 1]

        try:
            parsed = json_repair.loads(text)
            if isinstance(parsed, dict):
                parsed = parsed.get("scenarios", parsed.get("test_cases", [parsed]))
            if isinstance(parsed, list):
                return [item for item in parsed if isinstance(item, dict)]
            return []
        except Exception as e:
            print(f"[{self.submodel_name}] JSON Repair Error: {e}")
            return []

    def _parse_and_validate(self, raw_output: str) -> list[Scenario]:
        raw_items = self._extract_and_repair_json(raw_output)
        scenarios = []
        sub_code = self.submodel_name.replace("flync_4_", "").upper()

        for index, item in enumerate(raw_items, start=1):
            # تنظيف المعطيات وتكييفها تماماً مع validate_scenario (بدون حقول زائدة تمنع القبول)
            raw_type = str(item.get("type") or "Positive").capitalize()
            if raw_type not in ["Positive", "Negative"]:
                raw_type = "Positive"

            cleaned_item = {
                "id": str(item.get("id") or f"SC-{sub_code}-{index:03d}"),
                "submodel": str(item.get("submodel") or item.get("module") or self.submodel_name),
                "type": raw_type,
                "title": str(item.get("title") or item.get("name") or "Untitled Scenario"),
                "description": str(item.get("description") or ""),
                "expected_result": str(item.get("expected_result") or item.get("expected") or ""),
            }

            # إضافة injected_fault فقط إذا كان موجوداً كـ string أو None
            fault = item.get("injected_fault")
            if fault is not None:
                cleaned_item["injected_fault"] = str(fault) if fault else None
            else:
                cleaned_item["injected_fault"] = None

            try:
                # استدعاء validate_scenario الخاصة بك والتي ترجع Dataclass Scenario
                scenario_obj = validate_scenario(cleaned_item)
                scenarios.append(scenario_obj)
            except ScenarioValidationError as e:
                print(f"[{self.submodel_name}] Validation Error: {e}")
            except Exception as e:
                print(f"[{self.submodel_name}] Unexpected Error: {e}")

        return scenarios

    def generate_scenarios(
        self,
        n_scenarios: int = 6,
        retries: int = 2,
        custom_requirement: str | None = None,
        scenario_type: str = "both",
    ) -> list[Scenario]:
        """scenario_type: "positive", "negative" or "both" (default) -- filters
        the final result. The Critic pass always runs (it's what produces the
        Negative mutations), filtering happens after."""
        print(f"[{self.submodel_name}] actor start (Positive only)")
        gen_prompt = self._build_generator_prompt(n_scenarios, custom_requirement=custom_requirement)
        draft_raw = None

        for attempt in range(retries + 1):
            raw = self.llm_router.call_generator(gen_prompt)
            if self._extract_and_repair_json(raw):
                draft_raw = raw
                print(f"[{self.submodel_name}] actor done")
                break

        if not draft_raw:
            print(f"[{self.submodel_name}] Generator returned empty JSON")
            return []

        print(f"[{self.submodel_name}] critic start (audit + mutate)")
        critic_prompt = self._build_critic_prompt(draft_raw)

        for attempt in range(retries + 1):
            try:
                raw = self.llm_router.call_critic(critic_prompt)
                scenarios = self._parse_and_validate(raw)
                if scenarios:
                    n_pos = sum(1 for s in scenarios if s.type.value == "Positive")
                    n_neg = sum(1 for s in scenarios if s.type.value == "Negative")
                    print(f"[{self.submodel_name}] critic done -> {len(scenarios)} ({n_pos} Pos, {n_neg} Neg)")
                    return self._filter_by_type(scenarios, scenario_type)
            except Exception as e:
                print(f"[{self.submodel_name}] Critic call failed ({str(e)[:80]}), fallback to draft")
                return self._filter_by_type(self._parse_and_validate(draft_raw), scenario_type)

        return self._filter_by_type(self._parse_and_validate(draft_raw), scenario_type)

    @staticmethod
    def _filter_by_type(scenarios: list[Scenario], scenario_type: str) -> list[Scenario]:
        if scenario_type == "positive":
            return [s for s in scenarios if s.type.value == "Positive"]
        if scenario_type == "negative":
            return [s for s in scenarios if s.type.value == "Negative"]
        return scenarios