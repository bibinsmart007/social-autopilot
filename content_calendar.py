"""
Content Calendar — ensures variety by tracking past posts and rotating
niches, topics, and video styles intelligently.

Rules:
- Never repeat the same niche two days in a row
- Cycle through all 4 niches evenly
- Rotate through all 5 video styles
- Never repeat a topic until all topics in that niche are exhausted
"""

import random
from config import NICHES, VIDEO_STYLES, PATHS, get_profile
from utils import load_json, save_json, today_str


def _load_calendar() -> dict:
    """Load content calendar history."""
    return load_json(PATHS["content_calendar"], default={
        "posts": [],           # List of {date, niche, topic, style}
        "niche_cycle": [],     # Tracks niche rotation order
        "style_cycle": [],     # Tracks style rotation order
        "used_topics": {},     # {niche: [used_topic_1, ...]}
    })


def _save_calendar(cal: dict):
    save_json(PATHS["content_calendar"], cal)


def pick_niche(cal: dict) -> str:
    """Pick today's niche, ensuring no back-to-back repeats and even cycling."""
    profile = get_profile()
    available_niches = profile["niches"]

    # What was yesterday's niche?
    last_niche = None
    if cal["posts"]:
        last_niche = cal["posts"][-1].get("niche")

    # Rebuild cycle if exhausted
    if not cal["niche_cycle"]:
        cal["niche_cycle"] = list(available_niches)
        random.shuffle(cal["niche_cycle"])
        # If first in new cycle == last posted, rotate it to the end
        if cal["niche_cycle"] and cal["niche_cycle"][0] == last_niche:
            moved = cal["niche_cycle"].pop(0)
            cal["niche_cycle"].append(moved)

    chosen = cal["niche_cycle"].pop(0)

    # Double-check no back-to-back (edge case with 1-niche profiles)
    if chosen == last_niche and len(available_niches) > 1:
        cal["niche_cycle"].append(chosen)
        chosen = cal["niche_cycle"].pop(0)

    return chosen


def pick_topic(cal: dict, niche: str) -> str:
    """Pick an unused topic from the niche. Reset when all are used."""
    all_topics = NICHES[niche]["topics"]
    used = cal.get("used_topics", {}).get(niche, [])

    available = [t for t in all_topics if t not in used]

    if not available:
        # All topics used — reset this niche
        cal.setdefault("used_topics", {})[niche] = []
        available = list(all_topics)

    chosen = random.choice(available)
    cal.setdefault("used_topics", {}).setdefault(niche, []).append(chosen)
    return chosen


def pick_style(cal: dict) -> str:
    """Rotate through video styles evenly."""
    all_styles = list(VIDEO_STYLES.keys())

    if not cal["style_cycle"]:
        cal["style_cycle"] = list(all_styles)
        random.shuffle(cal["style_cycle"])

    return cal["style_cycle"].pop(0)


def select_todays_content() -> dict:
    """
    Main entry point: select today's niche, topic, and style.
    Returns dict with all content decisions.
    """
    cal = _load_calendar()

    niche = pick_niche(cal)
    topic = pick_topic(cal, niche)
    style = pick_style(cal)

    # Record this selection
    entry = {
        "date": today_str(),
        "niche": niche,
        "topic": topic,
        "style": style,
    }
    cal["posts"].append(entry)

    # Keep only last 90 days of calendar history
    cal["posts"] = cal["posts"][-90:]

    _save_calendar(cal)

    return entry
