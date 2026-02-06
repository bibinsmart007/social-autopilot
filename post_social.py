"""
Step 4: Post video to social media via Ayrshare API.
Supports Instagram, Facebook, LinkedIn, TikTok, and X/Twitter.
Generates platform-specific captions.
Supports DRY_RUN mode.
"""
import os
import json
import random
import requests
from config import POSTING, DRY_RUN, get_profile
from utils import retry_with_backoff, load_json, save_json

AYRSHARE_POST_URL = "https://app.ayrshare.com/api/post"
AYRSHARE_UPLOAD_URL = "https://app.ayrshare.com/api/media/upload"


def _get_ayrshare_key() -> str:
    """Get the Ayrshare API key for the active brand profile."""
    env_var = get_profile()["ayrshare_key_env"]
    key = os.environ.get(env_var)
    if not key:
        raise RuntimeError(f"Ayrshare API key not found in env var: {env_var}")
    return key


@retry_with_backoff(description="Ayrshare video upload")
def upload_video(video_path: str) -> str:
    """Upload video to Ayrshare and return public URL."""
    headers = {"Authorization": f"Bearer {_get_ayrshare_key()}"}
    with open(video_path, "rb") as f:
        files = {"file": ("video.mp4", f, "video/mp4")}
        response = requests.post(
            AYRSHARE_UPLOAD_URL,
            headers=headers,
            files=files,
            timeout=120,
        )
    response.raise_for_status()
    data = response.json()
    url = data.get("url") or data.get("accessUrl")
    if not url:
        raise RuntimeError(f"Upload response missing URL: {data}")
    return url


def build_ig_caption(script_data: dict) -> str:
    """Build Instagram caption: hook + value + CTA + lots of hashtags."""
    caption = script_data.get("ig_caption", script_data.get("caption", ""))
    base_tags = script_data.get("base_hashtags", [])
    dynamic_tags = script_data.get("dynamic_hashtags", [])
    all_tags = list(set(dynamic_tags + base_tags))
    random.shuffle(all_tags)
    selected = all_tags[: POSTING["ig_max_hashtags"]]
    full = f"{caption}\n\n.\n.\n.\n{' '.join(selected)}"
    if len(full) > POSTING["caption_max_length"]:
        full = full[: POSTING["caption_max_length"] - 3] + "..."
    return full


def build_fb_caption(script_data: dict) -> str:
    """Build Facebook caption: conversational, fewer hashtags."""
    caption = script_data.get("fb_caption", script_data.get("caption", ""))
    dynamic_tags = script_data.get("dynamic_hashtags", [])
    fb_tags = dynamic_tags[: POSTING["fb_max_hashtags"]]
    full = f"{caption}\n\n{' '.join(fb_tags)}" if fb_tags else caption
    return full


def build_linkedin_caption(script_data: dict) -> str:
    """Build LinkedIn caption: professional tone, minimal hashtags."""
    caption = script_data.get("linkedin_caption", script_data.get("caption", ""))
    dynamic_tags = script_data.get("dynamic_hashtags", [])
    li_tags = dynamic_tags[:3]
    full = f"{caption}\n\n{' '.join(li_tags)}" if li_tags else caption
    return full


def build_tiktok_caption(script_data: dict) -> str:
    """Build TikTok caption: short, trendy, hashtag-heavy."""
    caption = script_data.get("tiktok_caption", script_data.get("caption", ""))
    base_tags = script_data.get("base_hashtags", [])
    dynamic_tags = script_data.get("dynamic_hashtags", [])
    all_tags = list(set(dynamic_tags + base_tags))
    random.shuffle(all_tags)
    selected = all_tags[:10]
    full = f"{caption} {' '.join(selected)}"
    if len(full) > 150:
        full = full[:147] + "..."
    return full


def build_twitter_caption(script_data: dict) -> str:
    """Build Twitter/X caption: short, punchy, max 280 chars."""
    caption = script_data.get("twitter_caption", script_data.get("caption", ""))
    dynamic_tags = script_data.get("dynamic_hashtags", [])
    tw_tags = dynamic_tags[:2]
    full = f"{caption} {' '.join(tw_tags)}" if tw_tags else caption
    if len(full) > 280:
        full = full[:277] + "..."
    return full


def _get_caption_for_platform(platform: str, script_data: dict) -> str:
    """Get the right caption builder for each platform."""
    builders = {
        "instagram": build_ig_caption,
        "facebook": build_fb_caption,
        "linkedin": build_linkedin_caption,
        "tiktok": build_tiktok_caption,
        "twitter": build_twitter_caption,
    }
    builder = builders.get(platform, build_fb_caption)
    return builder(script_data)


@retry_with_backoff(description="Ayrshare post")
def _post_to_ayrshare(video_url: str, caption: str, platforms: list) -> dict:
    """Post to specified platforms via Ayrshare."""
    headers = {
        "Authorization": f"Bearer {_get_ayrshare_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "post": caption,
        "platforms": platforms,
        "mediaUrls": [video_url],
        "isVideo": True,
    }
    response = requests.post(
        AYRSHARE_POST_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def post_to_social(video_url: str, script_data: dict) -> dict:
    """Post with platform-specific captions to all configured platforms."""
    profile = get_profile()
    platforms = profile["platforms"]
    results = {}

    platform_icons = {
        "instagram": "📸",
        "facebook": "📘",
        "linkedin": "💼",
        "tiktok": "🎵",
        "twitter": "🐦",
    }

    for platform in platforms:
        icon = platform_icons.get(platform, "📱")
        print(f"  {icon} Posting to {platform.capitalize()}...")
        try:
            caption = _get_caption_for_platform(platform, script_data)
            result = _post_to_ayrshare(video_url, caption, [platform])
            results[platform] = {"status": "success", "response": result}
            print(f"  ✅ {platform.capitalize()} posted!")
        except Exception as e:
            print(f"  ❌ {platform.capitalize()} failed: {e}")
            results[platform] = {"status": "error", "error": str(e)}

    return results


def main() -> dict:
    """Upload and post video to social media."""
    print("📤 Step 4: Posting to social media...")
    script_data = load_json("temp/script.json")
    video_path = "output/final_video.mp4"

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    if DRY_RUN:
        print("  🧪 DRY RUN — skipping actual posting")
        result = {"status": "dry_run", "message": "Video generated but not posted"}
        save_json("temp/post_result.json", result)
        return result

    print("  ⬆️ Uploading video...")
    video_url = upload_video(video_path)
    print(f"  ✅ Uploaded")

    print(f"  📱 Posting to: {', '.join(get_profile()['platforms'])}...")
    result = post_to_social(video_url, script_data)

    success_count = sum(1 for r in result.values() if r.get("status") == "success")
    total = len(result)
    print(f"  ✅ Posted to {success_count}/{total} platforms!")

    save_json("temp/post_result.json", result)
    return result


if __name__ == "__main__":
    main()
