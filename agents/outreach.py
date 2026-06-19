"""
agents/outreach.py — Agent 3: WhatsApp outreach (pipeline-integrated)

Loads leads from data/built_sites.json (only businesses with a live site_url),
generates a personalized 2-message WhatsApp sequence via OpenAI, and sends
it through the Baileys Node.js sender that lives in `whatsapp-sender/sender/`.

This wraps the cloned repo's `agent.py` + `message_generator.py` so it works
inside the pipeline (uses BaseAgent, queue, built_sites registry) without
duplicating the OpenAI prompt or the Node.js call.

Usage (from project root):
    # First-time QR login (one time only, scans a QR in your terminal):
    cd whatsapp-sender/sender && npm install && node sender.js setup
    #   ↑ scan QR → session saved to auth_info/

    # Send outreach to a single lead (dry-run first!):
    python -m agents.outreach --place-id ChIJxxxx
    python -m agents.outreach --place-id ChIJxxxx --dry-run

    # Or let the autonomous pipeline drive it (after `RUN_AGENT3_AUTOMATIC=true`):
    python scripts/run_pipeline.py --deploy
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Make sure project root is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load .env BEFORE importing config so config picks up the values
import env_loader  # noqa: F401  (side-effect: populates os.environ)

from config import (
    OPENAI_API_KEY,
    RUN_AGENT3_AUTOMATIC,
    WA_AUTH_DIR,
    WA_DAILY_LIMIT,
    WA_SENDER_DIR,
)
from agents.base_agent import BaseAgent, load_json, save_json, now_iso


# ---------- helpers ----------
def _digits(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


def _has_session() -> bool:
    """True if a Baileys auth_info/ session exists (i.e. QR has been scanned)."""
    if not WA_AUTH_DIR.exists():
        return False
    # A real session has creds.json inside; that is the canonical signal.
    return (WA_AUTH_DIR / "creds.json").exists()


def _find_lead_by_place_id(place_id: str) -> Optional[dict]:
    """Look up a lead in data/leads.json by place_id. Returns the full lead dict."""
    leads = load_json(ROOT / "data" / "leads.json", default=[])
    if isinstance(leads, dict):  # tolerate either shape
        leads = list(leads.values())
    for lead in leads:
        if lead.get("place_id") == place_id:
            return lead
    return None


def _phone_for_lead(lead: dict) -> str:
    """Extract the last 10 digits of the lead's phone, robust to '+91 ' prefixes."""
    raw = (lead.get("business") or {}).get("phone", "")
    digits = _digits(raw)
    return digits[-10:] if len(digits) >= 10 else ""


