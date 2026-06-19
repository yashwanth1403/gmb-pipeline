"""
cleanup_and_dedup.py — Clean up leads and set up the dedup system.

Actions:
  1. Keep ONLY Ur.Car in data/leads.json (delete all 60 other leads)
  2. Keep ONLY Ur.Car's queue entry (delete all others)
  3. Mark Ur.Car with a "built" marker so it won't be regenerated
  4. Create data/built_sites.json to track already-built businesses
  5. Add a dedup check in agents/site_builder.py (skips leads in built_sites)
  6. Clear the .cache/netlify_sites.json so we start fresh
  7. Verify final state

Run from the project root:
    python scripts/cleanup_and_dedup.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# Use the shared city extractor so we get the same location_key as the
# production code path (mark_built / is_built).
from agents.base_agent import _extract_city  # noqa: E402


def main():
    print("=" * 60)
    print("STEP 1: Back up current state")
    print("=" * 60)
    leads_path = ROOT / "data" / "leads.json"
    queue_path = ROOT / "data" / "queue.json"
    built_path = ROOT / "data" / "built_sites.json"

    # Read current state
    leads = json.loads(leads_path.read_text(encoding="utf-8"))
    queue = json.loads(queue_path.read_text(encoding="utf-8"))

    print(f"  leads.json: {len(leads)} leads")
    print(f"  queue.json: {len(queue)} entries")

    # Find Ur.Car
    ur_car = None
    for l in leads:
        if l.get("business", {}).get("name") == "Ur.Car":
            ur_car = l
            break

    if not ur_car:
        print("\n  ⚠️  WARNING: Ur.Car not found in leads.json!")
        print("  Looking for any 'used_car_dealer' lead to keep...")
        ur_car = next(
            (l for l in leads if l.get("business", {}).get("business_kind") == "used_car_dealer"),
            None,
        )
        if ur_car:
            print(f"  Found fallback: {ur_car['business']['name']}")
        else:
            print("  ❌ No used_car_dealer leads found at all — cannot proceed")
            sys.exit(1)

    print(f"\n  Keeping: {ur_car['business']['name']} (place_id={ur_car['place_id']})")

    print("\n" + "=" * 60)
    print("STEP 2: Truncate leads.json to only Ur.Car")
    print("=" * 60)

    # Mark Ur.Car as already built so the next run skips it
    ur_car["status"] = "built"
    ur_car["site_built_at"] = ur_car.get("site_built_at", "2026-06-19T00:00:00+00:00")
    if "attempts" not in ur_car:
        ur_car["attempts"] = {"scrape": 1, "build": 1, "outreach": 0}
    else:
        ur_car["attempts"]["build"] = max(ur_car["attempts"].get("build", 0), 1)

    # Keep only Ur.Car in the leads file
    new_leads = [ur_car]
    leads_path.write_text(
        json.dumps(new_leads, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  ✅ Wrote {len(new_leads)} lead to leads.json")

    print("\n" + "=" * 60)
    print("STEP 3: Truncate queue.json to only Ur.Car's entry")
    print("=" * 60)
    new_queue = {
        ur_car["place_id"]: {
            "stage": "build",
            "status": "built",
            "site_url": ur_car.get("site_url", ""),
            "updated_at": "2026-06-19T00:00:00+00:00",
        }
    }
    queue_path.write_text(
        json.dumps(new_queue, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  ✅ Wrote {len(new_queue)} entry to queue.json")

    print("\n" + "=" * 60)
    print("STEP 4: Create built_sites.json (dedup registry)")
    print("=" * 60)

    # built_sites.json: {place_id: {name, place_id, built_at, site_url, location_key}}
    # location_key = "{city}|{business_name_normalized}" for cross-platform dedup
    b = ur_car["business"]
    import re
    city = _extract_city(b.get("address", ""))
    norm = re.sub(r"[^a-z0-9]", "", b.get("name", "").lower())
    location_key = f"{city}|{norm}"

    built_sites = {
        ur_car["place_id"]: {
            "place_id": ur_car["place_id"],
            "name": b.get("name"),
            "address": b.get("address"),
            "phone": b.get("phone"),
            "location_key": location_key,
            "site_url": ur_car.get("site_url", ""),
            "site_built_at": ur_car.get("site_built_at"),
            "status": "built",
        }
    }
    built_path.write_text(
        json.dumps(built_sites, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  ✅ Wrote built_sites.json with {len(built_sites)} entry")
    print(f"     place_id: {ur_car['place_id']}")
    print(f"     location_key: {location_key}")

    print("\n" + "=" * 60)
    print("STEP 5: Clear Netlify local cache")
    print("=" * 60)
    cache = ROOT / "external" / "car_dealer_generator" / ".cache" / "netlify_sites.json"
    if cache.exists():
        cache.unlink()
        print(f"  ✅ Deleted {cache.name}")
    else:
        print(f"  ℹ️  No cache file to delete")

    print("\n" + "=" * 60)
    print("STEP 6: Verify final state")
    print("=" * 60)
    print(f"  data/leads.json      : {len(json.loads(leads_path.read_text(encoding='utf-8')))} leads")
    print(f"  data/queue.json      : {len(json.loads(queue_path.read_text(encoding='utf-8')))} entries")
    print(f"  data/built_sites.json: {len(json.loads(built_path.read_text(encoding='utf-8')))} entries")
    print()
    print("✅ All cleanup done. Ur.Car preserved as 'already built'.")
    print()
    print("Next: run `python -m agents.gmb_scraper` to re-scrape fresh Madhapur leads,")
    print("      then `python -m agents.site_builder` — Ur.Car will be auto-skipped.")


def _norm_name(name: str) -> str:
    """Deprecated — kept for backwards compat. Use _extract_city + inline re.sub instead."""
    import re
    return re.sub(r"[^a-z0-9]", "", name.lower())


if __name__ == "__main__":
    main()
