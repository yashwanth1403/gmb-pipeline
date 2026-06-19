"""Check netlify account status."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa
import os
import pathlib

from agents.site_builder import _run_subprocess

r = _run_subprocess(["netlify", "status", "--json"], cwd=pathlib.Path("."), timeout=30)
print(f"returncode: {r.returncode}")
print(f"stdout: {r.stdout[:2000]}")
print(f"stderr: {r.stderr[:1000]}")
