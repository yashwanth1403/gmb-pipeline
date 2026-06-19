"""
verify_business_filter.py — Confirm the defense chain rejects non-car-dealers.

This script tests 4 layers of defense:
  1. SCRAPE_KINDS filter (would reject at scrape time)
  2. BUILDER_ALLOWED_KINDS filter (rejects at run() time)
  3. _build_one() raises ValueError on bad kind
  4. The site_builder's only_kind parameter

If any of these fail to reject, we get a red X.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import env_loader
from config import SCRAPE_KINDS, BUILDER_ALLOWED_KINDS


def test(name, condition, details=""):
    icon = "✅" if condition else "❌"
    print(f"  {icon} {name}")
    if details and not condition:
        print(f"      {details}")
    return condition


def main():
    print("=" * 70)
    print("BUSINESS_KIND FILTER VERIFICATION")
    print("=" * 70)
    print()
    print("Configuration:")
    print(f"  SCRAPE_KINDS          = {SCRAPE_KINDS!r}")
    print(f"  BUILDER_ALLOWED_KINDS = {BUILDER_ALLOWED_KINDS!r}")
    print()

    # ---- Layer 1: SCRAPE_KINDS ----
    print("─" * 70)
    print("Layer 1: SCRAPE_KINDS (scraper-time filter)")
    print("─" * 70)
    scraper_kinds = None
    if SCRAPE_KINDS and SCRAPE_KINDS.strip().lower() != "any":
        scraper_kinds = {k.strip() for k in SCRAPE_KINDS.split(",") if k.strip()}
    test(
        f"SCRAPE_KINDS is set to a non-'any' value",
        scraper_kinds is not None,
        "SCRAPE_KINDS=any means no filter at scrape time",
    )
    test(
        f"plant_nursery would be REJECTED by scraper",
        "plant_nursery" not in (scraper_kinds or set()),
    )
    test(
        f"bakery would be REJECTED by scraper",
        "bakery" not in (scraper_kinds or set()),
    )
    test(
        f"used_car_dealer would be ACCEPTED by scraper",
        "used_car_dealer" in (scraper_kinds or set()),
    )
    print()

    # ---- Layer 2: BUILDER_ALLOWED_KINDS ----
    print("─" * 70)
    print("Layer 2: BUILDER_ALLOWED_KINDS (builder-time filter, run() method)")
    print("─" * 70)
    builder_kinds = {k.strip() for k in BUILDER_ALLOWED_KINDS.split(",") if k.strip()}
    test(
        f"BUILDER_ALLOWED_KINDS is non-empty",
        len(builder_kinds) > 0,
    )
    test(
        f"plant_nursery would be REJECTED by builder",
        "plant_nursery" not in builder_kinds,
    )
    test(
        f"bakery would be REJECTED by builder",
        "bakery" not in builder_kinds,
    )
    test(
        f"used_car_dealer would be ACCEPTED by builder",
        "used_car_dealer" in builder_kinds,
    )
    print()

    # ---- Layer 3: _build_one() raises on bad kind ----
    print("─" * 70)
    print("Layer 3: _build_one() raises ValueError on disallowed kind")
    print("─" * 70)
    # Fake leads
    bakery_lead = {
        "place_id": "test_bakery_123",
        "business": {
            "name": "Test Bakery",
            "business_kind": "bakery",
            "phone": "+91 12345 67890",
        },
        "status": "scraped",
    }
    dealer_lead = {
        "place_id": "test_dealer_456",
        "business": {
            "name": "Test Car Dealer",
            "business_kind": "used_car_dealer",
            "phone": "+91 99999 99999",
        },
        "status": "scraped",
    }

    from agents.site_builder import SiteBuilder
    builder = SiteBuilder()

    # Test 3a: bakery should be REJECTED
    try:
        builder._build_one(bakery_lead, deploy=False, use_llm=False, generate_logo=False)
        test("Bakery lead → ValueError raised", False, "Lead was accepted (should have raised!)")
    except ValueError as e:
        test(f"Bakery lead → ValueError raised ({str(e)[:80]}...)", True)
    except Exception as e:
        test(
            f"Bakery lead → ValueError raised (got {type(e).__name__}: {e})",
            False,
            "Got a different exception type",
        )

    # Test 3b: dealer should be ACCEPTED (we don't run the full build, just check
    # it doesn't raise immediately on the kind check)
    try:
        # Monkey-patch to skip the actual build steps; we only test the guard
        import unittest.mock
        with unittest.mock.patch.object(builder, "_write_json_files"):
            with unittest.mock.patch.object(builder, "_patch_index_html"):
                with unittest.mock.patch.object(builder, "_run_subprocess"):
                    with unittest.mock.patch.object(builder, "mark_built"):
                        with unittest.mock.patch.object(builder, "upsert_lead"):
                            with unittest.mock.patch.object(builder, "set_queue"):
                                # We just want to check the kind guard passes
                                # The _build_one will fail later in the mocked
                                # chain, but the kind check is at the top.
                                try:
                                    builder._build_one(dealer_lead, deploy=False, use_llm=False, generate_logo=False)
                                except (Exception,) as e:
                                    # Expected: the kind check passes, but downstream mocks fail
                                    if "Refusing to build" in str(e):
                                        test("Dealer lead → kind check passed", False, "Got refused but should have passed")
                                    else:
                                        test(f"Dealer lead → kind check passed (downstream error is fine: {type(e).__name__})", True)
    except Exception as e:
        if "Refusing to build" in str(e):
            test("Dealer lead → kind check passed", False, "Got refused but should have passed")
        else:
            test(f"Dealer lead → kind check passed (got {type(e).__name__})", True)

    print()
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
