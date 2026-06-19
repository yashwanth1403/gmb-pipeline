"""
base_agent.py
Shared utilities for all agents in the GMB pipeline.
- Structured JSON logging
- Safe JSON file read/write (atomic)
- Retry decorator with exponential backoff
- Consistent agent interface
"""
from __future__ import annotations
import json
import logging
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional
from uuid import uuid4

# ---------- paths ----------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import LOG_FILE, LEADS_FILE, QUEUE_FILE, BUILT_SITES_FILE  # noqa: E402

# ---------- logging ----------
# Each agent gets its own logger; logs go to BOTH console and logs/pipeline.log
# Format: ISO timestamp | level | agent_name | message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-15s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


# ---------- JSON I/O ----------
def load_json(path: Path, default: Any = None) -> Any:
    """Read JSON from disk; return `default` if file missing or corrupt."""
    if not path.exists():
        return default if default is not None else {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log = get_logger("base.json")
        log.warning(f"Corrupt JSON at {path}: {e}; returning default")
        return default if default is not None else {}


def save_json(path: Path, data: Any) -> None:
    """Atomic write: write to .tmp then rename, so a crash never leaves half-written JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_city(address: str) -> str:
    """
    Pull the CITY out of a Google Maps-formatted address.

    Google Maps addresses look like:
        "500033, Andra Basti, Guttala_Begumpet, Hyderabad, Telangana 500081, India"
        "Madhapur Main Rd, Hyderabad, Telangana, India"
        "Banjara Hills, Hyderabad, India"

    Algorithm: split on commas, then walk from the right. Skip the country
    (always the last segment). Then look for a "state" segment — either:
      - "StateName PINCODE" combined (e.g. "Telangana 500081")
      - "StateName" alone (e.g. "Telangana")
    The segment immediately before that state segment is the city.

    Examples:
        "500033, Andra Basti, Guttala_Begumpet, Hyderabad, Telangana 500081, India"
            → "Hyderabad"
        "Madhapur Main Rd, Hyderabad, Telangana, India"
            → "Hyderabad"
        "Banjara Hills, Hyderabad, India"
            → "Hyderabad"
        "Sector 18, Noida, Uttar Pradesh 201301, India"
            → "Noida"
    """
    if not address:
        return ""
    parts = [p.strip() for p in address.split(",") if p.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]

    # Strip the country (last segment) before scanning for the state.
    # Then find the first segment from the right that looks like a state.
    # Segments before it = the city (if 1+ segments) or the parts[0] (edge case).
    tail = parts[:-1]  # everything except the country

    for i in range(len(tail) - 1, -1, -1):
        p = tail[i]
        is_state = (
            # "StateName PINCODE" e.g. "Telangana 500081"
            re.match(r"^[A-Z][a-z]+( [A-Z][a-z]+)*\s+\d{4,7}$", p)
            or
            # "StateName" alone, e.g. "Telangana" — typically a known state
            _is_indian_state(p)
        )
        if is_state:
            if i >= 1:
                return tail[i - 1]
            return parts[0]

    # Fallback: no state segment found. Take the last non-empty segment.
    return tail[-1] if tail else parts[0]


# Small set of common Indian states (the leads target Indian cities).
# If a non-state segment happens to match one of these names, we treat it
# as a state and use the segment before it as the city.
_INDIAN_STATES = {
    "andhra pradesh", "arunachal pradesh", "assam", "bihar",
    "chhattisgarh", "goa", "gujarat", "haryana", "himachal pradesh",
    "jharkhand", "karnataka", "kerala", "madhya pradesh",
    "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland",
    "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu",
    "telangana", "tripura", "uttar pradesh", "uttarakhand",
    "west bengal", "delhi", "jammu and kashmir", "ladakh", "chandigarh",
}


def _is_indian_state(segment: str) -> bool:
    return segment.strip().lower() in _INDIAN_STATES


def new_id() -> str:
    return uuid4().hex[:12]


# ---------- Retry decorator ----------
def retry(max_attempts: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Retry a function with exponential backoff + jitter.
    Example:
        @retry(max_attempts=4, base_delay=2, exceptions=(requests.RequestException,))
        def call_api(): ...
    """
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            log = get_logger(f"retry.{fn.__name__}")
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        log.error(f"FAILED after {attempt} attempts: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    log.warning(f"Attempt {attempt} failed ({e}); retrying in {delay:.1f}s")
                    time.sleep(delay)
        return wrapper
    return decorator


# ---------- Base Agent ----------
class BaseAgent:
    """
    All agents inherit from this.
    Subclasses override `run()`. Call `agent.run()` to execute.
    """
    name: str = "base"

    def __init__(self):
        self.log = get_logger(f"agent.{self.name}")

    def run(self, *args, **kwargs):
        raise NotImplementedError

    # ----- lead helpers -----
    def load_leads(self) -> list[dict]:
        # Leads are stored as a LIST so we can append without read-modify-write races
        data = load_json(LEADS_FILE, default=[])
        return data if isinstance(data, list) else []

    def save_leads(self, leads: list[dict]) -> None:
        save_json(LEADS_FILE, leads)

    def upsert_lead(self, lead: dict) -> bool:
        """
        Insert or update a lead by `place_id` (or `lead_id` if missing).
        Returns True if a NEW lead was added.

        Deep-merges the `business` sub-dict so that new fields added in later
        scraper versions (e.g. gbp_link) flow into older leads automatically.
        Top-level fields are merged shallowly.
        """
        leads = self.load_leads()
        key = lead.get("place_id") or lead.get("lead_id")
        for i, existing in enumerate(leads):
            if existing.get("place_id") == lead.get("place_id") or existing.get("lead_id") == lead.get("lead_id"):
                merged = {**existing, **lead}
                # Deep-merge the business sub-dict so new fields (gbp_link, etc.)
                # get filled in for leads scraped before the field existed.
                if "business" in existing and "business" in lead:
                    merged["business"] = {**existing["business"], **lead["business"]}
                leads[i] = merged
                self.save_leads(leads)
                self.log.info(f"Updated lead {key}")
                return False
        leads.append(lead)
        self.save_leads(leads)
        self.log.info(f"New lead added {key}")
        return True

    # ----- queue helpers -----
    def queue(self) -> dict:
        return load_json(QUEUE_FILE, default={})

    def set_queue(self, place_id: str, stage: str, status: str = "pending", **extra) -> None:
        q = self.queue()
        q[place_id] = {"stage": stage, "status": status, "updated_at": now_iso(), **extra}
        save_json(QUEUE_FILE, q)

    # ----- built-sites registry (cross-run dedup) -----
    def load_built(self) -> dict:
        """
        Load the dedup registry: {place_id: {name, location_key, site_url, ...}}.

        This is the single source of truth for "we have already built a site
        for this business". Any agent that produces work products (Agent 2
        builds, future Agent 3 outreach) should check this before processing.
        """
        return load_json(BUILT_SITES_FILE, default={})

    def save_built(self, registry: dict) -> None:
        save_json(BUILT_SITES_FILE, registry)

    def mark_built(
        self,
        place_id: str,
        name: str,
        address: str = "",
        phone: str = "",
        site_url: str = "",
        extra: Optional[dict] = None,
    ) -> None:
        """
        Add (or update) an entry in the built-sites registry.

        Stores both the place_id (exact match) and a `location_key` (fuzzy
        match by name+city) so dedup works even if the same business shows
        up with a different place_id (e.g. after a re-scrape).
        """
        city = _extract_city(address)
        norm = re.sub(r"[^a-z0-9]", "", name.lower()) if name else ""
        location_key = f"{city}|{norm}"

        registry = self.load_built()
        registry[place_id] = {
            "place_id": place_id,
            "name": name,
            "address": address,
            "phone": phone,
            "city": city,
            "location_key": location_key,
            "site_url": site_url,
            "site_built_at": now_iso(),
            "status": "built",
            **(extra or {}),
        }
        self.save_built(registry)
        self.log.info(f"  📌 Marked built: {name} ({place_id})")

    def is_built(self, lead: dict) -> bool:
        """
        Return True if this lead has already been built.

        Checks three ways (in order, first hit wins):
          1. Exact place_id match in the registry
          2. Fuzzy match: same normalized name + city
          3. Lead itself has status=='built' (recovered from leads.json)
        """
        registry = self.load_built()
        place_id = lead.get("place_id") or ""
        if place_id and place_id in registry:
            return True

        b = lead.get("business", {})
        name = b.get("name", "")
        address = b.get("address", "")
        city = _extract_city(address)
        norm = re.sub(r"[^a-z0-9]", "", name.lower()) if name else ""
        target_key = f"{city}|{norm}"
        for entry in registry.values():
            if entry.get("location_key") == target_key and target_key != "|":
                return True

        # Fallback: check the lead's own status field
        if lead.get("status") == "built":
            return True

        return False