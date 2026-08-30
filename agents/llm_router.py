import os
import re
import time
import threading

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

GROQ_GENERATOR_MODEL = os.environ.get("GROQ_GENERATOR_MODEL", "qwen/qwen3.6-27b")
GROQ_CRITIC_MODEL = os.environ.get("GROQ_CRITIC_MODEL", "openai/gpt-oss-120b")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(minimum, value)


def _env_float(name: str, default: float, minimum: float = 0.0) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return max(minimum, value)


LLM_RETRY_MAX_RETRIES = _env_int("LLM_RETRY_MAX_RETRIES", 3, minimum=1)
LLM_RETRY_BASE_DELAY_SECONDS = _env_float("LLM_RETRY_BASE_DELAY_SECONDS", 8.0, minimum=0.0)
CRITIC_MAX_PARALLEL_REQUESTS = _env_int("CRITIC_MAX_PARALLEL_REQUESTS", 1, minimum=1)
CRITIC_MIN_INTERVAL_SECONDS = _env_float("CRITIC_MIN_INTERVAL_SECONDS", 15.0, minimum=0.0)


def _load_multi_keys(multi_env_var: str, single_env_var: str, label: str) -> list[str]:
    multi = os.environ.get(multi_env_var)
    if multi:
        keys = [k.strip() for k in multi.split(",") if k.strip()]
        if keys:
            return keys
    single = os.environ.get(single_env_var)
    if single:
        return [single]
    raise RuntimeError(
        f"No {label} key found. Set {multi_env_var} (comma-separated) or {single_env_var} in your .env file."
    )


def _call_with_retry(
    invoke_fn,
    max_retries: int = LLM_RETRY_MAX_RETRIES,
    base_delay: float = LLM_RETRY_BASE_DELAY_SECONDS,
):
    """Retries on rate-limit AND transient server-overload errors, with
    increasing backoff."""
    RETRYABLE_MARKERS = ("rate", "429", "quota", "503", "unavailable", "overloaded", "high demand", "resource_exhausted")
    last_error = None
    for attempt in range(max_retries):
        try:
            return invoke_fn()
        except Exception as e:
            last_error = e
            msg = str(e).lower()
            if any(marker in msg for marker in RETRYABLE_MARKERS):
                delay = base_delay * (attempt + 1)
                print(f"[llm_router] Transient error, retrying in {delay:.0f}s (attempt {attempt+1}/{max_retries}): {msg[:100]}")
                time.sleep(delay)
                continue
            raise
    raise RuntimeError(f"Gave up after {max_retries} retries. Last error: {last_error}")


class LLMRouter:
    def __init__(self):
        groq_keys = _load_multi_keys("GROQ_API_KEYS", "GROQ_API_KEY", "Groq")
        gemini_keys = _load_multi_keys("GOOGLE_API_KEYS_INTEGRATOR", "GOOGLE_API_KEY_INTEGRATOR", "Gemini integrator")

        # --- Generator (Actor): Desactivation du raisonnement pour Qwen ---
        self._generator_llms = [
            ChatGroq(
                model=GROQ_GENERATOR_MODEL,
                api_key=key,
                temperature=0.4,
                reasoning_effort="none"
            )
            for key in groq_keys
        ]
        self._generator_index = 0
        self._generator_lock = threading.Lock()

        # --- Critic (Reviewer): Masquage des blocs de pensée pour GPT-OSS ---
        self._critic_llms = [
            ChatGroq(
                model=GROQ_CRITIC_MODEL,
                api_key=key,
                temperature=0.2,
                reasoning_format="hidden"  # Passage direct de l'argument
            )
            for key in groq_keys
        ]
        self._critic_index = 0
        self._critic_lock = threading.Lock()
        
        self._critic_semaphore = threading.BoundedSemaphore(CRITIC_MAX_PARALLEL_REQUESTS)
        self._critic_pace_lock = threading.Lock()
        self._critic_last_call_time = 0.0

        # --- Integrator: Gemini round-robin ---
        self._integrator_llms = [
            ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=key, temperature=0.4)
            for key in gemini_keys
        ]
        self._integrator_index = 0
        self._integrator_lock = threading.Lock()

    def _next_generator_llm(self) -> ChatGroq:
        with self._generator_lock:
            llm = self._generator_llms[self._generator_index % len(self._generator_llms)]
            self._generator_index += 1
        return llm

    def _next_critic_llm(self) -> ChatGroq:
        with self._critic_lock:
            llm = self._critic_llms[self._critic_index % len(self._critic_llms)]
            self._critic_index += 1
            return llm

    def _next_integrator_llm(self) -> ChatGoogleGenerativeAI:
        with self._integrator_lock:
            llm = self._integrator_llms[self._integrator_index % len(self._integrator_llms)]
            self._integrator_index += 1
        return llm

    def _wait_for_critic_pacing(self) -> None:
        with self._critic_pace_lock:
            elapsed = time.monotonic() - self._critic_last_call_time
            wait = CRITIC_MIN_INTERVAL_SECONDS - elapsed
            if wait > 0:
                print(f"[llm_router] Pacing critic call, waiting {wait:.0f}s...")
                time.sleep(wait)
            self._critic_last_call_time = time.monotonic()

    def _normalize_content(self, content) -> str:
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict) and "text" in block:
                    parts.append(block["text"])
            text = "".join(parts)
        else:
            text = str(content)

        # 1. Supprime d'éventuelles balises <think> restantes
        text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()

        # 2. Extrait le contenu des blocs Markdown ```json ... ```
        markdown_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if markdown_match:
            return markdown_match.group(1).strip()

        # 3. Extraction du premier objet ({...}) ou tableau ([...]) JSON
        start_obj, end_obj = text.find("{"), text.rfind("}")
        start_arr, end_arr = text.find("["), text.rfind("]")

        if start_obj != -1 and end_obj > start_obj:
            if start_arr == -1 or start_obj < start_arr:
                return text[start_obj : end_obj + 1].strip()

        if start_arr != -1 and end_arr > start_arr:
            return text[start_arr : end_arr + 1].strip()

        return text.strip()

    def call_generator(self, prompt: str) -> str:
        llm = self._next_generator_llm()
        content = _call_with_retry(lambda: llm.invoke(prompt).content)
        return self._normalize_content(content)

    def call_critic(self, prompt: str) -> str:
        llm = self._next_critic_llm()
        with self._critic_semaphore:
            self._wait_for_critic_pacing()
            content = _call_with_retry(lambda: llm.invoke(prompt).content)
        return self._normalize_content(content)

    def call_integrator(self, prompt: str) -> str:
        llm = self._next_integrator_llm()
        content = _call_with_retry(lambda: llm.invoke(prompt).content, max_retries=2)
        return self._normalize_content(content)