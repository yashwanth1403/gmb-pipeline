"""
deployer.py
Deploys a dist/ folder to Netlify and returns the live HTTPS URL.

Prerequisites:
  npm install -g netlify-cli
  set NETLIFY_AUTH_TOKEN env var (Personal Access Token from
  https://app.netlify.com/user/applications/personal-access-tokens)

On first deploy, a NAMED site is created using the dealer's slug (e.g. "ur-car"),
so the live URL looks like https://ur-car-madhapur.netlify.app instead of
Netlify's auto-generated random subdomain.

On subsequent deploys the same site is updated (keyed by site_id saved in
external/car_dealer_generator/.cache/netlify_sites.json).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Make sure env_loader has run so we can read NETLIFY_TEAM_SLUG from .env
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    import env_loader  # noqa
except ImportError:
    pass

CACHE_FILE = Path(__file__).parent / ".cache" / "netlify_sites.json"
NETLIFY_TEAM_SLUG = os.environ.get("NETLIFY_TEAM_SLUG", "").strip()


# ---------- cache helpers ----------
def _load_sites() -> dict:
    """Returns {slug: {site_id, url, name}}"""
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_sites(sites: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(sites, indent=2), encoding="utf-8")


def _slugify(name: str) -> str:
    # Netlify site names: lowercase, alphanumeric + hyphens, must start with a letter
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not s or not s[0].isalpha():
        s = "site-" + s
    return s[:30]  # Netlify has a 30-char limit on site names


# ---------- public API ----------
def deploy(dist_dir: Path, business_name: str) -> str:
    """
    Deploy dist_dir to Netlify under a dealer-named subdomain.
    Returns the live URL (e.g. https://ur-car-madhapur.netlify.app).

    Re-uses the same Netlify site on repeated deploys for the same dealer.
    """
    sites = _load_sites()
    slug = _slugify(business_name)
    # Include city to make the name more unique + recognizable: ur-car-madhapur
    site_name = slug
    site_info = sites.get(slug)  # may be None
    site_id = site_info.get("site_id") if site_info else None

    env = os.environ.copy()
    token = env.get("NETLIFY_AUTH_TOKEN", "").strip()
    if not token:
        raise RuntimeError("NETLIFY_AUTH_TOKEN not set in env — add it to .env")
    print(f"  🔑 Using NETLIFY_AUTH_TOKEN (len={len(token)})")
    print(f"  🏷️  Target site name: {site_name}.netlify.app")

    # 1. If we don't have a site yet, create one with the desired name
    if not site_id:
        print(f"  🆕 Creating new Netlify site '{site_name}' ...")
        create_cmd = [
            "netlify", "sites:create",
            "--name", site_name,
            "--auth", token,
            "--json",
        ]
        if NETLIFY_TEAM_SLUG:
            create_cmd += ["--account-slug", NETLIFY_TEAM_SLUG]
        result = _run(create_cmd, cwd=dist_dir.parent, timeout=120)
        if result.returncode != 0:
            # Fallback: if the failure is "name taken", retry without --name
            # so Netlify auto-generates a unique suffix.
            err_text = (result.stderr or "") + (result.stdout or "")
            name_taken = "isn't available" in err_text or "name" in err_text.lower() and "available" in err_text.lower()
            if name_taken:
                print(f"  ⚠️  Name '{site_name}' taken — retrying without --name (Netlify will auto-suffix) ...")
                fallback_cmd = [c for c in create_cmd if c not in ("--name", site_name)]
                result = _run(fallback_cmd, cwd=dist_dir.parent, timeout=120)
            if result.returncode != 0:
                raise RuntimeError(
                    f"netlify sites:create failed:\n{result.stderr}\n{result.stdout}"
                )

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Extract site_id from the URL the CLI usually prints
            m = re.search(r"https://app\.netlify\.com/sites/([a-f0-9-]+)", result.stdout)
            if not m:
                raise RuntimeError(
                    f"sites:create returned no JSON and no parseable site_id.\n"
                    f"Output:\n{result.stdout}\n{result.stderr}"
                )
            site_id = m.group(1)
            data = {"site_id": site_id, "name": site_name, "url": f"https://{site_name}.netlify.app"}

        site_id = data.get("site_id") or data.get("id") or site_id
        site_url = data.get("url") or data.get("ssl_url") or f"https://{site_name}.netlify.app"
        if not site_id:
            raise RuntimeError(
                f"sites:create succeeded but no site_id in response.\n{result.stdout}"
            )

        # Persist for future deploys
        sites[slug] = {"site_id": site_id, "url": site_url, "name": site_name}
        _save_sites(sites)
        print(f"  ✅ Created site: {site_url} (id={site_id})")
    else:
        print(f"  ♻️  Reusing existing site: {site_info.get('url')} (id={site_id})")

    # 2. Deploy to the site
    print(f"  🚀 Deploying dist/ to site {site_id} ...")
    deploy_cmd = [
        "netlify", "deploy",
        "--dir", str(dist_dir),
        "--site", site_id,
        "--auth", token,
        "--prod",
        "--json",
    ]
    result = _run(deploy_cmd, cwd=dist_dir.parent, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"netlify deploy failed:\n{result.stderr}\n{result.stdout}"
        )

    # 3. Parse the response and update cache if the URL changed
    try:
        data = json.loads(result.stdout)
        deploy_url = data.get("deploy_url") or data.get("ssl_url") or data.get("url") or ""
        if not deploy_url and data.get("site_id"):
            # netlify deploy --json doesn't always return deploy_url; fall back to site_url
            deploy_url = site_info.get("url", f"https://{site_name}.netlify.app")
    except json.JSONDecodeError:
        m = re.search(r"https://[^\s]+\.netlify\.app[^\s]*", result.stdout)
        deploy_url = m.group(0).rstrip(".") if m else f"https://{site_name}.netlify.app"

    # Update cache with the latest URL
    if site_id in [v.get("site_id") for v in sites.values()]:
        for k, v in sites.items():
            if v.get("site_id") == site_id:
                v["url"] = deploy_url
        _save_sites(sites)

    print(f"  🌐 Live URL: {deploy_url}")
    return deploy_url


def _run(cmd: list, cwd: Path, timeout: int) -> "subprocess.CompletedProcess":
    """Run netlify CLI reliably (uses Agent 2's Windows-safe wrapper if available)."""
    try:
        from agents.site_builder import _run_subprocess
        return _run_subprocess(cmd, cwd=cwd, timeout=timeout)
    except ImportError:
        return subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy(), cwd=cwd, timeout=timeout)