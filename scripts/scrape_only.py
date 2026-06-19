"""
scrape_only.py — Run ONLY the scraper, show all 20 raw results, no filters.

Use this to debug "why did this business show up for my query?"
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import env_loader
import os
import requests

# Manually hit SerpAPI to show all 20 results
key = os.environ["SERPAPI_KEY"]
query = os.environ.get("GMB_QUERY", "used cars in kokapet")

r = requests.get(
    "https://serpapi.com/search.json",
    params={"engine": "google_maps", "q": query, "api_key": key, "start": 0},
    timeout=30,
)
data = r.json()
results = data.get("local_results", [])

print("=" * 80)
print(f"Query: {query!r}")
print(f"Total results from SerpAPI: {len(results)}")
print("=" * 80)
print()

for i, p in enumerate(results, 1):
    title = p.get("title", "?")
    address = p.get("address", "")
    phone = p.get("phone")
    website = p.get("website")
    type_ids = p.get("type_ids") or []
    category = p.get("type") or p.get("category")

    print(f"--- Result {i}: {title} ---")
    print(f"  category:     {category}")
    print(f"  type_ids:     {type_ids}")
    print(f"  has_website:  {bool(website)} {website or ''}")
    print(f"  has_phone:    {bool(phone)} {phone or ''}")
    print(f"  address:      {address[:90]}")
    print()
