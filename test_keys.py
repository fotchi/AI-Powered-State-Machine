"""
Test all API keys configured in .env — run this before main.py to catch
key/quota/permission problems early, without burning pipeline quota.

Usage: python test_all_keys.py
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _load_multi(multi_var: str, single_var: str) -> list[str]:
    multi = os.environ.get(multi_var)
    if multi:
        keys = [k.strip() for k in multi.split(",") if k.strip()]
        if keys:
            return keys
    single = os.environ.get(single_var)
    return [single] if single else []


def test_groq_keys():
    print("\n=== GROQ (Actor & Critic) ===")
    from langchain_groq import ChatGroq

    keys = _load_multi("GROQ_API_KEYS", "GROQ_API_KEY")
    if not keys:
        print("  Aucune clé Groq trouvée (GROQ_API_KEYS ou GROQ_API_KEY manquant).")
        return

    actor_model = os.environ.get("GROQ_ACTOR_MODEL", "qwen/qwen3.6-27b")
    critic_model = os.environ.get("GROQ_CRITIC_MODEL", "openai/gpt-oss-120b")

    print(f"--> Test Actor Model ({actor_model}):")
    for i, key in enumerate(keys):
        label = f"Clé {i+1}/{len(keys)}"
        try:
            llm = ChatGroq(model=actor_model, api_key=key, temperature=0, timeout=20)
            response = llm.invoke("Reply with exactly: OK")
            print(f"  {label}: OK -> {response.content.strip()[:40]}")
        except Exception as e:
            print(f"  {label}: ECHEC -> {str(e)[:150]}")

    print(f"\n--> Test Critic Model ({critic_model}):")
    for i, key in enumerate(keys):
        label = f"Clé {i+1}/{len(keys)}"
        try:
            llm = ChatGroq(model=critic_model, api_key=key, temperature=0, timeout=20)
            response = llm.invoke("Reply with exactly: OK")
            print(f"  {label}: OK -> {response.content.strip()[:40]}")
        except Exception as e:
            print(f"  {label}: ECHEC -> {str(e)[:150]}")


def test_gemini_keys():
    print("\n=== GEMINI (Integrator / Clés en Rotation) ===")
    from langchain_google_genai import ChatGoogleGenerativeAI

    keys = _load_multi("GOOGLE_API_KEYS_INTEGRATOR", "GOOGLE_API_KEY_INTEGRATOR")
    if not keys:
        keys = _load_multi("GOOGLE_API_KEY", "GOOGLE_API_KEY")  # Shared fallback
    if not keys:
        print("  Aucune clé Gemini trouvée (GOOGLE_API_KEYS_INTEGRATOR ou GOOGLE_API_KEY manquant).")
        return

    model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
    for i, key in enumerate(keys):
        label = f"Clé {i+1}/{len(keys)}"
        try:
            llm = ChatGoogleGenerativeAI(model=model, google_api_key=key, temperature=0, timeout=20)
            response = llm.invoke("Reply with exactly: OK")
            content = response.content
            if isinstance(content, list):
                content = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
            print(f"  {label}: OK -> {content.strip()[:40]}")
        except Exception as e:
            print(f"  {label}: ECHEC -> {str(e)[:150]}")


def test_github_token():
    print("\n=== GITHUB (Doc Refresh & Metadata) ===")
    import requests

    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()["resources"]["core"]
        auth_status = "avec token" if token else "SANS token (limite basse: 60/h)"
        print(f"  OK ({auth_status}) -> {data['remaining']}/{data['limit']} requêtes restantes")
    except Exception as e:
        print(f"  ECHEC -> {str(e)[:150]}")


if __name__ == "__main__":
    print("🔍 Test de toutes les clés API configurées dans .env")
    test_groq_keys()
    test_gemini_keys()
    test_github_token()
    print("\n✅ Terminé.")