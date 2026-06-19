"""Delete test sites and try to claim 'ur-car' cleanly."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa
import os
import json
import pathlib

from agents.site_builder import _run_subprocess

# List all sites
r = _run_subprocess(["netlify", "sites:list", "--json"], cwd=pathlib.Path("."), timeout=30)
sites = json.loads(r.stdout)
print(f"Found {len(sites)} site(s):")
for s in sites:
    print(f"  {s['name']:35s}  id={s['site_id']}")
print()

# Delete test sites and anything that isn't a real car dealer
for s in sites:
    name = s["name"]
    if name.startswith("ur-car-test") or name == "urcars":
        print(f"Deleting {name} ({s['site_id']})...")
        r = _run_subprocess(
            ["netlify", "sites:delete", s["site_id"], "--force"],
            cwd=pathlib.Path("."),
            timeout=30,
        )
        print(f"  {r.stdout.strip()}")
