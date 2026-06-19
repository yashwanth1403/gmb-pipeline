"""
react_builder.py
Maps a GBP lead + LLM output → dealer.json, writes it to the React project,
then runs `npm run build` to produce a deployable dist/.
"""
import json
import re
import subprocess
from pathlib import Path
from logo_generator import generate_logo_svg


# ── Helpers ───────────────────────────────────────────────────────────────────

def _digits(phone: str) -> str:
    return re.sub(r"\D", "", phone)


def _format_phone(raw: str) -> str:
    d = _digits(raw)
    last10 = d[-10:] if len(d) >= 10 else d
    if len(last10) == 10:
        return f"+91 {last10[:5]} {last10[5:]}"
    return raw


def _extract_city(address: str) -> str:
    parts = [p.strip() for p in address.split(",")]
    # Walk from the end, skip parts that are countries, states+pin, or pure numbers
    skip = {"india", "telangana", "maharashtra", "karnataka", "tamil nadu", "gujarat", "rajasthan"}
    for part in reversed(parts):
        clean = re.sub(r"\d+", "", part).strip()
        if clean and clean.lower() not in skip and not re.fullmatch(r"[\d\s]+", part):
            return clean
    return parts[-1] if parts else "India"


def _maps_embed(lat: float, lng: float) -> str:
    return f"https://maps.google.com/maps?q={lat},{lng}&z=15&output=embed"


def _convert_hours(hours) -> list:
    """
    Normalize Google Maps hours into the React template's expected format.

    Handles THREE input shapes (SerpAPI is inconsistent):
      1. List of single-key dicts: [{"monday": "9 AM–8 PM"}, {"tuesday": "..."}, ...]
         (returned by SerpAPI's place_id lookup / enrichment)
      2. Single dict: {"monday": "9 AM–8 PM", "tuesday": "...", ...}
         (returned by SerpAPI's local search results)
      3. None / empty: returns []

    Output: [{"days": "Mon", "hours": "9 AM–8 PM"}, ...] — always 7 entries, one per day.
    """
    abbrev = {
        "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
        "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun",
    }
    if not hours:
        return []

    # Normalize to a single {day: hours} dict regardless of input shape
    flat: dict = {}
    if isinstance(hours, dict):
        flat = hours
    elif isinstance(hours, list):
        for item in hours:
            if isinstance(item, dict):
                flat.update(item)
            elif isinstance(item, str):
                # ["Mon 9-5", "Tue 9-5"] — best-effort: skip
                continue

    # Build the React-template list. Preserve the GBP order Mon→Sun if possible.
    canonical_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    result = []
    for day in canonical_order:
        # Match case-insensitively
        time = None
        for k, v in flat.items():
            if k.lower() == day:
                time = v
                break
        if time is not None:
            result.append({"days": abbrev[day], "hours": time})
    return result


def _testimonials_from_selected(selected_reviews: list, city: str) -> list:
    """Build testimonials.json from LLM-selected review strings."""
    return [
        {
            "name": "Google Reviewer",
            "location": city,
            "review": review.strip().strip('"'),
            "car": "Verified Purchase",
            "rating": 5,
        }
        for review in selected_reviews
        if review.strip()
    ]


# ── Main builder ──────────────────────────────────────────────────────────────

