"""
business_classifier.py — Robust classification of Google Maps business records
as used-car-dealer vs. everything-else.

The reality: SerpAPI's `type_ids` is INCONSISTENT:
  - Sometimes ['used_car_dealer']
  - Sometimes ['used_car_dealer', 'audi_dealer', 'car_dealer', ...]
  - Sometimes ['car_dealer'] ONLY (ambiguous: could be new OR used)
  - Sometimes ['car_dealer', 'auto_tag_agency', 'used_car_dealer'] (used_car_dealer is THIRD)

We need to look at MULTIPLE signals:
  1. type_ids — any one of them being 'used_car_dealer' or a *_dealer is a strong signal
  2. category — "Used car dealer" is the strongest text signal
  3. business name — contains "used", "pre-owned", "pre owned", "second hand"
  4. competitor/review snippets (when enriched)

Usage:
    from agents.business_classifier import classify
    is_used, confidence, reason = classify(lead)
"""

import re
from typing import Tuple

# type_ids values that STRONGLY indicate a used car business
# (from real SerpAPI data observed across 60+ queries)
USED_CAR_TYPE_IDS = {
    "used_car_dealer",
    "auto_auction",  # cars auctions are usually used
    "auto_broker",   # brokers typically deal in used
}

# type_ids values that indicate ANY car dealer (new or used)
CAR_DEALER_TYPE_IDS = {
    "car_dealer",
    "motor_vehicle_dealer",
    "audi_dealer", "bmw_dealer", "chevrolet_dealer", "dodge_dealer", "ford_dealer",
    "honda_dealer", "hyundai_dealer", "kia_dealer", "lexus_dealer",
    "mercedes_benz_dealer", "nissan_dealer", "skoda_dealer", "suzuki_dealer",
    "tata_dealer", "toyota_dealer", "volkswagen_dealer", "volvo_dealer",
    "jaguar_dealer", "land_rover_dealer", "mahindra_dealer", "mg_dealer",
    "renault_dealer", "jeep_dealer", "mitsubishi_dealer",
}

# type_ids values that indicate this is NOT a car dealer
NOT_CAR_DEALER_TYPE_IDS = {
    "auto_repair_shop", "auto_body_shop", "auto_painting", "auto_dent_removal_service",
    "car_repair", "car_wash", "mechanic", "tire_shop", "car_battery_store",
    "auto_parts_store", "auto_restoration_service",
    "gas_station", "parking", "car_rental_agency",
    "transportation_service", "moving_company", "moving_supply_store",
    "towing_service", "vehicle_inspection_station",
    "plant_nursery", "bakery", "restaurant", "cafe", "salon", "gym",
    "pharmacy", "hospital", "school", "hotel", "atm", "bank",
    # anything that doesn't start with one of our allow-list prefixes below
}

# Category strings (display names) that indicate used car dealer
USED_CAR_CATEGORIES = {
    "used car dealer",
}

# Category strings that indicate car dealer (could be new or used)
CAR_DEALER_CATEGORIES = {
    "car dealer",
    "motor vehicle dealer",
    "audi dealer", "bmw dealer", "chevrolet dealer", "honda dealer",
    "hyundai dealer", "kia dealer", "lexus dealer", "mercedes-benz dealer",
    "nissan dealer", "skoda dealer", "suzuki dealer", "tata dealer",
    "toyota dealer", "volkswagen dealer", "volvo dealer", "jaguar dealer",
    "land rover dealer", "mahindra dealer", "mg dealer", "renault dealer",
    "jeep dealer", "mitsubishi dealer",
    "auto auction", "auto broker",
}

# Name patterns that strongly suggest used car dealer
USED_CAR_NAME_PATTERNS = [
    r"\bused\b", r"\bpre[- ]owned\b", r"\bpre[- ]own\b",
    r"\bsecond[- ]hand\b", r"\bpre owned\b", r"\bsecond hand\b",
    r"\bpreowned\b", r"\b2nd hand\b", r"\b2nd[- ]hand\b",
    r"\bbuy[s]?\s*used\b", r"\bsell[s]?\s*used\b",
    r"\bvalue\s*car\b", r"\bbudget\s*car\b",
    r"\bcertified\s*pre[- ]owned\b",
]

