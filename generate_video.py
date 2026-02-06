"""
Step 3: Generate video — multi-clip stitching with crossfade transitions,
Ken Burns effect, niche-colored text overlays, and fallback clips.
"""

import os
import json
import glob
import random
import subprocess
import requests
from config import VIDEO, PATHS, VIDEO_STYLES, NICHES, get_profile
from utils import retry_with_backoff, load_json

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"


FONT_URL = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf"
FONT_PATH = "fonts/Montserrat-Bold.ttf"
FALLBACK_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def ensure_font() -> str:
    """Ensure font exists: try custom -> auto-download -> system fallback."""
    if os.path.exists(FONT_PATH):
        return FONT_PATH
    # Try downloading
    try:
        os.makedirs("fonts", exist_ok=True)
        resp = requests.get(FONT_URL, timeout=15)
        resp.raise_for_status()
        with open(FONT_PATH, "wb") as f:
            f.write(resp.content)
        print(f"  Downloaded {FONT_PATH}")
        return FONT_PATH
    except Exception as e:
        print(f"  Font download failed: {e}")
    # Fallback to system font
    if os.path.exists(FALLBACK_FONT):
        return FALLBACK_FONT
    return FONT_PATH  # Let FFmpeg handle missing font error

# ── Stock footage download ────────────────────────────────────

