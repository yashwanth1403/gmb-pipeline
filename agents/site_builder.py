"""
site_builder.py — Agent 2: Website Builder + Netlify Deployer

Reads leads from data/leads.json (produced by Agent 1),
builds a React site for each car-dealer lead using the cloned
`car-dealers-template`, and (optionally) deploys to Netlify.

Pipeline per lead:
    1. Copy the React template into a per-lead workdir
    2. Generate marketing copy via OpenAI (cached)
    3. Generate SVG logo via OpenAI (cached)
    4. Write dealer.json + testimonials.json into the template
    5. Run `npm run build` → dist/
    6. Optionally deploy dist/ to Netlify → live URL
    7. Save the live URL back into the lead record
    8. Update queue.json with stage="build", status="done"

Usage:
    python -m agents.site_builder                          # build all leads
    python -m agents.site_builder --place-id <id>         # build one lead
    python -m agents.site_builder --limit 5               # build first 5
    python -m agents.site_builder --deploy                # also deploy to Netlify
    python -m agents.site_builder --no-llm                # skip OpenAI calls
    python -m agents.site_builder --no-logo               # skip logo generation
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Make sure env vars are loaded BEFORE we import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa: F401  (side-effect: loads .env)

from config import (
    REACT_TEMPLATE_DIR,
    SITE_BUILDER_WORKDIR,
    USE_LLM,
    GENERATE_LOGO,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_LOGO_MODEL,
    DEPLOY_TO_NETLIFY,
    NETLIFY_AUTH_TOKEN,
    BUILDER_ALLOWED_KINDS,
)

from agents.base_agent import BaseAgent, now_iso, get_logger

# Make the cloned generator's modules importable
GEN_DIR = REACT_TEMPLATE_DIR.parent / "car_dealer_generator"
sys.path.insert(0, str(GEN_DIR))


class SiteBuilder(BaseAgent):
    name = "site_builder"

    def __init__(self):
        super().__init__()
        # Sanity checks at startup so failures are loud, not silent
        if not REACT_TEMPLATE_DIR.exists():
            self.log.error(f"React template not found at {REACT_TEMPLATE_DIR}")
            self.log.error("Did the clone succeed? Check external/car-dealers-template/")
            sys.exit(1)
        if not (REACT_TEMPLATE_DIR / "package.json").exists():
            self.log.error(f"No package.json in {REACT_TEMPLATE_DIR}")
            sys.exit(1)
        # Lazy-import the generator modules so missing deps only break at build-time
        try:
            from llm.openai_client import generate_content  # noqa
            from llm.response_parser import validate_and_fill, DEFAULTS  # noqa
            from react_builder import write_json_files, vite_build  # noqa
            from deployer import deploy as netlify_deploy  # noqa
            self._generate_content = generate_content
            self._validate_and_fill = validate_and_fill
            self._DEFAULTS = DEFAULTS
            self._write_json_files = write_json_files
            self._vite_build = vite_build
            self._netlify_deploy = netlify_deploy
        except ImportError as e:
            self.log.error(f"Failed to import generator modules from {GEN_DIR}: {e}")
            self.log.error(f"sys.path includes: {[p for p in sys.path if 'gmb-pipeline' in p]}")
            sys.exit(1)

    # ---------- public API ----------
    def run(
        self,
        place_id: Optional[str] = None,
        limit: Optional[int] = None,
        deploy: Optional[bool] = None,
        use_llm: Optional[bool] = None,
        generate_logo: Optional[bool] = None,
        only_kind: str = "used_car_dealer",
        force_rebuild: bool = False,
    ) -> dict:
        """
        place_id     : build only this lead. None = all eligible leads.
        limit        : cap number of leads processed this run.
        deploy       : override DEPLOY_TO_NETLIFY from .env for this run.
        use_llm      : override USE_LLM for this run.
        generate_logo: override GENERATE_LOGO for this run.
        only_kind    : only build leads whose business_kind matches (default "used_car_dealer"
                       — the only template we have today).
        force_rebuild: ignore built_sites.json and rebuild every eligible lead.
        """
        # Resolve effective settings
        deploy_flag = DEPLOY_TO_NETLIFY if deploy is None else deploy
        llm_flag = USE_LLM if use_llm is None else use_llm
        logo_flag = GENERATE_LOGO if generate_logo is None else generate_logo

        self.log.info(
            f"START  place_id={place_id or '(all)'} limit={limit} "
            f"deploy={deploy_flag} llm={llm_flag} logo={logo_flag} kind={only_kind}"
        )

        leads = self.load_leads()
        # Filter to eligible leads
        # If only_kind is empty, default to the BUILDER_ALLOWED_KINDS allowlist
        # (defense in depth). If only_kind is "any", accept everything.
        if only_kind == "any":
            eligible = list(leads)
            self.log.info("Filter: building all leads (only_kind=any)")
        elif only_kind:
            eligible = [l for l in leads if l.get("business", {}).get("business_kind") == only_kind]
        else:
            allowed = {k.strip() for k in BUILDER_ALLOWED_KINDS.split(",") if k.strip()}
            self.log.info(f"Filter: only building business_kinds in {sorted(allowed)} (per BUILDER_ALLOWED_KINDS)")
            eligible = [l for l in leads if l.get("business", {}).get("business_kind") in allowed]
        if place_id:
            eligible = [l for l in eligible if l.get("place_id") == place_id]
            if not eligible:
                self.log.error(f"No lead found with place_id={place_id}")
                return {"built": 0, "deployed": 0, "errors": 1}
        if limit:
            eligible = eligible[:limit]

        # Dedup: filter out leads we've already built. This is the single
        # source of truth — even a fresh scrape that re-pulls Ur.Car will
        # be skipped here. Override with --force-rebuild.
        before_dedup = len(eligible)
        if not force_rebuild:
            eligible = [l for l in eligible if not self.is_built(l)]
        skipped = before_dedup - len(eligible)
        if skipped:
            self.log.info(
                f"Skipped {skipped} lead(s) already in built_sites.json "
                f"(use --force-rebuild to override)"
            )
        if not eligible:
            self.log.info("No new leads to build. Exiting.")
            return {"built": 0, "deployed": 0, "errors": 0, "urls": [], "skipped": skipped}

        self.log.info(f"Eligible leads: {len(eligible)}")

        results = {"built": 0, "deployed": 0, "errors": 0, "urls": [], "skipped": skipped}

        for lead in eligible:
            try:
                self.log.info(f"\n--- Building {lead['business'].get('name', place_id)} ---")
                url = self._build_one(lead, deploy=deploy_flag, use_llm=llm_flag, generate_logo=logo_flag)
                results["built"] += 1
                if url:
                    results["deployed"] += 1
                    results["urls"].append(url)
            except Exception as e:
                self.log.error(f"Build failed for {lead.get('place_id')}: {e}")
                results["errors"] += 1

        self.log.info(
            f"DONE   built={results['built']} deployed={results['deployed']} "
            f"errors={results['errors']} skipped={results['skipped']}"
        )
        return results

    # ---------- per-lead build ----------
    def _patch_index_html(self, workdir: Path, lead: dict, llm: dict) -> None:
        """
        Patch the React template's static `index.html` (Vite reads it as a
        template at build time) with real lead data. The template ships
        hard-coded with "Shree Vaishnavi Cars" — we override:

          - <title>                  → "{Dealer Name} | {Tagline}"
          - <meta name="description"> → LLM meta_description
          - <meta name="author">      → dealer name
          - og:title, og:description → same as title + meta_description
          - og:image                 → thumbnail from lead
          - twitter:site             → dealer name
          - <link rel="icon">        → /logos/{slug}.svg
        """
        import re

        b = lead["business"]
        # Use the LLM's clean business name if present (fixes the long-GBP-name issue)
        name = llm.get("business_name") or b.get("name", "Site")
        # Sanitize as a final safety net
        from external.car_dealer_generator.llm.response_parser import _sanitize_business_name
        name = _sanitize_business_name(name) or name
        tagline = llm.get("tagline", "Quality used cars")
        meta_desc = llm.get("meta_description", "")
        if not meta_desc:
            meta_desc = f"{name} — {tagline}."

        # Thumbnail: prefer the lead's latest photo, then the Google thumbnail
        thumb = (
            b.get("photo_latest")
            or b.get("photo_inside")
            or b.get("photo_exterior")
            or b.get("thumbnail")
            or ""
        )

        # Logo file: /logos/{slug}.svg (written earlier in the pipeline)
        slug = _slugify(name)
        favicon = f"/logos/{slug}.svg"

        full_title = f"{name} | {tagline}"

        index_html = workdir / "index.html"
        if not index_html.exists():
            self.log.warning("  ⚠️  No index.html to patch (skipping SEO override)")
            return

        html = index_html.read_text(encoding="utf-8")

        # Replace <title>...</title>
        html = re.sub(
            r"<title>.*?</title>",
            f"<title>{full_title}</title>",
            html,
            count=1,
            flags=re.DOTALL,
        )
        # Replace meta description
        html = re.sub(
            r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',
            f'<meta name="description" content="{meta_desc}" />',
            html,
            count=1,
        )
        # Replace meta author
        html = re.sub(
            r'<meta\s+name="author"\s+content="[^"]*"\s*/?>',
            f'<meta name="author" content="{name}" />',
            html,
            count=1,
        )
        # Replace favicon
        html = re.sub(
            r'<link rel="icon"[^>]*href="[^"]*"[^>]*>',
            f'<link rel="icon" type="image/svg+xml" href="{favicon}" />',
            html,
            count=1,
        )
        # Replace og:title
        html = re.sub(
            r'<meta\s+property="og:title"\s+content="[^"]*"\s*/?>',
            f'<meta property="og:title" content="{full_title}" />',
            html,
            count=1,
        )
        # Replace og:description
        html = re.sub(
            r'<meta\s+property="og:description"\s+content="[^"]*"\s*/?>',
            f'<meta property="og:description" content="{meta_desc}" />',
            html,
            count=1,
        )
        # Replace og:image
        if thumb:
            html = re.sub(
                r'<meta\s+property="og:image"\s+content="[^"]*"\s*/?>',
                f'<meta property="og:image" content="{thumb}" />',
                html,
                count=1,
            )
        # Replace twitter:site
        html = re.sub(
            r'<meta\s+name="twitter:site"\s+content="[^"]*"\s*/?>',
            f'<meta name="twitter:site" content="{name}" />',
            html,
            count=1,
        )

        index_html.write_text(html, encoding="utf-8")
        self.log.info(f"  🏷️  Patched index.html: title='{full_title}', desc len={len(meta_desc)}")

    def _build_one(
        self,
        lead: dict,
        deploy: bool,
        use_llm: bool,
        generate_logo: bool,
    ) -> Optional[str]:
        """
        Build one lead's site. Returns the deployed URL if deploy=True, else None.
        Updates the lead in data/leads.json with the live URL and queue.json.
        """
        place_id = lead["place_id"]
        b = lead["business"]
        name = b.get("name", "site")

        # ---- DEFENSE IN DEPTH ----
        # Three layers of protection so we never accidentally build a site
        # for a non-car-dealer:
        #   1. Config allowlist (BUILDER_ALLOWED_KINDS)
        #   2. Robust classifier (checks all type_ids + name + category)
        #   3. Hard error if any of the above reject this lead
        lead_kind = b.get("business_kind")
        allowed = {k.strip() for k in BUILDER_ALLOWED_KINDS.split(",") if k.strip()}
        if lead_kind not in allowed:
            self.log.error(
                f"  ❌ REFUSED: {name} has business_kind='{lead_kind}' "
                f"(not in {sorted(allowed)}). The car-dealer template is not a fit."
            )
            raise ValueError(
                f"Refusing to build {name}: business_kind='{lead_kind}' "
                f"is not in the allowed list {sorted(allowed)}"
            )

        # Layer 2: robust classifier (catches "car_dealer" type_ids + name patterns)
        from agents.business_classifier import classify as classify_business
        is_used, confidence, reason = classify_business(lead)
        if not is_used:
            self.log.error(
                f"  ❌ REFUSED: {name} failed business_classifier: {reason}"
            )
            raise ValueError(
                f"Refusing to build {name}: classifier says not used car dealer. "
                f"Reason: {reason}"
            )
        if confidence < 0.6:
            # Ambiguous case — log loudly but allow (operator can decide later)
            self.log.warning(
                f"  ⚠️  AMBIGUOUS: {name} classified as used car dealer "
                f"with low confidence {confidence:.2f}: {reason}"
            )
        else:
            self.log.info(
                f"  ✅ Classified: {name} → used car dealer "
                f"(confidence {confidence:.2f}): {reason}"
            )

        # 1. Set up a per-lead workdir (copy of the React template)
        slug = _slugify(name)
        workdir = SITE_BUILDER_WORKDIR / slug
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.parent.mkdir(parents=True, exist_ok=True)

        self.log.info(f"  📁 Copying template → {workdir}")
        shutil.copytree(
            REACT_TEMPLATE_DIR,
            workdir,
            # Skip everything that doesn't belong in a build workspace:
            # node_modules (huge, re-installed), dist (build output),
            # .git (locked pack files on Windows), .netlify/.cache (deploy state)
            ignore=shutil.ignore_patterns(
                "node_modules", "dist", ".git", ".gitignore",
                ".netlify", ".cache", "bun.lockb", "*.log",
            ),
        )

        # 2. Generate or reuse LLM content
        if use_llm:
            if not OPENAI_API_KEY:
                self.log.error("  ⚠️  OPENAI_API_KEY missing — skipping LLM call, using defaults")
                lead["llm"] = self._DEFAULTS.copy()
            else:
                self.log.info("  🤖 Calling OpenAI for marketing copy...")
                try:
                    raw = self._generate_content(lead)
                    lead["llm"] = self._validate_and_fill(raw, lead=lead)
                    self.log.info("  ✅ LLM content generated")
                except Exception as e:
                    self.log.error(f"  ⚠️  OpenAI call failed: {e} — using defaults")
                    lead["llm"] = self._DEFAULTS.copy()
        elif lead.get("llm") and all(k in lead["llm"] for k in ("tagline", "about_us", "hero_subhead", "cta_text")):
            # --no-llm but lead already has complete embedded llm content → reuse it
            self.log.info("  ℹ️  Using embedded llm content from lead JSON")
            lead["llm"] = self._validate_and_fill(lead["llm"], lead=lead)
        else:
            # --no-llm AND no usable embedded content → use defaults
            self.log.info("  ⏭️  Skipping LLM (--no-llm, no embedded content) — using defaults")
            lead["llm"] = self._DEFAULTS.copy()

        # 3. Write JSON files into the per-lead workdir
        self._write_json_files(lead, lead["llm"], workdir)

        # 3b. Patch the static index.html SEO tags (title, meta description, OG tags).
        # The template ships with hard-coded "Shree Vaishnavi Cars" — we override
        # with real values from the lead so the deployed site shows the right
        # name in browser tabs, search results, and social previews.
        self._patch_index_html(workdir, lead, lead["llm"])

        # 4. npm install (only if node_modules missing)
        if not (workdir / "node_modules").exists():
            self.log.info("  📦 npm install (one-time per lead workdir)...")
            result = _run_subprocess(
                ["npm", "install", "--no-audit", "--no-fund", "--loglevel=error"],
                cwd=workdir,
                timeout=600,
            )
            if result.returncode != 0:
                raise RuntimeError(f"npm install failed: {result.stderr[-1500:]}")
        else:
            self.log.info("  📦 npm modules already present")

        # 5. npm run build
        self.log.info("  🔨 vite build...")
        dist = self._vite_build(workdir)

        # 6. Optional: deploy to Netlify
        url: Optional[str] = None
        if deploy:
            if not NETLIFY_AUTH_TOKEN:
                self.log.error("  ⚠️  NETLIFY_AUTH_TOKEN missing — skipping deploy")
                self.log.info(f"  💾 Build output: {dist}")
                self.log.info("     (set NETLIFY_AUTH_TOKEN in .env or pass --no-deploy)")
            else:
                os.environ["NETLIFY_AUTH_TOKEN"] = NETLIFY_AUTH_TOKEN
                self.log.info("  🚀 Deploying to Netlify...")
                try:
                    url = self._netlify_deploy(dist, name)
                    self.log.info(f"  🌐 Live URL: {url}")
                except Exception as e:
                    self.log.error(f"  ⚠️  Netlify deploy failed: {e}")
                    self.log.info(f"  💾 Build output (deploy failed): {dist}")
        else:
            self.log.info(f"  💾 Build output: {dist}")
            self.log.info("     (deploy skipped — set DEPLOY_TO_NETLIFY=true or pass --deploy)")

        # 7. Save the URL + build state back into the lead
        # Increment build attempt counter; bump lead status from "scraped" → "built"
        lead.setdefault("attempts", {"scrape": 0, "build": 0, "outreach": 0})
        lead["attempts"]["build"] = lead["attempts"].get("build", 0) + 1
        b = lead["business"]
        if url:
            lead["site_url"] = url
            lead["site_built_at"] = now_iso()
            lead["status"] = "built"
            self.upsert_lead(lead)
            self.set_queue(place_id, stage="build", status="done", site_url=url)
            # Register in the cross-run dedup registry so future runs skip this
            self.mark_built(
                place_id=place_id,
                name=b.get("name", "Unknown"),
                address=b.get("address", ""),
                phone=b.get("phone", ""),
                site_url=url,
            )
        else:
            lead["site_dist_path"] = str(dist.relative_to(SITE_BUILDER_WORKDIR.parent))
            lead["site_built_at"] = now_iso()
            lead["status"] = "built-local"
            self.upsert_lead(lead)
            self.set_queue(place_id, stage="build", status="built-local")
            # Even local builds get registered — the build work is done, no
            # need to redo it next run.
            self.mark_built(
                place_id=place_id,
                name=b.get("name", "Unknown"),
                address=b.get("address", ""),
                phone=b.get("phone", ""),
                site_url="",
                extra={"built_locally": True, "dist_path": str(dist)},
            )

        return url


def _slugify(name: str) -> str:
    import re
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "site"


def _run_subprocess(cmd: list, cwd: Path, timeout: int = 600) -> "subprocess.CompletedProcess":
    """
    Run a subprocess reliably on Windows. We can't rely on `subprocess.run(cmd)`
    alone because the inherited PATH may not include npm/node locations (common
    when Python is launched from a non-interactive shell or sandbox).

    Strategy:
    - Add the default Node.js install location to PATH as a safety net.
    - On Windows, npm is actually npm.cmd; we need to either:
        (a) use shell=True with a safely-quoted command string, OR
        (b) resolve .cmd/.bat to the .exe equivalent
    We go with (b) using shutil.which — it's safer and avoids shell injection.
    """
    import subprocess
    import sys
    import shutil as _shutil

    env = os.environ.copy()
    node_default = r"C:\Program Files\nodejs"
    if node_default not in env.get("PATH", ""):
        env["PATH"] = node_default + os.pathsep + env.get("PATH", "")

    # On Windows, npm/npx commands are .cmd shims. Python's subprocess won't
    # resolve them unless we find the .cmd explicitly. Only the EXECUTABLE
    # (first arg) should be resolved — subcommands like `npm install` must pass
    # through unmodified, otherwise `install` gets resolved to Git's install.EXE.
    resolved_cmd = list(cmd)
    if cmd and sys.platform.startswith("win") and "\\" not in cmd[0] and "/" not in cmd[0]:
        found = _shutil.which(cmd[0], path=env["PATH"])
        if found:
            resolved_cmd[0] = found

    return subprocess.run(
        resolved_cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )


# ---------- CLI ----------
def main():
    import argparse
    p = argparse.ArgumentParser(description="GMB Site Builder (Agent 2)")
    p.add_argument("--place-id", default=None, help="build only this lead's place_id")
    p.add_argument("--limit", type=int, default=None, help="cap number of leads to process")
    p.add_argument("--deploy", action="store_true", help="deploy to Netlify (overrides .env)")
    p.add_argument("--no-deploy", action="store_true", help="skip deploy even if .env says deploy")
    p.add_argument("--no-llm", action="store_true", help="skip OpenAI, use defaults")
    p.add_argument("--no-logo", action="store_true", help="skip logo generation")
    p.add_argument("--kind", default="used_car_dealer", help="business_kind to filter on")
    p.add_argument(
        "--force-rebuild",
        action="store_true",
        help="ignore built_sites.json and rebuild every lead (USE WITH CARE — costs OpenAI credits)",
    )
    args = p.parse_args()

    # Resolve deploy flag: explicit --deploy/--no-deploy wins over env
    deploy_arg = None
    if args.deploy:
        deploy_arg = True
    elif args.no_deploy:
        deploy_arg = False

    builder = SiteBuilder()
    results = builder.run(
        place_id=args.place_id,
        limit=args.limit,
        deploy=deploy_arg,
        use_llm=not args.no_llm,
        generate_logo=not args.no_logo,
        only_kind=args.kind,
        force_rebuild=args.force_rebuild,
    )

    # Exit code reflects failures (useful for CI / orchestrator)
    sys.exit(1 if results["errors"] > 0 else 0)


if __name__ == "__main__":
    main()