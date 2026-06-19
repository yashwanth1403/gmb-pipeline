"""Test site creation with explicit team slug."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa
import os
import pathlib

from agents.site_builder import _run_subprocess

print("--- Test 1: bare --name ---")
r = _run_subprocess(
    ["netlify", "sites:create", "--name", "ur-car-test-001", "--auth", os.environ["NETLIFY_AUTH_TOKEN"], "--json"],
    cwd=pathlib.Path("."),
    timeout=30,
)
print(f"rc={r.returncode}")
print(f"stdout: {r.stdout[:1000]}")
print(f"stderr: {r.stderr[:500]}")
print()

print("--- Test 2: --account-slug yashwanth1403 ---")
r = _run_subprocess(
    ["netlify", "sites:create", "--name", "ur-car-test-002", "--auth", os.environ["NETLIFY_AUTH_TOKEN"], "--account-slug", "yashwanth1403", "--json"],
    cwd=pathlib.Path("."),
    timeout=30,
)
print(f"rc={r.returncode}")
print(f"stdout: {r.stdout[:1000]}")
print(f"stderr: {r.stderr[:500]}")