@retry_with_backoff(description="Pexels API search")
def _search_pexels(query: str, per_page: int = 15) -> list:
    """Search Pexels for videos with retry."""
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": "portrait",
        "size": "medium",
        "per_page": per_page,
    }
    resp = requests.get(PEXELS_VIDEO_URL, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("videos", [])


def download_stock_clips(search_terms: list, num_clips: int = 4) -> list:
    """Download portrait stock clips from Pexels. Falls back to local clips."""
    clip_paths = []
    downloaded_ids = set()
    os.makedirs("temp/clips", exist_ok=True)

    for term in search_terms:
        if len(clip_paths) >= num_clips:
            break

        try:
            videos = _search_pexels(term)
        except Exception as e:
            print(f"   ⚠️  Pexels search failed for '{term}': {e}")
            continue

        random.shuffle(videos)

        for video in videos:
            if len(clip_paths) >= num_clips:
                break
            if video["id"] in downloaded_ids:
                continue

            # Find portrait HD file
            video_file = None
            for vf in video["video_files"]:
                w, h = vf.get("width", 0), vf.get("height", 0)
                if h > w and h >= 720:
                    video_file = vf
                    break
            if not video_file and video["video_files"]:
                video_file = video["video_files"][0]
            if not video_file:
                continue

            clip_path = f"temp/clips/clip_{len(clip_paths):02d}.mp4"
            try:
                dl = requests.get(video_file["link"], timeout=30)
                dl.raise_for_status()
                with open(clip_path, "wb") as f:
                    f.write(dl.content)
                clip_paths.append(clip_path)
                downloaded_ids.add(video["id"])
                print(f"   📥 Clip {len(clip_paths)}/{num_clips}: {term}")
            except Exception as e:
                print(f"   ⚠️  Download failed: {e}")

    # Fallback to local clips if not enough
    if len(clip_paths) < 3:
        print("   📦 Using fallback clips...")
        clip_paths = _load_fallback_clips(clip_paths, num_clips)

    return clip_paths


def _load_fallback_clips(existing: list, needed: int) -> list:
    """Load pre-downloaded fallback clips."""
    fallback_dir = PATHS["fallback_clips_dir"]
    if not os.path.exists(fallback_dir):
        return existing

    fallback_files = sorted(glob.glob(os.path.join(fallback_dir, "*.mp4")))
    random.shuffle(fallback_files)

    for fb in fallback_files:
        if len(existing) >= needed:
            break
        existing.append(fb)

    if len(existing) < 2:
        raise RuntimeError(f"Only {len(existing)} clips available. Need at least 2.")

    return existing


# ── BGM selection ─────────────────────────────────────────────

def select_bgm() -> str:
    """Randomly select a background music file."""
    bgm_dir = PATHS["bgm_dir"]
    if not os.path.exists(bgm_dir):
        return None
    bgm_files = [
        f for f in os.listdir(bgm_dir)
        if f.endswith((".mp3", ".wav", ".m4a"))
    ]
    if not bgm_files:
        return None
    return os.path.join(bgm_dir, random.choice(bgm_files))


# ── FFmpeg helpers ────────────────────────────────────────────

def get_duration(path: str) -> float:
    """Get media duration via ffprobe."""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def _escape(text: str) -> str:
    """Escape text for FFmpeg drawtext filter."""
    return (
        text.replace("\\", "\\\\")
        .replace("'", "'\\''")
        .replace(":", "\\:")
        .replace("%", "%%")
        .replace('"', '\\"')
    )


# ── Clip processing with Ken Burns ───────────────────────────

def process_clip(clip_path: str, index: int, clip_dur: float) -> str:
    """Scale, crop, and apply Ken Burns effect to a single clip."""
    out = f"temp/clips/kb_{index:02d}.mp4"
    w, h = VIDEO["width"], VIDEO["height"]
    zoom = VIDEO["ken_burns_zoom"]
    fps = VIDEO["fps"]

    # Alternate zoom direction for variety
    if index % 2 == 0:
        # Zoom in slowly
        zoompan = (
            f"zoompan=z='min(zoom+0.0005,{zoom})':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={int(clip_dur * fps)}:s={w}x{h}:fps={fps}"
        )
    else:
        # Slow pan from top-left to bottom-right
        zoompan = (
            f"zoompan=z='{zoom}':"
            f"x='if(eq(on,0),0,x+0.5)':"
            f"y='if(eq(on,0),0,y+0.3)':"
            f"d={int(clip_dur * fps)}:s={w}x{h}:fps={fps}"
        )

    cmd = [
        "ffmpeg", "-y", "-i", clip_path,
        "-t", str(clip_dur),
        "-vf", (
            f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,"
            f"crop={w * 2}:{h * 2},"
            f"{zoompan},"
            f"setsar=1"
        ),
        "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        out,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback: simple scale/crop without Ken Burns
        cmd_simple = [
            "ffmpeg", "-y", "-i", clip_path,
            "-t", str(clip_dur),
            "-vf", (
                f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h},fps={fps}"
            ),
            "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            out,
        ]
        subprocess.run(cmd_simple, capture_output=True, check=True)

    return out


# ── Stitch clips with crossfade ──────────────────────────────

def stitch_clips(processed_clips: list, target_duration: float) -> str:
    """Concatenate clips with xfade crossfade transitions."""
    if len(processed_clips) < 2:
        return processed_clips[0]

    cf_dur = VIDEO["crossfade_duration"]
    output = "temp/stitched.mp4"

    # Build xfade filter chain
    # For N clips: need N-1 xfade filters chained
    filter_parts = []
    current_input = "[0:v]"
    clip_dur = VIDEO["clip_duration"]

    for i in range(1, len(processed_clips)):
        next_input = f"[{i}:v]"
        offset = (clip_dur * i) - (cf_dur * i)
        offset = max(offset, clip_dur * i - cf_dur * i)
        out_label = f"[v{i}]" if i < len(processed_clips) - 1 else "[vout]"

        filter_parts.append(
            f"{current_input}{next_input}xfade=transition=fade:"
            f"duration={cf_dur}:offset={offset:.2f}{out_label}"
        )
        current_input = out_label

    # If only simple concat needed (xfade can be finicky)
    try:
        inputs = []
        for clip in processed_clips:
            inputs.extend(["-i", clip])

        filter_complex = ";".join(filter_parts)

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-t", str(target_duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            output,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(result.stderr[-300:])
    except Exception as e:
        print(f"   ⚠️  Crossfade failed, using simple concat: {e}")
        output = _simple_concat(processed_clips, target_duration)

    return output


def _simple_concat(clips: list, target_duration: float) -> str:
    """Fallback: simple concatenation without transitions."""
    output = "temp/stitched.mp4"
    concat_file = "temp/clips/concat.txt"

    with open(concat_file, "w") as f:
        for c in clips:
            abs_path = os.path.abspath(c)
            f.write(f"file '{abs_path}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-t", str(target_duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        output,
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output


# ── Final composite ──────────────────────────────────────────

def composite_video(
    video_path: str,
    voice_path: str,
    bgm_path: str,
    script_data: dict,
    output_path: str,
):
    """Composite: video + voiceover + BGM + niche-colored text overlays."""

    voice_vol = VIDEO["voice_volume"]
    bgm_vol = VIDEO["bgm_volume"]
    duration = get_duration(voice_path)

    # Text content
    title = _escape(script_data.get("title_text", "")[:40])
    hook = _escape(script_data.get("hook", "")[:80])
    watermark = _escape(get_profile()["watermark_text"])
    cta = _escape(get_profile()["cta_text"])

    # Niche-specific colors
    niche = script_data.get("niche", "health_wellness")
    niche_color = NICHES.get(niche, {}).get("color", "#FFFFFF")
    accent = NICHES.get(niche, {}).get("accent", "#FFFFFF")

    # Text position from style
    text_pos = script_data.get("text_position", "center")
    if text_pos == "top":
        title_y = "h*0.15"
        hook_y = "h*0.22"
    elif text_pos == "bottom":
        title_y = "h*0.70"
        hook_y = "h*0.77"
    else:
        title_y = "(h-text_h)/2"
        hook_y = "(h-text_h)/2"

    # Font
        font_path = ensure_font()

    title_size = int(VIDEO["title_font_size"])
    text_size = int(VIDEO["text_font_size"])

    # Build text overlay filters
    text_filters = [
        # Title card (first 4 seconds)
        f"drawbox=y={title_y}:w=iw:h=180:color=black@0.55:t=fill:enable='between(t,0.5,4.5)'",
        f"drawtext=text='{title}':fontfile={font_path}:fontsize={title_size}:"
        f"fontcolor={niche_color}:x=(w-text_w)/2:y={title_y}+40:"
        f"enable='between(t,0.5,4.5)'",

        # Hook line (4-9 seconds)
        f"drawbox=y={hook_y}:w=iw:h=140:color=black@0.55:t=fill:enable='between(t,4.5,9.5)'",
        f"drawtext=text='{hook}':fontfile={font_path}:fontsize={text_size}:"
        f"fontcolor=white:x=(w-text_w)/2:y={hook_y}+30:"
        f"enable='between(t,4.5,9.5)'",

        # Watermark (always visible)
        f"drawtext=text='{watermark}':fontfile={font_path}:fontsize=26:"
        f"fontcolor=white@0.6:x=30:y=h-55",

        # CTA (last 6 seconds)
        f"drawbox=y=h*0.58:w=iw:h=100:color={accent}@0.85:t=fill:enable='gte(t,{duration-6})'",
        f"drawtext=text='{cta}':fontfile={font_path}:fontsize=38:"
        f"fontcolor=white:x=(w-text_w)/2:y=h*0.58+25:"
        f"enable='gte(t,{duration-6})'",
    ]

    # Optional logo overlay
    logo_path = get_profile().get("logo_path")
    if logo_path and os.path.exists(logo_path):
        # We'll add logo as a separate input and overlay it
        pass  # Handled below in cmd construction

    vf_string = ",".join(text_filters)

    # ── Audio mix ──
    inputs = ["-i", video_path, "-i", voice_path]
    if bgm_path and os.path.exists(bgm_path):
        inputs.extend(["-i", bgm_path])
        audio_filter = (
            f"[1:a]volume={voice_vol},loudnorm=I=-16:TP=-1.5:LRA=11[voice];"
            f"[2:a]volume={bgm_vol},"
            f"afade=t=in:st=0:d=2,"
            f"afade=t=out:st={duration-3}:d=3[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        audio_map = "[aout]"
    else:
        audio_filter = (
            f"[1:a]volume={voice_vol},loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
        )
        audio_map = "[aout]"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", audio_filter,
        "-vf", vf_string,
        "-map", "0:v",
        "-map", audio_map,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-t", str(min(duration + 1, VIDEO["duration_seconds"] + 5)),
        "-r", str(VIDEO["fps"]),
        "-movflags", "+faststart",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ⚠️  FFmpeg stderr: {result.stderr[-500:]}")
        raise RuntimeError("FFmpeg composite failed!")


# ── Main ─────────────────────────────────────────────────────

def main() -> str:
    """Full video generation pipeline."""
    print("🎬 Step 3: Generating video...")

    script_data = load_json("temp/script.json")
    voice_path = "temp/voiceover.mp3"
    voice_duration = get_duration(voice_path)
    print(f"   Voiceover: {voice_duration:.1f}s")

    # Calculate clips needed
    clip_dur = VIDEO["clip_duration"]
    num_clips = max(VIDEO["clips_per_video"], int(voice_duration / clip_dur) + 1)
    print(f"   Downloading {num_clips} stock clips...")

    # Build search queries from topic + niche terms
    topic_words = script_data.get("topic", "").split()[:2]
    search_terms = topic_words + script_data.get("search_terms", ["nature"])

    clip_paths = download_stock_clips(search_terms, num_clips)
    print(f"   Got {len(clip_paths)} clips")

    # Process clips with Ken Burns
    print("   🎥 Applying Ken Burns effect...")
    processed = []
    for i, cp in enumerate(clip_paths):
        processed.append(process_clip(cp, i, clip_dur))

    # Stitch with crossfade
    print("   ✂️  Stitching with crossfade...")
    stitched = stitch_clips(processed, voice_duration + 2)

    # Select BGM
    bgm_path = select_bgm()
    if bgm_path:
        print(f"   🎵 BGM: {os.path.basename(bgm_path)}")

    # Final composite
    os.makedirs("output", exist_ok=True)
    output_path = "output/final_video.mp4"
    print("   🎞️  Compositing final video...")
    composite_video(stitched, voice_path, bgm_path, script_data, output_path)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.1f} MB")
    print("   ✅ Video ready")

    return output_path


if __name__ == "__main__":
    main()