# ---------- Agent 3 ----------
class OutreachAgent(BaseAgent):
    """
    Pipeline-integrated Agent 3.

    Reuses the cloned `whatsapp-sender/message_generator.py` for the OpenAI
    prompt (no copy-paste of the prompt) and shells out to the Node.js
    `sender.js` for actual delivery via Baileys.
    """

    name = "outreach"

    def __init__(self):
        super().__init__()
        # Make the cloned repo importable so we can reuse message_generator.py
        wa_repo = ROOT / "whatsapp-sender"
        if str(wa_repo) not in sys.path:
            sys.path.insert(0, str(wa_repo))
        # Import lazily so the file is editable in-place without restart pain
        from message_generator import generate_messages  # type: ignore
        self._generate_messages = generate_messages

    # ----- core send primitive -----
    def _send_via_node(self, phone_10: str, msg1: str, msg2: str) -> tuple[bool, str]:
        """
        Shell out to the Baileys sender. Returns (success, output).
        """
        payload = json.dumps({"phone": phone_10, "msg1": msg1, "msg2": msg2})
        sender_js = WA_SENDER_DIR / "sender.js"
        if not sender_js.exists():
            return False, f"sender.js missing at {sender_js}"

        self.log.info(f"  📤 Sending 2 messages to +91{phone_10} via Baileys...")
        try:
            result = subprocess.run(
                ["node", "sender.js", "send"],
                input=payload,
                cwd=str(WA_SENDER_DIR),
                capture_output=True,
                text=True,
                timeout=90,
            )
            output = (result.stdout or "") + (result.stderr or "")
            return result.returncode == 0, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Timed out after 90s"
        except FileNotFoundError as e:
            return False, f"Node not found: {e}"

    # ----- one lead -----
    def send_to_lead(
        self,
        lead: dict,
        site_url: str,
        dry_run: bool = False,
        phone_override: str = "",
    ) -> dict:
        """
        Send WhatsApp outreach for a single lead. Returns a status dict.
        """
        business = lead.get("business") or {}
        name = business.get("name", "Business")
        place_id = lead.get("place_id", "")

        if phone_override:
            phone_10 = _digits(phone_override)[-10:]
        else:
            phone_10 = _phone_for_lead(lead)

        if not phone_10 or len(phone_10) != 10:
            msg = f"❌ No 10-digit phone for {name} (got {phone_10!r})"
            self.log.warning(msg)
            return {"ok": False, "reason": "no_phone", "phone": phone_10}

        if not site_url:
            msg = f"❌ No site_url for {name} — build/deploy first"
            self.log.warning(msg)
            return {"ok": False, "reason": "no_site_url", "phone": phone_10}

        self.log.info(f"📨 {name} → +91{phone_10} → {site_url}")

        # 1) Generate the two-message sequence via OpenAI
        try:
            msg1, msg2 = self._generate_messages(business, site_url)
        except Exception as e:
            self.log.error(f"OpenAI message generation failed for {name}: {e}")
            return {"ok": False, "reason": f"openai_error: {e}", "phone": phone_10}

        # Always print what we'd send, even in dry-run, so you can sanity-check.
        print(f"\n── {name} ────────────────────────────────")
        print(f"📱 +91{phone_10}")
        print(f"🌐 {site_url}")
        print("─ Message 1 ─")
        print(msg1)
        print("─ Message 2 ─")
        print(msg2)
        print("──────────────────────────────────────────")

        if dry_run:
            self.log.info("  ℹ️  dry-run — not sending")
            return {"ok": True, "dry_run": True, "phone": phone_10, "msg1": msg1, "msg2": msg2}

        # 2) Send through the Baileys Node.js helper
        ok, output = self._send_via_node(phone_10, msg1, msg2)
        if output:
            # Surface the Node.js output line by line for easier debugging
            for line in output.splitlines():
                if line.strip():
                    print(f"    {line}")

        # 3) Update queue + built_sites
        stage = "outreach"
        status = "sent" if ok else "failed"
        self.set_queue(place_id, stage, status, site_url=site_url, phone=f"+91{phone_10}")

        # Mark outreach result in built_sites.json
        registry = self.load_built()
        if place_id in registry:
            registry[place_id]["outreach"] = {
                "status": status,
                "phone": f"+91{phone_10}",
                "site_url": site_url,
                "at": now_iso(),
                "msg1_preview": (msg1 or "")[:80],
            }
            self.save_built(registry)

        return {"ok": ok, "phone": phone_10, "site_url": site_url, "status": status, "output": output}

    # ----- batch: built sites with phones -----
    def run(
        self,
        deploy: bool = False,
        only_built: bool = True,
        dry_run: bool = False,
        max_leads: Optional[int] = None,
    ) -> dict:
        """
        Run Agent 3 over every business in data/built_sites.json that:
          - has a non-empty site_url
          - has a phone in data/leads.json
          - hasn't been messaged already (or whose last outreach failed)

        `max_leads` defaults to WA_DAILY_LIMIT.
        """
        if not OPENAI_API_KEY:
            self.log.error("OPENAI_API_KEY is not set — cannot generate messages")
            return {"sent": 0, "failed": 0, "skipped": 0, "error": "no_openai_key"}

        if not _has_session():
            self.log.error(
                "No WhatsApp session found.\n"
                f"  Expected: {WA_AUTH_DIR / 'creds.json'}\n"
                "  Run this once to scan the QR and save the session:\n"
                f"    cd {WA_SENDER_DIR} && npm install && node sender.js setup"
            )
            return {"sent": 0, "failed": 0, "skipped": 0, "error": "no_session"}

        registry = self.load_built()
        if not registry:
            self.log.info("No built sites yet — nothing to outreach.")
            return {"sent": 0, "failed": 0, "skipped": 0}

        cap = max_leads if max_leads is not None else WA_DAILY_LIMIT
        sent = failed = skipped = 0
        results = []

        for place_id, entry in registry.items():
            if sent + failed >= cap:
                self.log.info(f"Reached WA_DAILY_LIMIT={cap}; stopping.")
                break

            site_url = entry.get("site_url", "")
            if not site_url:
                skipped += 1
                continue

            # Skip if already messaged successfully
            prev = entry.get("outreach") or {}
            if prev.get("status") == "sent" and not dry_run:
                self.log.info(f"  ⏭️  {entry.get('name')} already messaged — skipping")
                skipped += 1
                continue

            lead = _find_lead_by_place_id(place_id)
            if not lead:
                self.log.warning(f"  ⚠️  No lead in leads.json for {place_id} — skipping")
                skipped += 1
                continue

            r = self.send_to_lead(lead, site_url, dry_run=dry_run)
            results.append({"place_id": place_id, "name": entry.get("name"), **r})
            if r.get("ok") and not r.get("dry_run"):
                sent += 1
            elif r.get("ok") and r.get("dry_run"):
                # count dry-runs as "would-send" but don't claim real sends
                pass
            else:
                failed += 1

        # Summary
        print("\n" + "=" * 70)
        print("📊 AGENT 3 (OUTREACH) SUMMARY")
        print("=" * 70)
        print(f"  Sent:    {sent}")
        print(f"  Failed:  {failed}")
        print(f"  Skipped: {skipped}  (already messaged or no site_url)")
        if results:
            print("\n  Per-lead:")
            for r in results:
                flag = "✅" if r.get("ok") and not r.get("dry_run") else ("🟡" if r.get("dry_run") else "❌")
                print(f"    {flag} {r.get('name','?'):40s} +91{r.get('phone','?')}  {r.get('site_url','')}")
        print("=" * 70)

        return {"sent": sent, "failed": failed, "skipped": skipped, "results": results}


