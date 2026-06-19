"""Delete the old random-named Netlify site so the new ur-car site can claim the clean name."""
from pathlib import Path
import os
import sys

# Load token from .env
token = None
for line in Path(".env").read_text(encoding="utf-8").splitlines():
    if line.startswith("NETLIFY_AUTH_TOKEN="):
        token = line.split("=", 1)[1].strip()
        break
if not token:
    print("NETLIFY_AUTH_TOKEN not found in .env")
    sys.exit(1)

os.environ["NETLIFY_AUTH_TOKEN"] = token
print(f"Token loaded (len={len(token)})")

# Use the same _run_subprocess helper that handles Windows PATH
sys.path.insert(0, str(Path.cwd()))
from agents.site_builder import _run_subprocess
import pathlib

# Delete old site
print("\n--- Deleting old site 89bb9a36-43fd-44aa-b065-b137691c03e3 ---")
r = _run_subprocess(
    ["netlify", "sites:delete", "89bb9a36-43fd-44aa-b065-b137691c03e3", "--force"],
    cwd=pathlib.Path("."),
    timeout=30,
)
print(f"returncode: {r.returncode}")
print(f"stdout: {r.stdout[-800:]}")
print(f"stderr: {r.stderr[-800:]}")

# List remaining sites
print("\n--- Remaining sites ---")
r = _run_subprocess(
    ["netlify", "sites:list", "--json"],
    cwd=pathlib.Path("."),
    timeout=30,
)
print(f"returncode: {r.returncode}")
# Parse out site names
import re
names = re.findall(r'"name"\s*:\s*"([^"]+)"', r.stdout)
print(f"Site names: {names}")
