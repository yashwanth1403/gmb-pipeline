"""
env_loader.py — minimal .env loader so we don't need python-dotenv.
Reads KEY=VALUE lines from .env (if present) and sets os.environ.

Rules:
  - Lines starting with '#' or empty lines are ignored.
  - Existing os.environ values WIN over .env values (so OS envs / runtime overrides take precedence).
  - Re-imports are idempotent (we don't keep re-overwriting).
  - A blank value (KEY=) sets the env var to empty string "" (not "None").
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"

def load_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            # KEY= (blank value) is meaningful — stores empty string, which lets us
            # distinguish "user explicitly cleared this" from "not in .env at all".
            os.environ[key] = value

# Auto-load on import so every agent gets it for free
load_env()