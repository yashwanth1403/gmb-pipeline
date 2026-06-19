"""
run_pipeline.py — Fully autonomous end-to-end pipeline.

Runs:
    1. Agent 1 (GMB Scraper)   — fetch leads from SerpAPI
    2. Agent 2 (Site Builder)  — build + (optionally) deploy to Netlify
    3. Agent 3 (Outreach)      — WhatsApp cold outreach (opt-in)

Designed to be run unattended. Exit code reflects the final result:
    0  → all leads built (and deployed + messaged if those steps were on)
    1  → one or more leads failed
    2  → no leads found at all (different from "0 leads built")

Usage:
    python scripts/run_pipeline.py                          # scrape + build (no deploy)
    python scripts/run_pipeline.py --deploy                 # scrape + build + deploy
    python scripts/run_pipeline.py --outreach               # scrape + build + outreach
    python scripts/run_pipeline.py --deploy --outreach      # full chain
    python scripts/run_pipeline.py --query "..." --max 5    # custom query
    python scripts/run_pipeline.py --skip-scrape            # use existing leads.json
    python scripts/run_pipeline.py --skip-build             # only scrape, no build
    python scripts/run_pipeline.py --enrich                 # full enrichment pass
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import RUN_AGENT3_AUTOMATIC
from agents.gmb_scraper import GMBScraper
from agents.site_builder import SiteBuilder


def main():
    ap = argparse.ArgumentParser(
        description="Fully autonomous GMB → Site → Outreach pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--query", default=None, help="GMB search query (overrides .env GMB_QUERY)")
    ap.add_argument("--location", default=None, help="GMB location for radius filter")
    ap.add_argument("--max", dest="max_results", type=int, default=None, help="cap leads saved (post-filter)")
    ap.add_argument("--deploy", action="store_true", help="deploy to Netlify after build")
    ap.add_argument("--outreach", action="store_true",
                    help="run Agent 3 WhatsApp outreach at the end (requires QR session + RUN_AGENT3_AUTOMATIC)")
    ap.add_argument("--outreach-dry-run", action="store_true",
                    help="generate WhatsApp messages but don't send (preview only)")
    ap.add_argument("--outreach-max", type=int, default=None, help="cap leads to message in Agent 3")
    ap.add_argument("--enrich", action="store_true", help="enrich leads with full place details")
    ap.add_argument("--enrich-limit", type=int, default=None, help="cap enrichment to N leads")
    ap.add_argument("--no-llm", action="store_true", help="skip OpenAI LLM (use defaults)")
    ap.add_argument("--no-logo", action="store_true", help="skip OpenAI logo generation")
    ap.add_argument("--force-rebuild", action="store_true", help="rebuild already-built leads")
    ap.add_argument("--skip-scrape", action="store_true", help="use existing leads.json (don't re-scrape)")
    ap.add_argument("--skip-build", action="store_true", help="only scrape, don't build")
    args = ap.parse_args()

    # Resolve whether Agent 3 should run: explicit --outreach flag OR
    # RUN_AGENT3_AUTOMATIC=true in .env.
    run_agent3 = args.outreach or RUN_AGENT3_AUTOMATIC

    print("=" * 70)
    chain = ["Agent 1: Scrape", "Agent 2: Build"]
    if args.deploy:
        chain.append("Deploy")
    if run_agent3:
        chain.append("Agent 3: Outreach")
    print(f"🚀 AUTONOMOUS PIPELINE: {' → '.join(chain)}")
    print("=" * 70)
    print()

    # ---------- Agent 1: Scrape ----------
    if not args.skip_scrape:
        print("─" * 70)
        print("AGENT 1: GMB Scraper")
        print("─" * 70)
        scraper = GMBScraper()
        try:
            scraper.run(
                query=args.query,
                location=args.location,
                max_results=args.max_results,
                enrich=args.enrich,
                enrich_limit=args.enrich_limit,
            )
        except Exception as e:
            print(f"\n❌ Agent 1 crashed: {e}")
            sys.exit(1)
        print()
    else:
        print("⏭️  Skipping Agent 1 (using existing leads.json)")
        print()

    # ---------- Agent 2: Build ----------
    if args.skip_build:
        print("⏭️  Skipping Agent 2 (--skip-build)")
        print()
        print("✅ Pipeline finished (scrape-only mode)")
        return 0

    print("─" * 70)
    print("AGENT 2: Site Builder" + (" + Netlify Deploy" if args.deploy else ""))
    print("─" * 70)
    builder = SiteBuilder()
    try:
        results = builder.run(
            deploy=args.deploy,
            use_llm=not args.no_llm,
            generate_logo=not args.no_logo,
            force_rebuild=args.force_rebuild,
            only_kind="",  # build all kinds, not just used_car_dealer
        )
    except Exception as e:
        print(f"\n❌ Agent 2 crashed: {e}")
        sys.exit(1)
    print()

    # ---------- Summary ----------
    print("=" * 70)
    print("📊 PIPELINE SUMMARY")
    print("=" * 70)
    print(f"  Built:   {results.get('built', 0)}")
    print(f"  Deployed: {results.get('deployed', 0)}")
    print(f"  Skipped:  {results.get('skipped', 0)}  (already in built_sites.json)")
    print(f"  Errors:   {results.get('errors', 0)}")
    if results.get("urls"):
        print()
        print("  🌐 Live URLs:")
        for url in results["urls"]:
            print(f"     → {url}")
    print()
    print("=" * 70)

    if results.get("errors", 0) > 0:
        return 1
    if results.get("built", 0) == 0 and results.get("skipped", 0) == 0:
        return 2

    # ---------- Agent 3: Outreach ----------
    outreach_summary = None
    if run_agent3:
        if not args.deploy:
            print("\n⚠️  Note: --outreach is set but --deploy is not.")
            print("   Agent 3 will only message businesses that already have site_url")
            print("   in data/built_sites.json (i.e. previously deployed).\n")

        print("─" * 70)
        print("AGENT 3: WhatsApp Outreach" + (" (DRY RUN)" if args.outreach_dry_run else ""))
        print("─" * 70)
        from agents.outreach import OutreachAgent
        out_agent = OutreachAgent()
        try:
            outreach_summary = out_agent.run(
                dry_run=args.outreach_dry_run,
                max_leads=args.outreach_max,
            )
        except Exception as e:
            print(f"\n❌ Agent 3 crashed: {e}")
            return 1
        print()

        # If anything failed to send, return non-zero so cron / CI sees it
        if outreach_summary.get("failed", 0) > 0:
            return 1
    elif RUN_AGENT3_AUTOMATIC is False and args.outreach is False:
        # Hint that Agent 3 exists now
        print("💡 Tip: Agent 3 (WhatsApp outreach) is wired in but not running.")
        print("   To enable: set RUN_AGENT3_AUTOMATIC=true in .env, OR pass --outreach")
        print("   First-time setup: cd whatsapp-sender/sender && npm install && node sender.js setup")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
