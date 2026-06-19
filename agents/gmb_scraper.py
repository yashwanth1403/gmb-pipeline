"""
gmb_scraper.py — Agent 1: GMB Lead Finder (SerpAPI backend)

What it does:
    1. Takes a search query (location is OPTIONAL and baked into the query string)
    2. Hits SerpAPI's Google Maps endpoint, paginating through all available
       results (the API-side cap defaults to 20, i.e. one full page). We
       intentionally do NOT pass the user-facing max_results cap to SerpAPI —
       the cap is applied after filtering (no-website + has-phone) so we
       don't end up with 0 saved leads when filters reject most results.
    3. (Optional) Enriches each lead with FULL place details via place_id lookup:
         - photos (All / Latest / Videos / Inside / By owner)
         - services (Delivery, In-store shopping, etc.)
         - offerings (Used goods, etc.)
         - payments (Credit cards, etc.)
         - hours + live open_state
         - rating_summary (5-star breakdown)
         - user review snippets
         - popular_times (hourly busyness)
         - plus_code
    4. Filters out businesses that ALREADY have a website
    5. Optionally requires a phone number (needed for outreach)
    6. Caps the saved list at SCRAPE_MAX_RESULTS (or --max)
    7. Saves each lead to data/leads.json (deduped by place_id)
    8. Updates data/queue.json so the orchestrator knows what's next

Usage:
    python -m agents.gmb_scraper --query "car dealers in Andheri West" --max 40
    python -m agents.gmb_scraper --query "salons" --location "Pune, India" --max 20
    python -m agents.gmb_scraper --query "used car dealers in Madhapur" --enrich   # full data
    python -m agents.gmb_scraper --query "used car dealers in Madhapur" --enrich-limit 10
"""
from __future__ import annotations
import os
import sys
import time
from pathlib import Path
from typing import Any

# Make sure env vars are loaded BEFORE we import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa: F401  (side-effect: loads .env)

from serpapi import GoogleSearch  # official SerpAPI Python SDK

from config import (
    SERPAPI_KEY,
    GMB_QUERY,
    GMB_LOCATION,
    SCRAPE_MAX_RESULTS,
    SCRAPE_KINDS,
    REQUIRE_PHONE,
)
from agents.base_agent import BaseAgent, now_iso


