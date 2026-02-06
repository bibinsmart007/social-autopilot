"""
Shared utilities: retry with exponential backoff, JSON helpers, logging.
"""

import os
import json
import time
import functools
import traceback
from datetime import datetime, timezone, timedelta
from config import RETRY, PATHS

UAE_TZ = timezone(timedelta(hours=4))


def retry_with_backoff(description: str = "operation"):
    """
    Decorator: retry a function up to max_attempts with exponential backoff.
    Raises the last exception if all attempts fail.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, RETRY["max_attempts"] + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < RETRY["max_attempts"]:
                        delay = min(
                            RETRY["base_delay"] * (2 ** (attempt - 1)),
                            RETRY["max_delay"],
                        )
                        print(f"   ⚠️  {description} attempt {attempt} failed: {e}")
                        print(f"       Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"   ❌ {description} failed after {attempt} attempts: {e}")
            raise last_exc
        return wrapper
    return decorator


def load_json(filepath: str, default=None):
    """Safely load a JSON file, returning default if missing or corrupt."""
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}


def save_json(filepath: str, data):
    """Save data to a JSON file, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def now_uae() -> datetime:
    """Current datetime in UAE timezone."""
    return datetime.now(UAE_TZ)


def today_str() -> str:
    """Today's date as YYYY-MM-DD in UAE timezone."""
    return now_uae().strftime("%Y-%m-%d")


def today_weekday() -> str:
    """Today's weekday name (e.g. 'Monday')."""
    return now_uae().strftime("%A")