# Name patterns that indicate new car dealer (NOT what we want)
NEW_CAR_DEALER_NAME_PATTERNS = [
    r"\bshowroom\b", r"\bnew\s*car[s]?\b", r"\bauthorized\b",
    r"\bnexa\b",  # Maruti's new-car brand
    r"^tata\s+motors\b", r"^maruti\s+suzuki\b", r"^hyundai\b",
    r"^honda\s+cars\b", r"^toyota\b",
    r"\bdealer\s*ship\b",
]

# compile patterns
_used_car_name_re = [re.compile(p, re.IGNORECASE) for p in USED_CAR_NAME_PATTERNS]
_new_car_name_re = [re.compile(p, re.IGNORECASE) for p in NEW_CAR_DEALER_NAME_PATTERNS]


def classify(lead: dict) -> Tuple[bool, float, str]:
    """
    Decide whether a lead is a used-car-dealer.

    Returns: (is_used_car_dealer, confidence_0_to_1, human_readable_reason)

    The confidence lets downstream code decide:
      - 0.95+ : definitely a used car dealer, build it
      - 0.50-0.95 : probably a used car dealer, build it but log the uncertainty
      - 0.20-0.50 : ambiguous, skip (user should review manually)
      - <0.20 : not a car dealer, definitely skip
    """
    b = lead.get("business", {})
    type_ids = b.get("type_ids") or []
    category = (b.get("category") or "").lower().strip()
    name = (b.get("name") or "").lower()

    # 1. Check the type_ids — any one being "used_car_dealer" is the strongest signal
    type_ids_set = {t.lower() for t in type_ids}
    if "used_car_dealer" in type_ids_set:
        return True, 0.99, f"type_ids contains 'used_car_dealer' ({type_ids})"

    if "auto_auction" in type_ids_set or "auto_broker" in type_ids_set:
        return True, 0.85, f"type_ids contains auto_auction/auto_broker ({type_ids})"

    # 2. Check the category text
    if category in USED_CAR_CATEGORIES:
        return True, 0.98, f"category is '{category}'"

    # 3. Check name patterns (this is the most reliable signal for ambiguous cases)
    has_used_name = any(p.search(name) for p in _used_car_name_re)
    has_new_name = any(p.search(name) for p in _new_car_name_re)

    if has_used_name and not has_new_name:
        return True, 0.90, f"name suggests used car dealer: {b.get('name')!r}"

    # 4. Check if it's a generic car_dealer (ambiguous)
    is_car_dealer_by_type = bool(type_ids_set & CAR_DEALER_TYPE_IDS)
    is_car_dealer_by_cat = category in CAR_DEALER_CATEGORIES

    if is_car_dealer_by_type or is_car_dealer_by_cat:
        # It's a car dealer but not explicitly used. Need more signals.
        if has_new_name:
            return False, 0.95, f"name suggests NEW car dealer: {b.get('name')!r}"
        # It's ambiguous — likely used (most car_dealer businesses in our
        # target market ARE used car dealers, since new car dealers usually
        # have a brand in their name)
        return True, 0.55, (
            f"ambiguous: type_ids={type_ids} category={category!r} name={b.get('name')!r}. "
            f"Marked as used (likely) — review manually if unsure."
        )

    # 5. Definitely NOT a car dealer
    if type_ids_set & NOT_CAR_DEALER_TYPE_IDS:
        return False, 0.99, f"type_ids indicates non-car-dealer: {type_ids}"

    # 6. Unknown — no type_ids at all
    if not type_ids_set and not category:
        return False, 0.30, "no type_ids or category — cannot classify"

    # 7. Fallback: type_ids and category are present but we don't recognize them
    return False, 0.40, f"unrecognized: type_ids={type_ids} category={category!r}"


# Backwards-compat shim — returns just the boolean
def is_used_car_dealer(lead: dict) -> bool:
    is_used, _, _ = classify(lead)
    return is_used
