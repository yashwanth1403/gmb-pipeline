"""
llm/openai_client.py
Calls OpenAI chat completions with disk-based caching to avoid re-billing on re-runs.
"""
import hashlib
import json
import os
from pathlib import Path

CACHE_DIR  = Path(__file__).parent.parent / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "llm_responses.json"


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def _cache_key(lead: dict) -> str:
    # Include PROMPT_VERSION so any change to the LLM prompt invalidates the
    # whole cache. This is important when we add new fields (e.g. business_name)
    # that the previous cached responses don't have.
    from llm.prompt_builder import PROMPT_VERSION
    b = lead.get("business", {})
    payload = json.dumps(
        {"prompt_version": PROMPT_VERSION, "place_id": lead.get("place_id"), "business": b},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_content(
    lead: dict,
    model: str = "gpt-4o-mini",
    use_cache: bool = True,
) -> dict:
    """
    Returns the parsed LLM response dict.
    Caches by (place_id + business_data_hash) — re-runs never re-bill.
    """
    from llm.prompt_builder import build_messages

    key   = _cache_key(lead)
    cache = _load_cache()

    if use_cache and key in cache:
        print("  (using cached LLM response)")
        return cache[key]

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not set. Copy .env.example → .env and add your key."
        )

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Run: pip install openai")

    client   = OpenAI(api_key=api_key)
    messages = build_messages(lead)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=1500,
        temperature=0.7,
    )

    raw_text = response.choices[0].message.content.strip()
    parsed   = json.loads(raw_text)

    cache[key] = parsed
    _save_cache(cache)
    return parsed
