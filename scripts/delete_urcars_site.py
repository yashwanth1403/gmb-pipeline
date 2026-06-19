"""Delete the 'urcars' Netlify site so we can create a clean 'ur-car' site."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa
import os
import pathlib

from agents.site_builder import _run_subprocess

site_id = "c0f304e0-6746-4f23-8f11-bb52e261be5c"  # urcars

r = _run_subprocess(
    ["netlify", "sites:delete", site_id, "--force"],
    cwd=pathlib.Path("."),
    timeout=30,
)
print(f"returncode: {r.returncode}")
print(f"stdout: {r.stdout}")
print(f"stderr: {r.stderr}")
