"""
pipeline.py — Full lead-to-URL pipeline

Usage:
  python pipeline.py --lead leads/dealer.json --react-dir ../car-dealer-template
  python pipeline.py --lead leads/dealer.json --react-dir ../car-dealer-template --no-llm
  python pipeline.py --lead leads/dealer.json --react-dir ../car-dealer-template --no-deploy

What it does:
  1. Read GBP lead JSON
  2. Call OpenAI to generate marketing copy (tagline, about, hero subhead)
  3. Generate SVG logo
  4. Write dealer.json + testimonials.json into the React project
  5. Run `npm run build` → dist/
  6. Deploy dist/ to Netlify → prints live HTTPS URL  (skip with --no-deploy)
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from llm.openai_client import generate_content
from llm.response_parser import validate_and_fill, DEFAULTS
from react_builder import write_json_files, vite_build
from deployer import deploy


def run(lead_path: Path, react_dir: Path, use_llm: bool, do_deploy: bool) -> str | None:
    lead = json.loads(lead_path.read_text(encoding="utf-8"))
    b    = lead["business"]
    name = b.get("name", "Car Dealer")

    print(f"\n=== Pipeline: {name} ===")

    # ── Step 1: LLM content generation ───────────────────────────────────────
    if "llm" in lead and lead["llm"]:
        print("  ℹ️  Using embedded LLM content from lead JSON")
        lead["llm"] = validate_and_fill(lead["llm"])
    elif use_llm:
        print(f"  🤖 Calling Claude for \"{name}\"...")
        try:
            raw = generate_content(lead)
            lead["llm"] = validate_and_fill(raw)
            print("  ✅ LLM content generated")
        except Exception as exc:
            print(f"  ⚠️  LLM call failed ({exc}). Using defaults.")
            lead["llm"] = DEFAULTS.copy()
    else:
        print("  ⏭️  Skipping LLM (--no-llm)")
        lead["llm"] = DEFAULTS.copy()

    # ── Step 2: Write JSON config into React project ──────────────────────────
    write_json_files(lead, lead["llm"], react_dir)

    # ── Step 3: Vite build ────────────────────────────────────────────────────
    dist = vite_build(react_dir)

    # ── Step 4: Deploy ────────────────────────────────────────────────────────
    if do_deploy:
        url = deploy(dist, name)
        print(f"\n{'='*50}")
        print(f"  🌐  Live URL: {url}")
        print(f"{'='*50}\n")
        return url
    else:
        print(f"\n  dist ready at: {dist}")
        print("  (deploy skipped — remove --no-deploy to publish)\n")
        return None


def main():
    parser = argparse.ArgumentParser(description="GBP lead → React build → Netlify URL")
    parser.add_argument("--lead",      required=True, help="Path to lead JSON")
    parser.add_argument("--react-dir", required=True, help="Path to car-dealer-template project")
    parser.add_argument("--no-deploy", action="store_true", help="Skip Netlify deploy (build only)")
    parser.add_argument("--no-llm",   action="store_true", help="Skip OpenAI, use default copy")
    args = parser.parse_args()

    lead_path  = Path(args.lead).expanduser().resolve()
    react_dir  = Path(args.react_dir).expanduser().resolve()

    if not lead_path.exists():
        sys.exit(f"Lead file not found: {lead_path}")
    if not react_dir.exists():
        sys.exit(f"React project not found: {react_dir}")

    run(lead_path, react_dir, use_llm=not args.no_llm, do_deploy=not args.no_deploy)


if __name__ == "__main__":
    main()
