"""
Step 1: Generate video script using Google Gemini API (free tier).
Falls back to backup scripts if Gemini is unavailable.
"""

import os
import json
import shutil
from datetime import datetime
from config import NICHES, VIDEO_STYLES, SCRIPT_PROMPT, VIDEO, PATHS
from utils import retry_with_backoff, load_json, save_json, today_str

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


@retry_with_backoff(description="Gemini API call")
def _call_gemini(prompt: str) -> str:
    """Call Gemini API with retry logic."""
    import requests

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 1200,
        },
    }

    response = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()

    result = response.json()
    text = result["candidates"][0]["content"]["parts"][0]["text"]

    # Clean markdown fences
    text = text.strip()
    for prefix in ["```json", "```JSON", "```"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def generate_script(niche: str, topic: str, style: str) -> dict:
    """Generate a video script via Gemini or fallback."""

    duration = VIDEO["duration_seconds"]
    word_count = int(duration * 2.5)
    niche_display = niche.replace("_", " ").title()
    style_data = VIDEO_STYLES[style]

    prompt = SCRIPT_PROMPT.format(
        duration=duration,
        topic=topic,
        niche=niche_display,
        style_name=style.replace("_", " ").title(),
        style_hint=style_data["prompt_hint"],
        word_count=word_count,
    )

    try:
        raw = _call_gemini(prompt)
        script_data = json.loads(raw)

        # Validate required fields
        required = ["hook", "body", "cta", "ig_caption", "fb_caption",
                     "title_text", "dynamic_hashtags"]
        for field in required:
            if field not in script_data:
                raise ValueError(f"Missing field: {field}")

        script_data["source"] = "gemini"

    except Exception as e:
        print(f"   ⚠️  Gemini failed completely: {e}")
        print(f"   📦 Loading backup script...")
        script_data = _load_backup_script(niche, topic, style)
        script_data["source"] = "backup"

    return script_data


def _load_backup_script(niche: str, topic: str, style: str) -> dict:
    """Load a pre-written backup script for the given niche."""
    backups = load_json(PATHS["backup_scripts"], default={"scripts": []})
    scripts = backups.get("scripts", [])

    # Try to find a matching niche script
    niche_scripts = [s for s in scripts if s.get("niche") == niche]
    if not niche_scripts:
        niche_scripts = scripts  # Fall back to any script

    if not niche_scripts:
        # Ultimate fallback — hardcoded generic script
        return _emergency_script(niche, topic)

    # Pick one that hasn't been used recently
    import random
    chosen = random.choice(niche_scripts)

    # Ensure it has all required fields
    chosen.setdefault("dynamic_hashtags", ["#dailytips", "#growth", "#motivation"])
    chosen.setdefault("ig_caption", chosen.get("caption", f"Daily tip on {topic} 🔥"))
    chosen.setdefault("fb_caption", chosen.get("caption", f"Here's a tip on {topic}"))
    chosen.setdefault("title_text", topic.title()[:30])

    return chosen


def _emergency_script(niche: str, topic: str) -> dict:
    """Absolute last-resort hardcoded script."""
    return {
        "hook": f"Here's something about {topic} that will change your perspective.",
        "body": [
            f"Most people overlook {topic}, but it can transform your daily life.",
            "Small consistent changes lead to remarkable results over time.",
            "The key is to start simple and build momentum day by day.",
            "Winners focus on progress, not perfection.",
        ],
        "cta": "Follow for more daily tips that actually work!",
        "ig_caption": f"🔥 {topic.title()}\n\nSmall changes → Big results.\n\nSave this for later! 🔖",
        "fb_caption": f"Something I learned about {topic} that changed everything for me...",
        "title_text": topic.title()[:25],
        "dynamic_hashtags": ["#dailytips", "#growthmindset", "#motivation"],
    }


def build_full_narration(script_data: dict) -> str:
    """Combine script parts into full narration text."""
    parts = [script_data["hook"]]
    parts.extend(script_data["body"])
    parts.append(script_data["cta"])
    return " ... ".join(parts)  # Pauses between sections


def archive_script(script_data: dict, niche: str, topic: str, style: str):
    """Save script to archive folder with date-based filename."""
    archive_dir = PATHS["scripts_archive_dir"]
    os.makedirs(archive_dir, exist_ok=True)

    date_str = today_str()
    filename = f"{date_str}_{niche}_{style}.json"
    filepath = os.path.join(archive_dir, filename)

    archive_entry = {
        "date": date_str,
        "niche": niche,
        "topic": topic,
        "style": style,
        **script_data,
    }
    save_json(filepath, archive_entry)
    print(f"   📂 Script archived: {filename}")


def main(content: dict = None) -> dict:
    """Generate script and save to temp directory."""
    print("📝 Step 1: Generating script...")

    if content is None:
        from content_calendar import select_todays_content
        content = select_todays_content()

    niche = content["niche"]
    topic = content["topic"]
    style = content["style"]

    print(f"   Niche: {niche}")
    print(f"   Topic: {topic}")
    print(f"   Style: {style}")

    script_data = generate_script(niche, topic, style)
    narration = build_full_narration(script_data)

    # Enrich with metadata
    niche_data = NICHES[niche]
    script_data["niche"] = niche
    script_data["topic"] = topic
    script_data["style"] = style
    script_data["narration"] = narration
    script_data["search_terms"] = niche_data["search_terms"]
    script_data["base_hashtags"] = niche_data["base_hashtags"]
    script_data["niche_color"] = niche_data["color"]
    script_data["niche_color_name"] = niche_data["color_name"]
    script_data["text_position"] = VIDEO_STYLES[style]["text_position"]

    # Save to temp
    os.makedirs("temp", exist_ok=True)
    save_json("temp/script.json", script_data)

    # Archive
    archive_script(script_data, niche, topic, style)

    print(f"   Source: {script_data.get('source', 'unknown')}")
    print(f"   Title: {script_data['title_text']}")
    print(f"   Hook: {script_data['hook'][:80]}...")
    print("   ✅ Script saved")

    return script_data


if __name__ == "__main__":
    main()
