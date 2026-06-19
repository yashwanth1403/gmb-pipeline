"""
llm/response_parser.py
Validates the LLM response shape and fills in safe defaults for missing fields.
"""

REQUIRED_FIELDS = ["business_name", "tagline", "about_us", "why_choose_us", "hero_subhead", "cta_text"]
OPTIONAL_FIELDS = ["meta_description", "og_image_alt", "selected_reviews", "show_review_count_in_hero"]

DEFAULTS = {
    # No default for business_name — it must come from the lead itself if the LLM
    # doesn't supply one. Falls back to a 3-word cap on the raw GBP name.
    "tagline": "Quality used cars you can trust",
    "about_us": (
        "We are a local used car dealership committed to honest pricing and quality vehicles. "
        "Every car is inspected before listing.\n\n"
        "Visit us today — no pressure, no hidden fees."
    ),
    "why_choose_us": [
        "Quality inspected vehicles before every sale",
        "Transparent pricing with no hidden charges",
        "Friendly team ready to help you choose",
        "Convenient location with flexible payment options",
    ],
    "hero_subhead": "Browse our selection of quality pre-owned vehicles today",
    "cta_text": "Visit Our Showroom",
    "meta_description": "Quality used cars at fair prices. Visit us today.",
    "og_image_alt": "Our car dealership showroom",
    "show_review_count_in_hero": False,  # default to safe (off)
}


def _sanitize_business_name(raw: str) -> str:
    """
    Best-effort clean-up of a Google Business Profile name when the LLM
    didn't supply a cleaner one.

    Examples:
      "MUJEEB CARS (CHILKALGUDA) best second hand car dealer in Hyderabad"
          → "Mujeeb Cars"
      "PlantLove Garden Centre" → "PlantLove Garden Centre"
      "AUTO CAR" → "Auto Car"
      "Cars24 - Buy, Sell, Finance Used Cars in Bachupally, Hyderabad" → "Cars24"
    """
    import re
    if not raw:
        return ""
    s = raw.strip()
    # Drop everything from the first " in <city>" SEO phrase onward.
    m = re.search(r"\s+in\s+", s, re.IGNORECASE)
    if m:
        before_in = s[:m.start()].strip()
        if len(before_in.split()) >= 1:
            s = before_in
    # Drop parentheticals like "(CHILKALGUDA)", "(Madhapur)"
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s).strip()
    # Drop trailing SEO slop, repeated until stable.
    # IMPORTANT: this list is also used to chop off "Cars24 - Buy, Sell" → "Cars24".
    seo_words = (
        r"\b(best|second[- ]hand|pre[- ]owned|pre[- ]own|used|car dealer|"
        r"car dealers|dealer|dealership|used cars?|top|cheap|affordable|"
        r"trusted|good|quality|hyderabad|secunderabad|madhapur|kokapet|"
        r"jubliee[- ]?hills|kukatpally|dilsukhnagar|attapur|mehdipatnam|"
        r"and\s+sell|buy\b|sell\b|finance|in\s+(hyderabad|secunderabad|madhapur|kokapet|jubileehills|kukatpally))\b"
    )
    prev = None
    while prev != s:
        prev = s
        s = re.sub(rf"(\s+{seo_words})+[\s,;]*$", "", s, flags=re.IGNORECASE).strip()
    # Cut at " - " / " | " / " – " / " — " if the right side has SEO words
    for sep in [" - ", " | ", " – ", " — "]:
        if sep in s:
            left, right = s.split(sep, 1)
            if re.search(r"\b(buy|sell|finance|used|pre.?owned|second.?hand|car|dealer|dealership|hub|now|trade|mart|choice|multibrand|showroom)\b",
                         right, re.IGNORECASE):
                s = left.strip()
    # Also drop trailing "| <location>" and " - <location>" suffixes
    s = re.split(r"\s*[\|\-–]\s*(?=.*(?:hyderabad|madhapur|kokapet|secunderabad|kukatpally|jubliee|dilsukh|attapur|mehdipatnam))",
                 s, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    # Drop trailing commas/dashes
    s = s.rstrip(",-–| ").strip()
    # Title case ONLY if the name is all-upper or all-lower (preserves "PlantLove")
    if s.isupper() or s.islower():
        s = s.title()
    # Limit to 4 words max (nav bar friendly but not too aggressive)
    words = s.split()
    if len(words) > 4:
        s = " ".join(words[:4])
    return s


def validate_and_fill(llm_response: dict, lead: dict | None = None) -> dict:
    """
    Validate the LLM response and fill in defaults for any missing/empty fields.

    The optional `lead` argument lets us fall back to a sanitized version of
    the GBP name if the LLM didn't supply a clean `business_name`.
    """
    out = {}
    for field in REQUIRED_FIELDS + OPTIONAL_FIELDS:
        value = llm_response.get(field)
        if not value or (isinstance(value, list) and not value):
            value = DEFAULTS[field]
        out[field] = value

    # business_name: if the LLM didn't supply one, fall back to a sanitized
    # version of the raw GBP name from the lead
    if not llm_response.get("business_name") and lead:
        gbp_name = lead.get("business", {}).get("name", "")
        out["business_name"] = _sanitize_business_name(gbp_name)

    out["tagline"] = _truncate(out["tagline"], 100, DEFAULTS["tagline"])
    out["cta_text"] = _truncate(out["cta_text"], 40, DEFAULTS["cta_text"])
    out["meta_description"] = _truncate(out["meta_description"], 160, DEFAULTS["meta_description"])

    if not isinstance(out["why_choose_us"], list):
        out["why_choose_us"] = DEFAULTS["why_choose_us"]
    out["why_choose_us"] = (out["why_choose_us"] + DEFAULTS["why_choose_us"])[:4]

    # selected_reviews: keep non-empty strings only
    reviews = out.get("selected_reviews") or []
    if not isinstance(reviews, list):
        reviews = []
    out["selected_reviews"] = [r for r in reviews if isinstance(r, str) and r.strip()]

    # Coerce show_review_count_in_hero to bool
    out["show_review_count_in_hero"] = bool(out.get("show_review_count_in_hero"))

    return out


def _truncate(text: str, max_chars: int, fallback: str) -> str:
    if not text or len(text) > max_chars:
        return fallback
    return text
