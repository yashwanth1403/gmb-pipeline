"""Quick test: what type_ids values does SerpAPI return for various queries?"""
import sys
import json
import os
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import env_loader  # loads .env into os.environ
import requests

key = os.environ.get("SERPAPI_KEY", "")

queries = [
    "used cars in kokapet",
    "used car dealers in Hyderabad",
    "car dealers in Madhapur",
]

for q in queries:
    print("=" * 70)
    print(f"Query: {q!r}")
    print("=" * 70)
    r = requests.get(
        "https://serpapi.com/search.json",
        params={"engine": "google_maps", "q": q, "api_key": key, "start": 0},
        timeout=30,
    )
    data = r.json()
    results = data.get("local_results", [])
    print(f"Got {len(results)} results\n")

    seen = {}
    for p in results:
        title = p.get("title", "?")[:35]
        tids = tuple(p.get("type_ids") or [])
        cat = p.get("type") or p.get("category")
        key_str = (tids, cat)
        if key_str not in seen:
            seen[key_str] = []
        seen[key_str].append(title)

    print("Unique (type_ids, category) combinations seen:")
    for (tids, cat), titles in sorted(seen.items(), key=lambda x: -len(x[1])):
        print(f"  type_ids={list(tids)!r:55s} category={str(cat)!r:30s} count={len(titles)}")
        for t in titles[:3]:
            print(f"      e.g. {t}")
    print()
