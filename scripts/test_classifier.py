"""Test the business classifier against real SerpAPI results."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import env_loader
import os
import requests

from agents.business_classifier import classify

key = os.environ["SERPAPI_KEY"]

queries = [
    "used cars in kokapet",
    "used car dealers in Hyderabad",
    "car dealers in Madhapur",
]

# A few businesses I manually classified by name as ground truth
ground_truth = {
    "AUTO CAR": ("new-or-used", "name doesn't say used, generic car dealer"),
    "The car factory": ("used-likely", "sounds like used/refurb"),
    "The car choice": ("used-likely", "sounds like used"),
    "Our Cars": ("used-likely", "generic car dealer, likely used"),
    "NEXA (RKS Motors, Jubilee Hills, Hyderabad)": ("new", "NEXA = Maruti new car brand"),
    "Tata Motors Cars Showroom - Tejaswi Automobiles, Madhapur": ("new", "explicit 'Showroom'"),
    "Maruti Suzuki Gem Motors": ("new", "Maruti authorized"),
    "Vac's Pastries - KOKAPET": ("not-car", "bakery"),
    "PlantLove Garden Centre": ("not-car", "plant nursery"),
    "Sub5 Cars Habsiguda": ("used-likely", "Sub5 = Cars under 5yrs, pre-owned"),
    "Spinny Car Hub | D-Mart, Madhapur, ": ("used", "Spinny = used car platform"),
    "Cars24 - Buy, Sell, Finance Used Ca": ("used", "explicitly used in name"),
    "Car Timez": ("used-likely", "pre-owned brand"),
    "Value car mart": ("used-likely", "value car = pre-owned"),
    "Speeds Pre-Owned Cars | Hyderabad’s": ("used", "explicit 'pre-owned'"),
}

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

    for p in results:
        # Build a fake lead
        lead = {
            "place_id": p.get("place_id", "x"),
            "business": {
                "name": p.get("title"),
                "category": p.get("type") or p.get("category"),
                "type_ids": p.get("type_ids") or [],
            },
        }
        is_used, conf, reason = classify(lead)
        # Check against ground truth
        title = p.get("title", "")
        gt = ground_truth.get(title)
        gt_label = "?"
        if gt:
            gt_label = gt[0]
        icon = "✅" if (gt and (
            (gt_label == "used" and is_used and conf >= 0.9) or
            (gt_label == "not-car" and not is_used) or
            (gt_label == "new" and not is_used and conf >= 0.9) or
            (gt_label == "used-likely" and is_used) or
            (gt_label == "new-or-used" and conf < 0.9)
        )) else "  "
        print(f"  {icon} {'USED' if is_used else 'SKIP'} (conf={conf:.2f}) {title[:40]:40s}")
        print(f"      {reason}")
        if gt and gt_label == "new" and is_used:
            print(f"      ⚠️  GROUND TRUTH: NEW car dealer! We classified as used (WRONG)")
        if gt and gt_label == "not-car" and is_used:
            print(f"      ⚠️  GROUND TRUTH: NOT a car dealer! We classified as used (WRONG)")
    print()