def build_dealer_json(lead: dict, llm: dict) -> dict:
    """Produce the dealer.json dict from GBP lead + LLM content."""
    b = lead["business"]

    city      = _extract_city(b.get("address", ""))
    raw_phone = b.get("phone", "")
    d         = _digits(raw_phone)
    phone_10  = d[-10:] if len(d) >= 10 else d

    lat, lng  = b.get("lat"), b.get("lng")
    embed_url = _maps_embed(lat, lng) if lat and lng else ""

    hours = _convert_hours(b.get("hours", []))
    if not hours:
        hours = [
            {"days": "Mon – Sat", "hours": "10:00 AM – 8:00 PM"},
            {"days": "Sunday",    "hours": "11:00 AM – 6:00 PM"},
        ]

    # Story paragraphs from LLM about_us (split on double newline)
    about_raw  = llm.get("about_us", "")
    paragraphs = [p.strip() for p in about_raw.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [about_raw] if about_raw else [
            f"{b['name']} is a trusted used car dealer in {city}. Visit us today."
        ]

    review_count = b.get("review_count") or 0
    rating       = b.get("rating") or 4.5

    # The LLM decides whether the review count is worth highlighting.
    # Default safe: hide it (LLM only enables it if review_count >= ~20).
    show_review_count = bool(llm.get("show_review_count_in_hero", False))

    # When the LLM says "show it", reference it. Otherwise use a generic trust signal.
    if show_review_count and review_count >= 20:
        review_label_text = f"{review_count}+ Google reviews"
    else:
        review_label_text = "Verified Google reviews"

    stats = [
        {
            "metric": f"{review_count}+" if show_review_count and review_count >= 20 else "100%",
            "label":  "Happy Customers" if show_review_count else "Verified",
            "desc":   review_label_text,
        },
        {
            "metric": f"{rating}★",
            "label":  f"Trusted {city} Dealer",
            "desc":   "Consistently rated by customers",
        },
        {
            "metric": "2 Days",
            "label":  "Avg. Loan Approval",
            "desc":   "Quick approvals via partner banks",
        },
        {
            "metric": "10+",
            "label":  "Cars Available",
            "desc":   "Fresh inventory every week",
        },
    ]

    # Gallery: use GBP photos, skip street view and non-photo thumbnails
    skip_domains = ("streetviewpixels-pa.googleapis.com", "maps.googleapis.com/maps/api/streetview")
    gallery = []
    for img in b.get("photo_gallery", []):
        src = img.get("thumbnail", "")
        if src and not any(d in src for d in skip_domains):
            gallery.append({"src": src, "alt": f"{b['name']} {img.get('category', 'photo')}"})

    # Use the LLM-extracted CLEAN name for the navbar / brand display.
    # Fall back to a sanitized version of the GBP name if the LLM didn't supply one.
    clean_name = llm.get("business_name") or b.get("name", "Car Dealer")
    # Last-resort: strip SEO slop if the LLM value still has it
    from llm.response_parser import _sanitize_business_name
    clean_name = _sanitize_business_name(clean_name) or clean_name

    return {
        "name":      clean_name,
        "city":      city,
        "logoPath":  "",
        "emblemPath":"",
        "contact": {
            "phone":          phone_10,
            "phoneFormatted": _format_phone(raw_phone),
            "email":          "",
            "address":        b.get("address", ""),
            "mapsUrl":        b.get("gbp_link", ""),
            "mapsEmbedUrl":   embed_url,
            "instagram":      "",
        },
        "hours": hours,
        "hero": {
            "headline":          llm.get("tagline",     f"Trusted Pre-Owned Cars in {city}"),
            "subheadline":       llm.get("hero_subhead","Budget-friendly. Verified. Ready to Drive."),
            "backgroundDesktop": "/hero-bg.jpg",
            "backgroundMobile":  "/hero-bg.jpg",
        },
        "story": {
            "headline":   f"Born to make car buying simple in {city}",
            "paragraphs": paragraphs,
        },
        "stats": stats,
        "rating": {
            "score":          rating,
            "outOf":          5,
            "totalCustomers": (
                f"{review_count}+" if show_review_count and review_count >= 20
                else "Trusted local dealer"
            ),
            "tagline":        f"Trusted by {city} car buyers",
        },
        "featuredCarIds": ["1", "2", "3", "4"],
        "galleryImages":  gallery,
    }


def write_json_files(lead: dict, llm: dict, react_dir: Path) -> None:
    """Write dealer.json and testimonials.json into the React project."""
    b = lead["business"]

    # ── dealer.json ───────────────────────────────────────────
    dealer = build_dealer_json(lead, llm)

    # Generate SVG logo and set emblemPath
    try:
        emblem_path = generate_logo_svg(b["name"], react_dir)
        dealer["emblemPath"] = emblem_path
    except Exception as e:
        print(f"  ⚠️  logo generation skipped: {e}")

    dest   = react_dir / "src" / "config" / "dealer.json"
    dest.write_text(json.dumps(dealer, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✅ dealer.json → {dest}")

    # ── testimonials.json ─────────────────────────────────────
    city         = dealer["city"]
    testimonials = _testimonials_from_selected(llm.get("selected_reviews", []), city)

    tdest = react_dir / "src" / "data" / "testimonials.json"
    tdest.write_text(json.dumps(testimonials, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✅ testimonials.json → {tdest}")


def vite_build(react_dir: Path) -> Path:
    """
    Run `npm run build` and return the dist/ path.

    Note: we deliberately call `_run_subprocess` from agents.site_builder
    so Windows PATH issues with npm/node are handled. Import lazily to avoid
    circular deps.
    """
    print(f"  🔨 vite build in {react_dir} ...")
    try:
        from agents.site_builder import _run_subprocess
        result = _run_subprocess(["npm", "run", "build"], cwd=react_dir, timeout=300)
    except ImportError:
        # Fall back if called standalone (e.g. from the generator's own CLI)
        import subprocess
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=react_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )

    if result.returncode != 0:
        print(result.stdout[-2000:] if result.stdout else "")
        print(result.stderr[-2000:] if result.stderr else "")
        raise RuntimeError("vite build failed — see output above")
    dist = react_dir / "dist"
    print(f"  ✅ dist → {dist}")
    return dist