# ---------- CLI ----------
def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Agent 3 — WhatsApp outreach (pipeline-integrated)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--place-id", help="Send to a single lead by place_id")
    ap.add_argument("--phone", help="Override phone (10 digits, no +91)")
    ap.add_argument("--dry-run", action="store_true", help="Generate messages but don't send")
    ap.add_argument("--all", action="store_true", help="Send to all built+deployed sites")
    ap.add_argument("--max", type=int, default=None, help="Cap on leads to message")
    args = ap.parse_args()

    agent = OutreachAgent()

    if args.place_id:
        lead = _find_lead_by_place_id(args.place_id)
        if not lead:
            sys.exit(f"❌ place_id {args.place_id} not found in data/leads.json")
        # Get the site_url from the built registry
        registry = agent.load_built()
        entry = registry.get(args.place_id, {})
        site_url = entry.get("site_url", "")
        agent.send_to_lead(lead, site_url, dry_run=args.dry_run, phone_override=args.phone or "")
        return

    if args.all:
        agent.run(dry_run=args.dry_run, max_leads=args.max)
        return

    ap.print_help()
    print("\n💡 Examples:")
    print("  python -m agents.outreach --place-id ChIJxxxx --dry-run")
    print("  python -m agents.outreach --all --max 5")


if __name__ == "__main__":
    main()
