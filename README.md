# GMB Lead Pipeline

End-to-end pipeline that turns **Google Maps businesses without a website**
into **deployed landing pages** and **WhatsApp cold outreach** messages.

Built as 3 cooperating agents + 1 autonomous orchestrator:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Agent 1     │    │  Agent 2     │    │  Agent 3     │
│  GMB Scraper │───▶│  Site Builder│───▶│  Outreach    │
│  (SerpAPI)   │    │  (React+Netl)│    │  (WhatsApp)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                                       │
        ▼                                       ▼
   data/leads.json                      data/built_sites.json
                                        (with outreach.status)
```

## What it does

1. **Agent 1 (`agents/gmb_scraper.py`)** — Pulls business leads from Google
   Maps via [SerpAPI](https://serpapi.com/), enriches each with full place
   details, and classifies the business kind (e.g. `used_car_dealer`,
   `car_dealer`, `restaurant`). Writes to `data/leads.json`.

2. **Agent 2 (`agents/site_builder.py`)** — For each lead, clones a React/
   Vite template (`external/car-dealers-template`), generates marketing copy
   + an SVG logo via OpenAI, builds a static site, and deploys to Netlify.
   Records the live URL in `data/built_sites.json`.

3. **Agent 3 (`agents/outreach.py`)** — For each deployed site, generates
   a personalized 2-message WhatsApp sequence (intro + link) via OpenAI
   and sends it through a [Baileys](https://github.com/WhiskeySockets/Baileys)
   Node.js sender (`whatsapp-sender/`). Marks outreach status in
   `data/built_sites.json` so the same lead is never messaged twice.

4. **Orchestrator (`scripts/run_pipeline.py`)** — Runs the whole chain
   in one command. Designed for cron / CI.

## Repository layout

```
gmb-pipeline/
├── agents/
│   ├── base_agent.py           # shared: JSON I/O, logging, retries,
│   │                           # lead/queue/built-sites helpers
│   ├── gmb_scraper.py          # Agent 1
│   ├── business_classifier.py  # used-car / restaurant / etc. classifier
│   ├── site_builder.py         # Agent 2
│   └── outreach.py             # Agent 3
├── scripts/
│   ├── run_pipeline.py         # 🚀 main entry point (autonomous)
│   ├── scrape_only.py          # debug helpers
│   ├── list_netlify_sites.py
│   ├── cleanup_*.py            # maintenance
│   └── ...                     # 17 utility scripts total
├── external/
│   ├── car-dealers-template/   # React/Vite template (embedded git repo)
│   └── car_dealer_generator/   # legacy/alt generator
├── whatsapp-sender/            # Baileys Node.js sender (Agent 3 transport)
│   ├── agent.py                # standalone CLI for the sender
│   ├── message_generator.py    # OpenAI prompt for the 2 WhatsApp msgs
│   └── sender/                 # Node.js deps + sender.js
├── templates/                  # prompt templates (legacy)
├── data/                       # runtime state (gitignored, regeneratable)
│   ├── leads.json              # all leads
│   ├── built_sites.json        # dedup registry + outreach status
│   └── queue.json              # per-place_id stage/status
├── logs/                       # structured pipeline.log (gitignored)
├── site_builder_workdir/       # per-lead React clones (gitignored)
├── config.py                   # all env-driven settings
├── env_loader.py               # .env loader (no python-dotenv needed)
├── requirements.txt
├── .env.example                # copy → .env, fill in keys
└── README.md
```

## Quick start

### 1. Clone + install

```bash
git clone https://github.com/yashwanth1403/gmb-pipeline.git
cd gmb-pipeline

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# For Agent 3 (WhatsApp sender):
cd whatsapp-sender/sender
npm install
cd ../../..
```

### 2. Configure secrets

```bash
cp .env.example .env
# Open .env and fill in:
#   SERPAPI_KEY          (https://serpapi.com/dashboard)
#   OPENAI_API_KEY       (https://platform.openai.com/api-keys)
#   NETLIFY_AUTH_TOKEN   (https://app.netlify.com/user/applications/personal-access-tokens)
#   NETLIFY_TEAM_SLUG    (your Netlify team/account slug)
```

Minimal `.env` for **Agent 1 + 2**:

```env
SERPAPI_KEY=your_serpapi_key
OPENAI_API_KEY=sk-...
NETLIFY_AUTH_TOKEN=your_netlify_pat
NETLIFY_TEAM_SLUG=yashwanth1403
GMB_QUERY=used car dealers in Madhapur, Hyderabad, India
DEPLOY_TO_NETLIFY=true
```

### 3. Run individual agents

```bash
# Agent 1 only — fetch + enrich 20 used-car dealers in Hyderabad
python -m agents.gmb_scraper --query "used car dealers in Madhapur" --enrich --enrich-limit 5

