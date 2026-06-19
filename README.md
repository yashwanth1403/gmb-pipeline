# GMB Lead Pipeline — Agent 1: Scraper

Finds Google Maps businesses **without a website**, so they can be
turned into leads for a website-building + outreach service.

## Architecture

```
agents/
  base_agent.py       ← shared: logging, JSON I/O, retries, lead/queue helpers
  gmb_scraper.py      ← Agent 1 (this)
config.py             ← all env-driven settings
env_loader.py         ← loads .env without python-dotenv
data/
  leads.json          ← all leads (list), deduped by place_id
  queue.json          ← state per place_id (stage/status)
logs/pipeline.log     ← structured log across all agents
```

## Setup

### 1. Get a SerpAPI key (free tier OK)
- Sign up at https://serpapi.com/
- Copy your **Private API Key** from the dashboard
- Free tier = 100 searches/month (enough for testing)

### 2. Configure
```bash
# Copy the template
copy .env.example .env

# Open .env and paste your key:
#   SERPAPI_KEY=abc123yourkeyhere
```

### 3. Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### 4. Run
```bash
# Default: restaurants in Mumbai, 40 results
python -m agents.gmb_scraper

# Custom:
python -m agents.gmb_scraper --query "salons" --location "Pune, India" --max 20
```

### 5. Inspect results
```bash
type data\leads.json           # Windows
cat data/leads.json            # macOS/Linux
```

## Lead schema (contract for Agents 2 & 3)

```json
{
  "lead_id": "...",
  "place_id": "...",
  "source": "serpapi",
  "scraped_at": "ISO8601",
  "business": {
    "name": "...",
    "category": "...",
    "address": "...",
    "phone": "+91...",
    "rating": 4.3,
    "review_count": 87,
    "hours": {...},
    "photos": ["url", ...],
    "thumbnail": "url",
    "lat": 19.13, "lng": 72.82,
    "website": null,
    "has_website": false,
    "place_id": "..."
  },
  "status": "scraped",
  "attempts": {"scrape": 1, "build": 0, "outreach": 0}
}
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `SERPAPI_KEY missing` | You forgot to paste the key in `.env` |
| `0 raw results` | Try a broader query or different location |
| `kept=0` | All results had websites — try a less-saturated niche |
| `SerpAPI call failed` | Check your key & free-tier quota at serpapi.com/dashboard |