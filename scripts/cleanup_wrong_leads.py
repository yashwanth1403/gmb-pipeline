"""
cleanup_wrong_leads.py — Remove businesses that aren't used car dealers.

This script:
  1. Removes non-used_car_dealer leads from data/leads.json
  2. Removes their queue entries
  3. Removes their entries from data/built_sites.json
  4. Optionally deletes their Netlify sites (if --delete-netlify is passed)
  5. Preserves Ur.Car and any real used_car_dealer leads

Run:
    python scripts/cleanup_wrong_leads.py
    python scripts/cleanup_wrong_leads.py --delete-netlify   # also delete the Netlify sites
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    delete_netlify = "--delete-netlify" in sys.argv

    leads_path = ROOT / "data" / "leads.json"
    queue_path = ROOT / "data" / "queue.json"
    built_path = ROOT / "data" / "built_sites.json"

    leads = json.loads(leads_path.read_text(encoding="utf-8"))
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    built = json.loads(built_path.read_text(encoding="utf-8"))

    # Find wrong-kind leads
    keep = []
    wrong = []
    for l in leads:
        kind = l.get("business", {}).get("business_kind")
        if kind == "used_car_dealer":
            keep.append(l)
        else:
            wrong.append(l)

    print(f"Found {len(wrong)} non-car-dealer leads to remove:")
    for l in wrong:
        b = l["business"]
        print(f"  - {b.get('name')} (kind: {b.get('business_kind')})")

    print()
    print(f"Keeping {len(keep)} car-dealer leads:")
    for l in keep:
        print(f"  + {l['business'].get('name')}")
    print()

    # Remove wrong from leads.json
    leads_path.write_text(
        json.dumps(keep, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"✅ Updated {leads_path.name}: {len(leads)} → {len(keep)} leads")

    # Remove wrong from queue.json
    wrong_pids = {l["place_id"] for l in wrong}
    new_queue = {k: v for k, v in queue.items() if k not in wrong_pids}
    queue_path.write_text(
        json.dumps(new_queue, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"✅ Updated {queue_path.name}: {len(queue)} → {len(new_queue)} entries")

    # Remove wrong from built_sites.json
    new_built = {k: v for k, v in built.items() if k not in wrong_pids}
    built_path.write_text(
        json.dumps(new_built, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"✅ Updated {built_path.name}: {len(built)} → {len(new_built)} entries")

    # Delete the Netlify sites
    if delete_netlify and wrong:
        try:
            sys.path.insert(0, str(ROOT))
            import env_loader  # noqa
            from agents.site_builder import _run_subprocess
            import os
            import pathlib

            print()
            print("Deleting Netlify sites for removed leads...")
            for l in wrong:
                name = l["business"]["name"]
                slug = l["business"].get("name", "site").lower()
                # Try to find the site by guessed name
                # (We don't have the site_id stored; query by name from the list)
                r = _run_subprocess(
                    ["netlify", "sites:list", "--json"],
                    cwd=pathlib.Path("."),
                    timeout=30,
                )
                sites = json.loads(r.stdout)
                for s in sites:
                    if name.lower().replace(" ", "-").replace("'", "").replace("&", "") in s["name"].lower():
                        print(f"  Deleting {s['name']} ({s['site_id']})...")
                        rd = _run_subprocess(
                            ["netlify", "sites:delete", s["site_id"], "--force"],
                            cwd=pathlib.Path("."),
                            timeout=30,
                        )
                        print(f"    {rd.stdout.strip()}")
                        break
        except Exception as e:
            print(f"  ⚠️  Netlify cleanup error (manual cleanup needed): {e}")
    else:
        print()
        print("ℹ️  Netlify sites not deleted. Run with --delete-netlify to clean them up.")


if __name__ == "__main__":
    main()
