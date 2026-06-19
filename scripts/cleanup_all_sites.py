"""Clean up Netlify: delete both ur-car-* test sites, leaving account empty."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa
import os
import json
import pathlib

from agents.site_builder import _run_subprocess

# List all
r = _run_subprocess(["netlify", "sites:list", "--json"], cwd=pathlib.Path("."), timeout=30)
sites = json.loads(r.stdout)
print(f"Found {len(sites)} site(s) to clean up:")
for s in sites:
    print(f"  Deleting {s['name']} ({s['site_id']})...")
    r = _run_subprocess(
        ["netlify", "sites:delete", s["site_id"], "--force"],
        cwd=pathlib.Path("."),
        timeout=30,
    )
    print(f"    {r.stdout.strip()}")
print()
print("--- After cleanup ---")
r = _run_subprocess(["netlify", "sites:list", "--json"], cwd=pathlib.Path("."), timeout=30)
sites = json.loads(r.stdout)
print(f"Sites remaining: {len(sites)}")
