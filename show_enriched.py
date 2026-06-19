"""Show what an enriched lead looks like."""
import json
leads = json.load(open('data/leads.json'))

# Find an enriched lead (the first 5 in Madhapur should be enriched)
enriched_names = ['Mohans Motors', 'Famous Car Mart', 'Ur.Car', 'Moto Links', 'Budget Car']
for name in enriched_names:
    for l in leads:
        if l['business']['name'] == name:
            b = l['business']
            print(f'=== {name} ===')
            print(f'  business_kind  : {b.get("business_kind")}')
            print(f'  type_ids       : {b.get("type_ids")}')
            print(f'  country        : {b.get("country")}')
            print(f'  plus_code      : {b.get("plus_code")}')
            print(f'  open_state     : {b.get("open_state")}')
            print(f'  rating_summary : {b.get("rating_summary")}')
            print(f'  services       : {b.get("services")}')
            print(f'  offerings      : {b.get("offerings")}')
            print(f'  payments       : {b.get("payments")}')
            print(f'  photo_count    : {b.get("photo_count")} (gallery: {len(b.get("photo_gallery", []))})')
            print(f'  photo_latest   : {(b.get("photo_latest") or "")[:80]}')
            print(f'  photo_inside   : {(b.get("photo_inside") or "")[:80]}')
            print(f'  review_snippets: {len(b.get("review_snippets", []))}')
            for i, s in enumerate(b.get('review_snippets', [])[:3], 1):
                print(f'    {i}. "{s.get("snippet", "")[:80]}"')
            print(f'  popular_times  : {bool(b.get("popular_times"))} (current_day: {b.get("popular_current_day")})')
            print(f'  competitors    : {b.get("competitors")}')
            print(f'  enriched_at    : {b.get("enriched_at")}')
            print()
            break