"""
Step 4: Post video to Instagram and Facebook via Ayrshare API.
Generates platform-specific captions (IG gets more hashtags, FB more conversational).
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

    # Combine base + dynamic hashtags
    base_tags = script_data.get("base_hashtags", [])
    dynamic_tags = script_data.get("dynamic_hashtags", [])
    all_tags = list(set(dynamic_tags + base_tags))
    random.shuffle(all_tags)
    selected = all_tags[: POSTING["ig_max_hashtags"]]

    full = f"{caption}\n\n.\n.\n.\n{'  '.join(selected)}"

    if len(full) > POSTING["caption_max_length"]:
        full = full[: POSTING["caption_max_length"] - 3] + "..."
    return full


def build_fb_caption(script_data: dict) -> str:
    """Build Facebook caption: conversational, fewer hashtags."""
    caption = script_data.get("fb_caption", script_data.get("caption", ""))

    # Only a few hashtags for FB
    dynamic_tags = script_data.get("dynamic_hashtags", [])
    fb_tags = dynamic_tags[: POSTING["fb_max_hashtags"]]

    full = f"{caption}\n\n{'  '.join(fb_tags)}" if fb_tags else caption
    return full


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
    """Post with platform-specific captions."""
    profile = get_profile()
    platforms = profile["platforms"]
    results = {}

    # Ayrshare accepts one caption per post, so we post to each platform
    # separately to get custom captions. If both use the same caption,
    # we can combine them.

    ig_caption = build_ig_caption(script_data)
    fb_caption = build_fb_caption(script_data)

    if "instagram" in platforms and "facebook" in platforms:
        if ig_caption == fb_caption:
            # Same caption — post together
            result = _post_to_ayrshare(video_url, ig_caption, ["instagram", "facebook"])
            results["combined"] = result
        else:
            # Different captions — post separately
            if "instagram" in platforms:
                print("   📸 Posting to Instagram...")
                results["instagram"] = _post_to_ayrshare(
                    video_url, ig_caption, ["instagram"]
                )
            if "facebook" in platforms:
                print("   📘 Posting to Facebook...")
                results["facebook"] = _post_to_ayrshare(
                    video_url, fb_caption, ["facebook"]
                )
    else:
        # Single platform
        caption = ig_caption if "instagram" in platforms else fb_caption
        result = _post_to_ayrshare(video_url, caption, platforms)
        results["post"] = result

    return results


def main() -> dict:
    """Upload and post video to social media."""
    print("📤 Step 4: Posting to social media...")

    script_data = load_json("temp/script.json")
    video_path = "output/final_video.mp4"

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    # DRY RUN check
    if DRY_RUN:
        print("   🧪 DRY RUN — skipping actual posting")
        result = {"status": "dry_run", "message": "Video generated but not posted"}
        save_json("temp/post_result.json", result)
        return result

    # Upload
    print("   ⬆️  Uploading video...")
    video_url = upload_video(video_path)
    print(f"   ✅ Uploaded")

    # Post
    print(f"   📱 Posting to: {', '.join(get_profile()['platforms'])}...")
    result = post_to_social(video_url, script_data)

    print("   ✅ Posted successfully!")
    save_json("temp/post_result.json", result)

    return result


if __name__ == "__main__":
    main()
