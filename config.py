"""Central config for the GMB lead pipeline."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DATA = ROOT / "data"
DEPLOY = ROOT / "deploy"
LOGS = ROOT / "logs"
TEMPLATES = ROOT / "templates"

QUEUE_FILE = DATA / "queue.json"
LEADS_FILE = DATA / "leads.json"
LOG_FILE = LOGS / "pipeline.log"

# Cross-run registry of businesses we've already built sites for.
# Keyed by place_id, but also stores a fuzzy `location_key` (name+city) so
# dedup works even if a re-scrape returns a different place_id for the
# same business. Checked by Agent 2 before every build.
BUILT_SITES_FILE = DATA / "built_sites.json"

# -------- Scraper settings --------
# SerpAPI key. Loaded from environment or .env file in project root.
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# Search query for Google Maps via SerpAPI.
# Location is baked INTO the query string (e.g. "car dealers in Andheri West").
GMB_QUERY = os.getenv("GMB_QUERY", "restaurants")

# OPTIONAL: city for SerpAPI radius-based filtering.
# Leave blank in .env if you bake location into GMB_QUERY.
# Returns None when not set, so the agent skips the location param entirely.
_GMB_LOCATION_RAW = os.getenv("GMB_LOCATION", "").strip()
GMB_LOCATION = _GMB_LOCATION_RAW if _GMB_LOCATION_RAW else None

# How many results to pull per run (SerpAPI returns 20 per page)
SCRAPE_MAX_RESULTS = int(os.getenv("SCRAPE_MAX_RESULTS", "40"))

# Only keep leads that have a phone (needed for outreach)
REQUIRE_PHONE = os.getenv("REQUIRE_PHONE", "true").lower() == "true"

# Comma-separated list of business_kind values to keep.
# Anything not in this list gets filtered out at the scraper stage.
# Default: used_car_dealer only. Set to "any" to disable filtering.
# Examples:
#   "used_car_dealer"        → only car dealers
#   "used_car_dealer,car_dealer" → both
#   "any"                    → keep everything (no kind filter)
SCRAPE_KINDS = os.getenv("SCRAPE_KINDS", "used_car_dealer")

# Defense-in-depth: business_kind values the builder will accept.
# If a lead slips through the scraper filter somehow, the builder will
# refuse to build it (and log an error) if its kind isn't in this list.
# Default must match what templates we actually have (car-dealers-template only).
BUILDER_ALLOWED_KINDS = os.getenv("BUILDER_ALLOWED_KINDS", "used_car_dealer,car_dealer")

# -------- Builder settings (Agent 2) --------
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "http://localhost:8000/sites")

# Path to the React template project (car-dealers-template) we cloned
REACT_TEMPLATE_DIR = ROOT / "external" / "car-dealers-template"

# Where Agent 2 builds per-lead working copies (gitignored, .gitkeep'd)
SITE_BUILDER_WORKDIR = ROOT / "site_builder_workdir"

# Netlify CLI auth token (get from https://app.netlify.com/user/applications/personal-access-tokens)
NETLIFY_AUTH_TOKEN = os.getenv("NETLIFY_AUTH_TOKEN", "")

# Netlify team/account slug. Required when using a Personal Access Token (PAT)
# to deploy to a team-owned account — otherwise `netlify sites:create` fails with
# "No teams available". Find yours: https://app.netlify.com/ → URL bar shows
# the slug after /teams/ (e.g. "yashwanth1403").
NETLIFY_TEAM_SLUG = os.getenv("NETLIFY_TEAM_SLUG", "")

# Should Agent 2 deploy to Netlify after building? Default false (build-only).
DEPLOY_TO_NETLIFY = os.getenv("DEPLOY_TO_NETLIFY", "false").lower() == "true"

# Should Agent 2 call the LLM for content? Default true.
# Disable with USE_LLM=false to use sample/embedded content (good for offline testing).
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"

# Which LLM provider for content generation (Agent 2).
# Options: "anthropic" (Claude), "openai" (GPT-4o-mini — used by original generator)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# OpenAI API key. Used when LLM_PROVIDER=openai AND for logo generation.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# OpenAI model for logo generation
OPENAI_LOGO_MODEL = os.getenv("OPENAI_LOGO_MODEL", "gpt-4o-mini")

# Should we generate a logo SVG via OpenAI? Falls back to an initial-based SVG if false.
GENERATE_LOGO = os.getenv("GENERATE_LOGO", "true").lower() == "true"

# -------- Outreach settings (Agent 3) --------
SEND_EMAIL = os.getenv("SEND_EMAIL", "false").lower() == "true"
SEND_WHATSAPP = os.getenv("SEND_WHATSAPP", "false").lower() == "true"

# Agent 3 is opt-in for the autonomous run_pipeline.py:
# only fires if BOTH this is true AND there is an auth_info/ session present.
RUN_AGENT3_AUTOMATIC = os.getenv("RUN_AGENT3_AUTOMATIC", "false").lower() == "true"

# Where the Baileys WhatsApp session is stored (qr-scanned once).
# Points at the cloned whatsapp-sender repo by default.
WA_SENDER_DIR = ROOT / "whatsapp-sender" / "sender"
WA_AUTH_DIR = WA_SENDER_DIR / "auth_info"

# How many seconds to wait between sending message 1 and message 2 to the
# same recipient (tweak in sender.js too if you want to change the human-feel).
WA_MSG_DELAY_SEC = int(os.getenv("WA_MSG_DELAY_SEC", "3"))

# Cap how many leads Agent 3 will message in one run (safety).
WA_DAILY_LIMIT = int(os.getenv("WA_DAILY_LIMIT", "20"))

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

WA_API_TOKEN = os.getenv("WA_API_TOKEN", "")
WA_PHONE_ID = os.getenv("WA_PHONE_ID", "")