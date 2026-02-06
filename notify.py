"""
Step 5: Telegram notifications — success, error, DRY_RUN alerts,
and weekly summary reports.
"""

import os
import requests
from datetime import datetime, timedelta
from config import DRY_RUN, PATHS
from utils import retry_with_backoff, load_json, now_uae, today_str

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"


@retry_with_backoff(description="Telegram notification")
def _send_telegram(message: str, parse_mode: str = "HTML"):
    """Send a Telegram message with retry."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("   ⚠️  Telegram credentials not set. Skipping.")
        return None

    url = TELEGRAM_URL.format(token=TELEGRAM_BOT_TOKEN)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_success(script_data: dict, post_result: dict):
    """Send success notification."""
    niche = script_data.get("niche", "?").replace("_", " ").title()
    topic = script_data.get("topic", "?")
    title = script_data.get("title_text", "?")
    style = script_data.get("style", "?").replace("_", " ").title()
    source = script_data.get("source", "?")

    prefix = "🧪 <b>DRY RUN</b> — " if DRY_RUN else ""

    msg = (
        f"{prefix}✅ <b>Social AutoPilot — Post {'Generated' if DRY_RUN else 'Published'}!</b>\n\n"
        f"📌 <b>Niche:</b> {niche}\n"
        f"📝 <b>Topic:</b> {topic}\n"
        f"🎬 <b>Title:</b> {title}\n"
        f"🎨 <b>Style:</b> {style}\n"
        f"🤖 <b>Script:</b> {source}\n"
        f"📱 <b>Platforms:</b> {'Not posted (dry run)' if DRY_RUN else 'Instagram, Facebook'}\n\n"
        f"📅 {now_uae().strftime('%Y-%m-%d %I:%M %p')} UAE"
    )
    return _send_telegram(msg)


def send_error(error_message: str, step: str = "unknown"):
    """Send error notification."""
    msg = (
        f"❌ <b>Social AutoPilot — Error!</b>\n\n"
        f"🔧 <b>Failed Step:</b> {step}\n"
        f"⚠️ <b>Error:</b>\n<code>{error_message[:400]}</code>\n\n"
        f"📅 {now_uae().strftime('%Y-%m-%d %I:%M %p')} UAE\n"
        f"<i>Check GitHub Actions logs for full details.</i>"
    )
    return _send_telegram(msg)


def send_weekly_summary():
    """
    Send a weekly summary every Sunday: posts this week,
    niches covered, failures.
    """
    history = load_json(PATHS["history"], default={"entries": []})
    entries = history.get("entries", [])

    # Get this week's entries (last 7 days)
    today = datetime.strptime(today_str(), "%Y-%m-%d")
    week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")

    week_entries = [e for e in entries if e.get("date", "") >= week_ago]
    successes = [e for e in week_entries if e.get("status") == "success"]
    failures = [e for e in week_entries if e.get("status") == "error"]
    dry_runs = [e for e in week_entries if e.get("status") == "dry_run"]

    # Niche distribution
    niche_counts = {}
    for e in successes:
        n = e.get("niche", "unknown")
        niche_counts[n] = niche_counts.get(n, 0) + 1

    niche_breakdown = "\n".join(
        f"   • {n.replace('_', ' ').title()}: {c} posts"
        for n, c in sorted(niche_counts.items(), key=lambda x: -x[1])
    )
    if not niche_breakdown:
        niche_breakdown = "   No posts this week"

    # Style distribution
    style_counts = {}
    for e in successes:
        s = e.get("style", "unknown")
        style_counts[s] = style_counts.get(s, 0) + 1

    style_breakdown = "\n".join(
        f"   • {s.replace('_', ' ').title()}: {c}"
        for s, c in sorted(style_counts.items(), key=lambda x: -x[1])
    )

    msg = (
        f"📊 <b>Weekly Summary — Social AutoPilot</b>\n"
        f"📅 Week of {week_ago} → {today_str()}\n\n"
        f"✅ <b>Published:</b> {len(successes)}\n"
        f"❌ <b>Failed:</b> {len(failures)}\n"
        f"🧪 <b>Dry Runs:</b> {len(dry_runs)}\n\n"
        f"📌 <b>Niches:</b>\n{niche_breakdown}\n\n"
        f"🎨 <b>Styles:</b>\n{style_breakdown}\n\n"
    )

    if failures:
        fail_summary = "\n".join(
            f"   • {e.get('date')}: {e.get('error', '?')[:60]}"
            for e in failures[:5]
        )
        msg += f"⚠️ <b>Failures:</b>\n{fail_summary}\n"

    return _send_telegram(msg)


def main():
    """Send notification based on results."""
    print("🔔 Step 5: Sending notification...")

    try:
        script_data = load_json("temp/script.json")
        post_result = load_json("temp/post_result.json", default={})

        result = send_success(script_data, post_result)
        if result:
            print("   ✅ Notification sent!")

        # Check if it's Sunday → send weekly summary
        if now_uae().strftime("%A") == "Sunday":
            print("   📊 Sending weekly summary (it's Sunday)...")
            send_weekly_summary()
            print("   ✅ Weekly summary sent!")

    except Exception as e:
        print(f"   ⚠️  Notification failed: {e}")


if __name__ == "__main__":
    main()
