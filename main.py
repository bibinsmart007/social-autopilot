"""
Social AutoPilot — Main Orchestrator (Production-Ready)
Runs the full pipeline with graceful error handling, history logging,
and DRY_RUN support.
"""

import os
import sys
import traceback

from config import DRY_RUN
from content_calendar import select_todays_content
from generate_script import main as generate_script
from generate_voice import main as generate_voice
from generate_video import main as generate_video
from post_social import main as post_social
from notify import send_success, send_error, send_weekly_summary, main as notify_main
from history import log_success, log_error
from utils import load_json, now_uae, today_str


def run_pipeline():
    """Execute the full pipeline with error recovery."""

    print("=" * 60)
    print("🚀 Social AutoPilot — Production Pipeline")
    if DRY_RUN:
        print("🧪 DRY RUN MODE — video will NOT be posted")
    print(f"📅 {now_uae().strftime('%Y-%m-%d %I:%M %p')} UAE")
    print("=" * 60)

    script_data = None

    # ── Step 0: Content calendar ──
    try:
        print(f"\n{'─' * 40}")
        print("📅 Selecting today's content...")
        content = select_todays_content()
        print(f"   Niche: {content['niche']}")
        print(f"   Topic: {content['topic']}")
        print(f"   Style: {content['style']}")
    except Exception as e:
        _handle_failure("Content Calendar", e, script_data)
        return

    # ── Step 1: Script generation ──
    try:
        print(f"\n{'─' * 40}")
        script_data = generate_script(content)
    except Exception as e:
        _handle_failure("Script Generation", e, script_data)
        return

    # ── Step 2: Voice generation ──
    try:
        print(f"\n{'─' * 40}")
        generate_voice()
    except Exception as e:
        _handle_failure("Voice Generation", e, script_data)
        return

    # ── Step 3: Video generation ──
    try:
        print(f"\n{'─' * 40}")
        generate_video()
    except Exception as e:
        _handle_failure("Video Generation", e, script_data)
        return

    # ── Step 4: Social posting ──
    try:
        print(f"\n{'─' * 40}")
        post_result = post_social()
    except Exception as e:
        _handle_failure("Social Posting", e, script_data)
        return

    # ── Step 5: Success! Log + notify ──
    print(f"\n{'─' * 40}")
    print("📊 Logging to history...")
    try:
        log_success(script_data, post_result, dry_run=DRY_RUN)
    except Exception as e:
        print(f"   ⚠️  History logging failed: {e}")

    print("🔔 Sending notification...")
    try:
        send_success(script_data, post_result)

        # Weekly summary on Sundays
        if now_uae().strftime("%A") == "Sunday":
            print("   📊 Sunday — sending weekly summary...")
            send_weekly_summary()
    except Exception as e:
        print(f"   ⚠️  Notification failed: {e}")

    print(f"\n{'=' * 60}")
    status = "generated (DRY RUN)" if DRY_RUN else "published"
    print(f"✅ Pipeline complete — video {status}!")
    print(f"{'=' * 60}")


def _handle_failure(step: str, exception: Exception, script_data: dict = None):
    """Handle pipeline failure gracefully: log, notify, skip today."""
    error_msg = str(exception)
    print(f"\n❌ PIPELINE FAILED at step: {step}")
    print(f"   Error: {error_msg}")
    print(traceback.format_exc())

    # Log to history
    try:
        log_error(step, error_msg, script_data)
    except Exception:
        print("   ⚠️  Could not log error to history")

    # Send error notification
    try:
        send_error(error_msg, step)
        print("   📱 Error notification sent to Telegram")
    except Exception:
        print("   ⚠️  Could not send error notification")

    print("\n⏭️  Skipping today's post. Will retry tomorrow.")
    # Exit with 0 so GitHub Actions doesn't flag the whole workflow as failed
    # (we've already handled the error gracefully)
    sys.exit(0)


if __name__ == "__main__":
    run_pipeline()
