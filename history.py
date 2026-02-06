"""
History tracker — logs every run (success or failure) to history.json.
"""

import os
from config import PATHS
from utils import load_json, save_json, today_str, now_uae


def log_success(script_data: dict, post_result: dict, dry_run: bool = False):
    """Log a successful post to history."""
    history = load_json(PATHS["history"], default={"entries": []})

    entry = {
        "date": today_str(),
        "timestamp": now_uae().isoformat(),
        "status": "dry_run" if dry_run else "success",
        "niche": script_data.get("niche"),
        "topic": script_data.get("topic"),
        "style": script_data.get("style"),
        "title": script_data.get("title_text"),
        "script_source": script_data.get("source"),
        "platforms": "none (dry run)" if dry_run else "instagram, facebook",
        "error": None,
    }
    history["entries"].append(entry)

    # Keep last 365 entries
    history["entries"] = history["entries"][-365:]
    save_json(PATHS["history"], history)


def log_error(step: str, error_message: str, script_data: dict = None):
    """Log a failed run to history."""
    history = load_json(PATHS["history"], default={"entries": []})

    entry = {
        "date": today_str(),
        "timestamp": now_uae().isoformat(),
        "status": "error",
        "niche": script_data.get("niche") if script_data else None,
        "topic": script_data.get("topic") if script_data else None,
        "style": script_data.get("style") if script_data else None,
        "title": None,
        "script_source": None,
        "platforms": None,
        "error": f"{step}: {error_message[:200]}",
    }
    history["entries"].append(entry)
    history["entries"] = history["entries"][-365:]
    save_json(PATHS["history"], history)