# Agent 2 only — build + deploy for every lead in data/leads.json
python -m agents.site_builder --deploy

# Agent 3 only — WhatsApp outreach to every built+deployed site
python -m agents.outreach --all --dry-run          # preview first
python -m agents.outreach --all --max 5             # actually send (max 5)

# Or send to one specific lead:
python -m agents.outreach --place-id ChIJxxxx
```

### 4. Run the whole chain autonomously

```bash
# Scrape → build → deploy → outreach (one command, hands-off)
python scripts/run_pipeline.py --deploy --outreach

# Useful flags:
#   --query "..."          custom GMB search
#   --max 10               cap leads saved
#   --enrich               full enrichment pass
#   --enrich-limit 5       cap enrichment to 5 leads
#   --outreach-dry-run     preview WhatsApp messages, don't send
#   --outreach-max 3       cap Agent 3 sends per run
#   --skip-scrape          reuse existing data/leads.json
#   --skip-build           only scrape, don't build
#   --no-llm               skip OpenAI in Agent 2 (use embedded content)
#   --no-logo              skip OpenAI logo (use initial fallback)
#   --force-rebuild        rebuild already-built leads
```

### 5. Agent 3 (WhatsApp) first-time setup

Agent 3 needs a one-time QR scan to link your WhatsApp account:

```bash
cd whatsapp-sender/sender
node sender.js setup
# → QR prints in terminal
# → On your phone: WhatsApp → ⋮ → Linked Devices → Link a Device → scan
# → Session saved to auth_info/ (gitignored)
# → You only do this once; the session is reused on every subsequent run
```

After the QR is scanned, `--outreach` works.

## Data contracts (important for extending)

### Lead (`data/leads.json`)

```json
{
  "lead_id": "...",
  "place_id": "ChIJxxxx",
  "source": "serpapi",
  "scraped_at": "2026-06-19T...",
  "business": {
    "name": "MUJEEB CARS",
    "category": "Used car dealer",
    "address": "Plot no.518/1, Chilkalguda, Secunderabad, ...",
    "phone": "+91 70950 61026",
    "rating": 4.5,
    "review_count": 50,
    "type_ids": ["used_car_dealer", "car_dealer"],
    "place_id": "ChIJxxxx",
    "website": null,
    "has_website": false,
    "country": "India",
    "plus_code": "...",
    "open_state": "OPEN",
    "rating_summary": [...],
    "photo_gallery": [...],
    "services": [...],
    "popular_times": {...},
    "competitors": [...],
    "gbp_link": "https://www.google.com/maps/place/?q=place_id:ChIJxxxx"
  },
  "status": "scraped",
  "attempts": {"scrape": 1, "build": 0, "outreach": 0}
}
```

### Built site (`data/built_sites.json`)

```json
{
  "ChIJxxxx": {
    "place_id": "ChIJxxxx",
    "name": "MUJEEB CARS",
    "address": "...",
    "phone": "+91 70950 61026",
    "city": "Hyderabad",
    "location_key": "Hyderabad|mujeebcars",
    "site_url": "https://xxx--mujeeb-cars.netlify.app",
    "site_built_at": "2026-06-19T...",
    "status": "built",
    "outreach": {
      "status": "sent",
      "phone": "+91xxxxxxx026",
      "site_url": "...",
      "at": "2026-06-19T...",
      "msg1_preview": "Hi MUJEEB CARS! ..."
    }
  }
}
```

### Queue (`data/queue.json`)

```json
{
  "ChIJxxxx": {
    "stage": "outreach",
    "status": "sent",
    "updated_at": "2026-06-19T...",
    "site_url": "...",
    "phone": "+91xxxxxxx026"
  }
}
```

## Configuration reference (full list in `.env.example`)

| Key | Purpose | Default |
|---|---|---|
| `SERPAPI_KEY` | Agent 1 — SerpAPI auth | (required) |
| `GMB_QUERY` | Agent 1 — search query (location baked in) | `restaurants` |
| `GMB_LOCATION` | Agent 1 — optional radius filter city | `None` |
| `SCRAPE_MAX_RESULTS` | Agent 1 — max results to keep | `40` |
| `SCRAPE_KINDS` | Agent 1 — business kinds to keep (CSV) | `used_car_dealer` |
| `REQUIRE_PHONE` | Agent 1 — drop leads with no phone | `true` |
| `OPENAI_API_KEY` | Agents 2 & 3 — OpenAI auth | (required) |
| `OPENAI_LOGO_MODEL` | Agent 2 — logo gen model | `gpt-4o-mini` |
| `LLM_PROVIDER` | Agent 2 — `openai` or `anthropic` | `openai` |
| `USE_LLM` | Agent 2 — call OpenAI? | `true` |
| `GENERATE_LOGO` | Agent 2 — OpenAI logo? | `true` |
| `NETLIFY_AUTH_TOKEN` | Agent 2 — Netlify PAT | (required for deploy) |
| `NETLIFY_TEAM_SLUG` | Agent 2 — Netlify account slug | (required for deploy) |
| `DEPLOY_TO_NETLIFY` | Agent 2 — auto-deploy? | `false` |
| `BUILDER_ALLOWED_KINDS` | Agent 2 — defense-in-depth filter | `used_car_dealer,car_dealer` |
| `REACT_TEMPLATE_DIR` | Agent 2 — path to template | `external/car-dealers-template` |
| `SEND_WHATSAPP` | Agent 3 — enable WhatsApp | `false` |
| `RUN_AGENT3_AUTOMATIC` | Agent 3 — auto-run in `run_pipeline.py` | `false` |
| `WA_DAILY_LIMIT` | Agent 3 — max sends per run | `20` |
| `WA_MSG_DELAY_SEC` | Agent 3 — delay between msg 1 & 2 | `3` |

## Logging

All agents write structured logs to `logs/pipeline.log` and stdout:

```
2026-06-19T19:41:00 | INFO    | agent.outreach  | 📨 MUJEEB CARS → +917****1026 → https://...
2026-06-19T19:41:05 | INFO    | httpx           | HTTP Request: POST .../v1/chat/completions "200 OK"
```

Format: `ISO timestamp | LEVEL | logger_name | message`

## Extending the pipeline

Adding a new agent? It should:
1. Inherit from `BaseAgent` (gives you `load_leads`, `save_leads`,
   `upsert_lead`, `set_queue`, `load_built`, `mark_built`).
2. Be invokable as a module: `python -m agents.my_agent [args]`.
3. Return a `{"built": N, "deployed": N, "skipped": N, "errors": N}` dict
   if you want it to plug into `scripts/run_pipeline.py`.

## License

MIT — for personal/educational use. Be respectful of WhatsApp's ToS when
using Agent 3; this is a personal-account Baileys sender, not a business
API client.
