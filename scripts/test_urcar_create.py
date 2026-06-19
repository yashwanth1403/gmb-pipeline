"""Test creating 'ur-car' directly via netlify CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa
import os
import json
import pathlib

from agents.site_builder import _run_subprocess

token = os.environ["NETLIFY_AUTH_TOKEN"]
print(f"--- Test: create 'ur-car' with --account-slug yashwanth1403 ---")
r = _run_subprocess(
    ["netlify", "sites:create",
     "--name", "ur-car",
     "--auth", token,
     "--account-slug", "yashwanth1403",
     "--json"],
    cwd=pathlib.Path("."),
    timeout=60,
)
print(f"returncode: {r.returncode}")
print(f"stdout: {r.stdout[:1500]}")
print(f"stderr: {r.stderr[:500]}")
