"""
scrape_40.py — Run the scraper, get 40 results, show what passes each filter.
"""
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import env_loader
import requests

from agents.business_classifier import classify
from config import SCRAPE_KINDS

key = os.environ["SERPAPI_KEY"]
query = os.environ.get("GMB_QUERY", "used cars in kokapet")

# Resolve the simple kind filter
kinds = None
if SCRAPE_KINDS and SCRAPE_KINDS.strip().lower() != "any":
    kinds = {k.strip() for k in SCRAPE_KINDS.split(",") if k.strip()}

print("=" * 80)
print(f"Query: {query!r}")
print(f"Fetching 2 pages (40 results) from SerpAPI")
print(f"Simple filter (SCRAPE_KINDS): {kinds}")
print("=" * 80)

# Fetch 2 pages
all_results = []
for start in [0, 20]:
    r = requests.get(
        "https://serpapi.com/search.json",
        params={"engine": "google_maps", "q": query, "api_key": key, "start": start},
        timeout=30,
    )
    data = r.json()
    page = data.get("local_results", [])
    all_results.extend(page)
    print(f"  Page {start // 20 + 1}: got {len(page)} results")

print()
print(f"Total raw: {len(all_results)}")
print()

# Apply the SAME 3 filters the scraper uses
print("=" * 80)
print("FILTER PROGRESSION")
print("=" * 80)
print()

# Filter 0: name and phone (we'll fake these for the test since not all results have them)
filter0_drops = []
remaining = []
for p in all_results:
    title = p.get("title", "?")
    if not title:
        filter0_drops.append(("no name", p))
        continue
    remaining.append(p)

print(f"  After 'has name' filter: {len(remaining)} (dropped {len(filter0_drops)})")

# Filter 1: has_website
filter1_drops = []
remaining2 = []
for p in remaining:
    if p.get("website"):
        filter1_drops.append(("has_website", p))
    else:
        remaining2.append(p)
print(f"  After 'no website' filter: {len(remaining2)} (dropped {len(filter1_drops)} with website)")

# Filter 2: has phone
filter2_drops = []
remaining3 = []
for p in remaining2:
    if not p.get("phone"):
        filter2_drops.append(("no_phone", p))
    else:
        remaining3.append(p)
print(f"  After 'has phone' filter: {len(remaining3)} (dropped {len(filter2_drops)} without phone)")

# Filter 3: simple business_kind
filter3_drops = []
remaining4 = []
for p in remaining3:
    lead_kind = (p.get("type_ids") or [None])[0]
    if kinds is not None and lead_kind not in kinds:
        filter3_drops.append((lead_kind, p))
    else:
        remaining4.append(p)
print(f"  After 'SCRAPE_KINDS' filter: {len(remaining4)} (dropped {len(filter3_drops)} with wrong kind)")

# Filter 4: robust classifier
filter4_drops = []
final_saved = []
for p in remaining4:
    lead = {
        "place_id": p.get("place_id", "x"),
        "business": {
            "name": p.get("title"),
            "category": p.get("type") or p.get("category"),
            "type_ids": p.get("type_ids") or [],
        },
    }
    is_used, conf, reason = classify(lead)
    if not is_used:
        filter4_drops.append((reason, p))
    else:
        final_saved.append((lead, conf, reason))

print(f"  After 'business_classifier' filter: {len(final_saved)} (dropped {len(filter4_drops)} as not used car)")
print()

# Show what got dropped at each stage
print("=" * 80)
print("DROPPED AT FILTER 1 (has_website): " + str(len(filter1_drops)))
print("=" * 80)
for reason, p in filter1_drops[:10]:
    print(f"  - {p.get('title')[:50]:50s}  {p.get('website', '')[:60]}")
if len(filter1_drops) > 10:
    print(f"  ... and {len(filter1_drops) - 10} more")
print()

print("=" * 80)
print("DROPPED AT FILTER 3 (SCRAPE_KINDS): " + str(len(filter3_drops)))
print("=" * 80)
for kind, p in filter3_drops:
    print(f"  - kind='{kind}'  {p.get('title')[:50]}")
print()

print("=" * 80)
print("DROPPED AT FILTER 4 (business_classifier): " + str(len(filter4_drops)))
print("=" * 80)
for reason, p in filter4_drops:
    print(f"  - {p.get('title')[:40]:40s}  {reason[:80]}")
print()

print("=" * 80)
print(f"FINAL SAVED: {len(final_saved)} leads")
print("=" * 80)
for lead, conf, reason in final_saved:
    print(f"  ✅ ({conf:.2f}) {lead['business']['name'][:50]}")
    print(f"      {reason[:100]}")
