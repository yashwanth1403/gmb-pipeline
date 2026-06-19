"""List all Netlify sites in the account.

Reads NETLIFY_AUTH_TOKEN via env_loader so the secret never appears in source.
"""
import sys
from pathlib import Path

# Load .env via env_loader (avoids putting the token in this source file)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa: F401 — auto-runs load_env()
import os
import json
import pathlib

from agents.site_builder import _run_subprocess

token = os.environ.get("NETLIFY_AUTH_TOKEN", "")
if not token:
    print("NETLIFY_AUTH_TOKEN not loaded from .env")
    sys.exit(1)
print(f"Token loaded (len={len(token)})\n")

r = _run_subprocess(["netlify", "sites:list", "--json"], cwd=pathlib.Path("."), timeout=30)
if r.returncode != 0:
    print(f"netlify sites:list failed:\n{r.stderr}\n{r.stdout}")
    sys.exit(1)

data = json.loads(r.stdout)
print(f"Found {len(data)} site(s):\n")
for s in data:
    print(f"  name:  {s['name']}")
    print(f"  id:    {s['site_id']}")
    print(f"  url:   {s['url']}")
    print(f"  ssl:   {s['ssl_url']}")
    print()