class GMBScraper(BaseAgent):
    name = "gmb_scraper"

    # ---------- public API ----------
    def run(self, query: str | None = None, location: str | None = None,
            max_results: int | None = None,
            enrich: bool = False, enrich_limit: int | None = None):
        """
        query    : REQUIRED-ish (falls back to GMB_QUERY in .env, else errors out).
                   Pass the FULL search string here, e.g. "car dealers in Andheri West".
                   Location is baked into the query, so SerpAPI does the geo filtering for us.
        location : OPTIONAL. Only set if you want SerpAPI to do radius-based filtering
                   around a city. If omitted, no `location` param is sent at all.
        max_results : OPTIONAL cap on how many leads to SAVE (post-filter). We ALWAYS
                   fetch the full first page from SerpAPI (~20) regardless of this cap,
                   so that filter rejections don't leave us with 0 leads to save.
                   Defaults to SCRAPE_MAX_RESULTS from .env.
        enrich   : If True, after the search pass we call SerpAPI's `place_id` lookup
                   on each lead for full details (photos, services, popular_times, etc.).
                   Costs N extra API calls per N kept leads — use sparingly on free tier.
        enrich_limit : Cap enrichment to this many leads (e.g. 10) to control quota.
        """
        query = query or GMB_QUERY
        # location stays None unless explicitly provided (CLI flag OR .env)
        location = location if location else GMB_LOCATION or None
        max_results = max_results or SCRAPE_MAX_RESULTS

        if not query:
            self.log.error("No query provided. Pass --query or set GMB_QUERY in .env.")
            sys.exit(1)
        if not SERPAPI_KEY:
            self.log.error("SERPAPI_KEY missing. Put it in .env (see .env.example).")
            sys.exit(1)

        loc_msg = f"location='{location}'" if location else "location=(none, geo from query)"
        self.log.info(f"START  query='{query}' {loc_msg} max={max_results} enrich={enrich}")
        self.log.info(
            f"        (fetching 1 page from SerpAPI; will keep up to {max_results} "
            f"after filters — see SCRAPE_MAX_RESULTS in .env)"
        )

        # Fetch one full page from SerpAPI (20 results). The `max_results` cap
        # is applied AFTER filtering, not at the API call, so we don't get
        # stuck with 0 saved leads if all results fail the no-website filter.
        raw_results = self._fetch_all(query, location, fetch_cap=20)
        self.log.info(f"SerpAPI returned {len(raw_results)} raw results")

        # Resolve the business_kind filter. "any" disables the filter; otherwise
        # we accept a comma-separated list. This is the single source of truth
        # for "what kinds of businesses is this pipeline even looking for".
        #
        # Defense in depth: we ALSO run every candidate through the robust
        # business_classifier (which looks at all type_ids + name + category).
        # A lead that slips through the simple filter (e.g. has type_ids=
        # ['car_dealer'] only) will be caught by the classifier.
        kinds = None
        if SCRAPE_KINDS and SCRAPE_KINDS.strip().lower() != "any":
            kinds = {k.strip() for k in SCRAPE_KINDS.split(",") if k.strip()}
            self.log.info(f"Filter: only keeping business_kinds in {kinds}")
        else:
            self.log.info("Filter: business_kind filter disabled (SCRAPE_KINDS=any)")

        # Pass 1: collect candidates (with basic data from search results)
        from agents.business_classifier import classify as classify_business
        candidates: list[dict] = []
        rejected_kinds: dict[str, int] = {}
        classifier_rejected: list[tuple[str, str]] = []  # (name, reason)
        for r in raw_results:
            lead = self._normalize(r)
            if not lead:
                continue
            if lead["business"].get("has_website"):
                continue
            if REQUIRE_PHONE and not lead["business"].get("phone"):
                continue

            # Filter 1: simple business_kind check (cheap, fails fast)
            if kinds is not None:
                lead_kind = lead["business"].get("business_kind")
                if lead_kind not in kinds:
                    rejected_kinds[lead_kind or "(none)"] = rejected_kinds.get(lead_kind or "(none)", 0) + 1
                    continue

            # Filter 2: robust classifier (looks at ALL type_ids + name + category)
            is_used, confidence, reason = classify_business(lead)
            if not is_used:
                classifier_rejected.append((lead["business"].get("name", "?"), reason))
                continue

            # Annotate the lead with classification result so downstream knows
            lead["business"]["business_kind"] = "used_car_dealer"  # canonical
            lead["business"]["_classification"] = {
                "is_used_car_dealer": is_used,
                "confidence": confidence,
                "reason": reason,
            }
            candidates.append(lead)

        if rejected_kinds:
            self.log.info(
                f"Rejected by business_kind filter: {rejected_kinds}"
            )
        if classifier_rejected:
            self.log.info(
                f"Rejected by business_classifier ({len(classifier_rejected)} leads):"
            )
            for name, reason in classifier_rejected[:10]:
                self.log.info(f"  - {name}: {reason}")
            if len(classifier_rejected) > 10:
                self.log.info(f"  ... and {len(classifier_rejected) - 10} more")

        self.log.info(f"Candidates after filters: {len(candidates)} (of {len(raw_results)} raw)")

        # Apply the storage cap here, NOT at the API call. This way if you
        # have 20 raw results and 15 get filtered out, you still get 5 saved
        # — instead of the old behavior where you'd get 0.
        if len(candidates) > max_results:
            self.log.info(
                f"Limiting to {max_results} of {len(candidates)} candidates "
                f"(per SCRAPE_MAX_RESULTS / --max)"
            )
            candidates = candidates[:max_results]

        # Pass 2 (optional): enrich each candidate with full place details
        if enrich and candidates:
            cap = enrich_limit or len(candidates)
            self.log.info(f"Enriching {min(cap, len(candidates))} leads with full place details...")
            for i, lead in enumerate(candidates[:cap], 1):
                self.log.info(f"  [{i}/{cap}] enriching {lead['business']['name']}")
                details = self._fetch_place_details(lead["place_id"])
                if details:
                    lead = self._merge_details(lead, details)
                else:
                    self.log.warning(f"    no details returned for {lead['place_id']}")
                # Save incrementally so a crash mid-enrich doesn't lose work
                self.upsert_lead(lead)
                self.set_queue(lead["place_id"], stage="scrape", status="done")
                time.sleep(0.5)  # be polite
            # Save any remaining candidates (above the cap) with just basic data
            for lead in candidates[cap:]:
                self.upsert_lead(lead)
                self.set_queue(lead["place_id"], stage="scrape", status="done")
        else:
            for lead in candidates:
                self.upsert_lead(lead)
                self.set_queue(lead["place_id"], stage="scrape", status="done")

        self.log.info(f"DONE   saved={len(candidates)} (no-website + has-phone)")
        return len(candidates)

    # ---------- enrichment ----------
    def _fetch_place_details(self, place_id: str) -> dict | None:
        """
        Second-pass SerpAPI call: look up a single place by place_id for FULL details.
        Returns the `place_results` dict (or None on failure).
        """
        params = {"engine": "google_maps", "place_id": place_id, "api_key": SERPAPI_KEY}
        try:
            data = GoogleSearch(params).get_dict()
        except Exception as e:
            self.log.warning(f"place_id lookup failed for {place_id}: {e}")
            return None
        if data.get("error"):
            self.log.warning(f"place_id lookup error for {place_id}: {data['error']}")
            return None
        return data.get("place_results")

    def _merge_details(self, lead: dict, details: dict) -> dict:
        """
        Merge the rich `place_results` into our lead's business dict.
        Anything we already have wins only if our value is truthy
        (so enrichment upgrades sparse fields but never overwrites a phone we already have).
        """
        b = lead["business"]

        # ---- Type & category ----
        types = details.get("type") or []
        if isinstance(types, list) and types:
            b["category"] = types[0] if not b.get("category") else b["category"]
            b["all_types"] = types
        type_ids = details.get("type_ids") or []
        if type_ids:
            b["type_ids"] = type_ids
            b["business_kind"] = type_ids[0]  # e.g. "used_car_dealer" — for template picking

        # ---- Location helpers ----
        if details.get("country"):
            b["country"] = details["country"]
        if details.get("plus_code"):
            b["plus_code"] = details["plus_code"]

        # ---- Hours ----
        if details.get("hours"):
            b["hours"] = details["hours"]
        if details.get("open_state"):
            b["open_state"] = details["open_state"]  # e.g. "Closed · Opens 10 AM"

        # ---- Rating breakdown ----
        if details.get("rating_summary"):
            b["rating_summary"] = details["rating_summary"]  # [{stars:1,amount:79}, ...]

        # ---- Services / Offerings / Payments ----
        # SerpAPI puts them in two places: structured `service_options` and the looser `extensions[]`.
        b["service_options"] = details.get("service_options") or {}
        b["extensions"] = details.get("extensions") or []
        # Flatten the extensions into easy-to-use lists
        flat_services, flat_offerings, flat_payments = [], [], []
        for ext in (details.get("extensions") or []):
            if "service_options" in ext: flat_services.extend(ext["service_options"])
            if "offerings" in ext:       flat_offerings.extend(ext["offerings"])
            if "payments" in ext:        flat_payments.extend(ext["payments"])
        if flat_services:  b["services"]  = flat_services
        if flat_offerings: b["offerings"] = flat_offerings
        if flat_payments:  b["payments"]  = flat_payments

        # ---- Photos (categorized) ----
        # SerpAPI returns photos grouped by category: All / Latest / Videos / Inside / By owner / Street View
        photos = details.get("images") or []
        if photos:
            b["photo_gallery"] = [
                {
                    "category": img.get("title"),
                    "last_updated": img.get("last_updated"),
                    "thumbnail": img.get("thumbnail"),
                }
                for img in photos
            ]
            # Convenience: just the latest & the inside (most useful for a website hero)
            by_cat = {img.get("title"): img for img in photos}
            b["photo_latest"]  = by_cat.get("Latest", {}).get("thumbnail")
            b["photo_inside"]  = by_cat.get("Inside", {}).get("thumbnail")
            b["photo_exterior"] = by_cat.get("All", {}).get("thumbnail") or b.get("thumbnail")
            b["photo_count"] = len(photos)

        # ---- Reviews (snippets) ----
        ur = details.get("user_reviews") or {}
        if ur.get("summary"):
            b["review_snippets"] = ur["summary"]  # list of {snippet, thumbnail}

        # ---- Popular times (hourly busyness) ----
        pt = details.get("popular_times") or {}
        if pt:
            b["popular_times"] = pt
            b["popular_current_day"] = pt.get("current_day")

        # ---- Cross-link helpers ----
        if details.get("reviews_link"):
            b["reviews_link"] = details["reviews_link"]
        if details.get("photos_link"):
            b["photos_link"] = details["photos_link"]
        if details.get("data_id"):
            b["data_id"] = details["data_id"]
        if details.get("data_cid"):
            b["data_cid"] = details["data_cid"]

        # ---- Competitor discovery (people_also_search_for) ----
        pasf = details.get("people_also_search_for") or []
        if pasf:
            comp_titles = []
            for entry in pasf:
                for sub in (entry.get("local_results") or []):
                    t = sub.get("title")
                    if t:
                        comp_titles.append(t)
            if comp_titles:
                b["competitors"] = comp_titles[:5]

        b["enriched_at"] = now_iso()
        return lead

    # ---------- internals ----------
    def _fetch_all(self, query: str, location: str | None, fetch_cap: int = 20) -> list[dict]:
        """
        SerpAPI's Google Maps engine returns 20 results per page.
        We loop with `start` (offset) until we have `fetch_cap` results or
        SerpAPI runs out.

        If `location` is None, we DON'T pass it at all — and therefore don't need `z` either.
        SerpAPI will then take the location from inside the `query` string
        (e.g. "car dealers in Andheri West" → resolves to Andheri West on its own).

        Note: `fetch_cap` is the API-side limit. The user-facing `max_results`
        cap is applied AFTER filtering (see `run`), not here. This way, if
        many results get filtered out, we still have enough survivors.
        """
        results: list[dict] = []
        start = 0
        per_page = 20

        while len(results) < fetch_cap:
            params = {
                "engine": "google_maps",
                "q": query,
                "type": "search",
                "start": start,
                "api_key": SERPAPI_KEY,
            }
            # Only add location + zoom when the user explicitly asked for them
            if location:
                params["location"] = location
                # SerpAPI REQUIRES either `z` (zoom 0-21) or `m` (radius in meters)
                # when you supply `location`. z=13 ≈ city-level radius.
                params["z"] = 13

            self.log.info(f"GET    start={start}")
            try:
                search = GoogleSearch(params)
                data = search.get_dict()
            except Exception as e:
                self.log.error(f"SerpAPI call failed: {e}")
                break

            # SerpAPI returns `error` key on bad params / quota / etc — surface it loudly
            if "error" in data and not data.get("local_results"):
                self.log.error(f"SerpAPI error: {data['error']}")
                break

            page = data.get("local_results", []) or []
            if not page:
                self.log.info("No more results from SerpAPI.")
                break

            results.extend(page)

            # If SerpAPI returns fewer than a full page, we've hit the end.
            if len(page) < per_page:
                break

            start += per_page
            time.sleep(1.0)  # be polite

        return results[:fetch_cap]

    def _normalize(self, raw: dict[str, Any]) -> dict | None:
        """
        Convert SerpAPI's verbose GMB shape into OUR clean lead schema.
        Returns None if the result is too sparse to be useful.
        """
        # SerpAPI uses `place_id` for data_id; we keep that as our key.
        place_id = raw.get("place_id") or raw.get("data_id") or raw.get("data_cid")
        if not place_id:
            return None

        # `website` is a string URL when present, None otherwise
        website = raw.get("website")
        has_website = bool(website)

        # Phone comes through as a string like "+91 98XXX XXXXX" — keep as-is
        phone = raw.get("phone")

        # Address can be in multiple fields depending on locale
        address = (
            raw.get("address")
            or raw.get("full_address")
            or ", ".join(filter(None, [raw.get("street"), raw.get("city"), raw.get("state")]))
        )

        # Google Business Profile (GBP) verification link.
        # Prefer SerpAPI's own `link` field when present (most reliable).
        # Fall back to constructing the standard GBP URL from place_id.
        serpapi_link = raw.get("link")
        gbp_link = serpapi_link or f"https://www.google.com/maps/place/?q=place_id:{place_id}"

        # SerpAPI's search results sometimes include `type` as a STRING, sometimes as a LIST,
        # sometimes missing. Be defensive.
        raw_type = raw.get("type")
        if isinstance(raw_type, list):
            type_list = raw_type
            type_str = raw_type[0] if raw_type else None
        elif isinstance(raw_type, str):
            type_list = [raw_type]
            type_str = raw_type
        else:
            type_list = []
            type_str = raw.get("category")

        # `type_ids` is a list of slugs like ["used_car_dealer"] — we use the FIRST as
        # `business_kind` to pick a website template downstream.
        type_ids = raw.get("type_ids") or []
        business_kind = type_ids[0] if type_ids else None

        lead = {
            "lead_id": place_id,         # alias so other agents don't need to know place_id
            "place_id": place_id,
            "source": "serpapi",
            "scraped_at": now_iso(),
            "business": {
                "name": raw.get("title") or raw.get("name"),
                "category": type_str,
                "all_types": type_list,
                "type_ids": type_ids,
                "business_kind": business_kind,
                "address": address,
                "phone": phone,
                "country": raw.get("country"),
                "plus_code": raw.get("plus_code"),
                "rating": raw.get("rating"),
                "review_count": raw.get("reviews"),
                "rating_summary": raw.get("rating_summary") or [],
                "hours": raw.get("operating_hours") or raw.get("hours"),
                "open_state": raw.get("open_state"),
                "photos": raw.get("photos") or [],
                "photo_gallery": [],
                "thumbnail": raw.get("thumbnail"),
                "photo_latest": None,
                "photo_inside": None,
                "photo_exterior": raw.get("thumbnail"),
                "photo_count": len(raw.get("photos") or []),
                "lat": (raw.get("gps_coordinates") or {}).get("latitude"),
                "lng": (raw.get("gps_coordinates") or {}).get("longitude"),
                "website": website,
                "has_website": has_website,
                "place_id": place_id,
                "gbp_link": gbp_link,    # public Google Business Profile URL for verification
                "data_id": raw.get("data_id"),
                "data_cid": raw.get("data_cid"),
            },
            "status": "scraped",
            "attempts": {"scrape": 1, "build": 0, "outreach": 0},
        }

        # Drop leads where we couldn't even get a name — useless for outreach
        if not lead["business"]["name"]:
            return None

        return lead


# ---------- CLI entrypoint ----------
def main():
    import argparse
    p = argparse.ArgumentParser(description="GMB Lead Finder (SerpAPI)")
    p.add_argument("--query", default=None, help="search string, e.g. 'car dealers in Andheri West' (geo is baked into query)")
    p.add_argument("--location", default=None, help="optional: city for SerpAPI radius filter, e.g. 'Mumbai, India'")
    p.add_argument("--max", dest="max_results", type=int, default=None, help="max leads to fetch")
    p.add_argument("--enrich", action="store_true", help="after search, fetch full place details (photos, services, popular_times) for each lead")
    p.add_argument("--enrich-limit", type=int, default=None, help="cap enrichment to first N leads (to control API quota)")
    args = p.parse_args()

    scraper = GMBScraper()
    scraper.run(query=args.query, location=args.location,
                max_results=args.max_results,
                enrich=args.enrich, enrich_limit=args.enrich_limit)


if __name__ == "__main__":
    main()