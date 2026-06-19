"""
llm/prompt_builder.py
Builds the OpenAI chat messages from a lead dict.
"""
import json
import re

# Bump this whenever the prompt changes. The LLM cache key includes this
# version, so a bump automatically invalidates every cached response and
# forces a fresh OpenAI call next time the pipeline runs.
PROMPT_VERSION = "2"  # v2: added business_name, show_review_count_in_hero, name-cleanup rules

SYSTEM_PROMPT = """You are a website copywriter for small local businesses, specifically used car dealerships. You write honest, peer-to-peer, trustworthy copy. You base every claim STRICTLY on the data provided; if something isn't in the data, you don't make it up. You write in short sentences, scannable format, friendly tone, never salesy.

Rules:
- DO NOT invent years of experience, awards, certifications, or claims not in the data
- DO reference actual review count and rating (e.g. "471+ Google reviews")
- DO mention specific services they offer (delivery, buying used cars, etc.)
- DO keep tone peer-to-peer, not corporate
- In tagline and hero_subhead use ONLY the city name — never the area, locality, or state
- DO NOT use words like: premier, best-in-class, unparalleled, world-class, top-notch, cutting-edge
- Return ONLY valid JSON matching the requested schema
- Use plain English, no jargon, no hashtags, no emojis

About the business name (CRITICAL):
- Google Business Profile names often have extra location/keyword stuff appended
  (e.g. "MUJEEB CARS (CHILKALGUDA) best second hand car dealer in Hyderabad")
- Extract a CLEAN short brand name suitable for a website navbar (max 3 words).
  Example: "MUJEEB CARS" or "Mujeeb Cars" — NOT the full GBP name.
- Drop trailing parentheticals like "(CHILKALGUDA)", drop trailing SEO keyword
  slop like "best second hand car dealer in Hyderabad".
- If the name is already short and clean, return it as-is.

About the review count (CRITICAL):
- If the business has fewer than ~20 reviews, do NOT highlight the count in the
  tagline or hero_subhead. Saying "11+ reviews" can look weak.
- If the count is ≥20, you may reference it (e.g. "Trusted by 100+ Hyderabad buyers").
- The `show_review_count_in_hero` field lets the template know your decision.
"""

_SKIP_STATE = {"india", "telangana", "maharashtra", "karnataka", "tamil nadu",
               "gujarat", "rajasthan", "andhra pradesh", "kerala", "punjab",
               "haryana", "west bengal", "odisha", "madhya pradesh"}


def _extract_city(address: str) -> str:
    parts = [p.strip() for p in address.split(",")]
    for part in reversed(parts):
        clean = re.sub(r"\d+", "", part).strip()
        if clean and clean.lower() not in _SKIP_STATE and not re.fullmatch(r"[\d\s]+", part):
            return clean
    return parts[-1] if parts else "India"


def build_user_prompt(lead: dict) -> str:
    b    = lead["business"]
    city = _extract_city(b.get("address", ""))

    reviews_text = ""
    for i, r in enumerate(b.get("review_snippets", [])[:5], 1):
        reviews_text += f'  {i}. "{r.get("snippet", "")}"\n'

    competitors_text = ", ".join(b.get("competitors", [])[:5]) or "other dealers in the area"

    return f"""Generate website content for this used car dealership.

BUSINESS:
- Name: {b.get("name", "Unknown")}
- Category: {b.get("category", "Used car dealer")}
- City: {city}
- Phone: {b.get("phone", "")}
- Rating: {b.get("rating", "N/A")} stars from {b.get("review_count", 0)} Google reviews

SERVICES THEY OFFER:
{json.dumps(b.get("services", []), indent=2)}

WHAT THEY OFFER (sell / buy / etc.):
{json.dumps(b.get("offerings", []), indent=2)}

PAYMENT METHODS ACCEPTED:
{json.dumps(b.get("payments", []), indent=2)}

CUSTOMER REVIEWS (select the best 1–3 that sound genuine and positive):
{reviews_text or "  (no reviews provided)"}

NEARBY COMPETITORS (do NOT name them):
{competitors_text}

Return ONLY this exact JSON structure:
{{
  "business_name": "<CLEAN short brand name, max 3 words, drop trailing location/SEO slop from the GBP name>",
  "tagline": "<max 10 words, city name only — e.g. 'Trusted used cars in {city}'>",
  "about_us": "<2 paragraphs separated by \\n\\n, 60–90 words, friendly, mention {city} and actual rating>",
  "why_choose_us": [
    "<bullet 1, max 15 words, grounded in actual services or rating>",
    "<bullet 2, max 15 words>",
    "<bullet 3, max 15 words>",
    "<bullet 4, max 15 words>"
  ],
  "hero_subhead": "<max 15 words, use only city name — e.g. 'Quality used cars in {city}, backed by {b.get("review_count", 0)}+ reviews'. If review_count is low, drop the review mention.>",
  "show_review_count_in_hero": <true if review_count >= 20, false otherwise>,
  "selected_reviews": [
    "<best review snippet verbatim, or empty string if none>",
    "<second best, or omit>",
    "<third best, or omit>"
  ],
  "cta_text": "<max 4 words, button label>",
  "meta_description": "<max 155 chars, SEO-friendly, includes {city}>"
}}
"""


def build_messages(lead: dict) -> list:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": build_user_prompt(lead)},
    ]
