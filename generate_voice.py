"""
Step 2: Generate voiceover using Edge TTS (completely free).
Includes retry logic and audio normalization.
"""

import os
import json
import asyncio
import subprocess
import edge_tts
from config import VOICE, VIDEO
from utils import retry_with_backoff, load_json


@retry_with_backoff(description="Edge TTS generation")
def _generate_tts(text: str, output_path: str):
    """Generate speech with retry support."""

    async def _run():
        communicate = edge_tts.Communicate(
            text=text,
            voice=VOICE["voice_id"],
            rate=VOICE["rate"],
            pitch=VOICE["pitch"],
        )
        await communicate.save(output_path)

    asyncio.run(_run())

    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
        raise RuntimeError("TTS output file is missing or too small")


def normalize_audio(input_path: str, output_path: str):
    """Normalize audio levels using FFmpeg loudnorm filter."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar", "44100", "-ac", "1",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ⚠️  Normalization warning: {result.stderr[-200:]}")
        # Fall back to unnormalized
        if not os.path.exists(output_path):
            os.rename(input_path, output_path)


def get_audio_duration(audio_path: str) -> float:
    """Get duration of an audio file using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-show_entries",
            "format=duration", "-of", "csv=p=0", audio_path,
        ],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def main() -> str:
    """Load script and generate voiceover."""
    print("🎙️  Step 2: Generating voiceover...")

    script_data = load_json("temp/script.json")
    narration = script_data["narration"]

    os.makedirs("temp", exist_ok=True)
    raw_path = "temp/voiceover_raw.mp3"
    final_path = "temp/voiceover.mp3"

    # Generate TTS
    _generate_tts(narration, raw_path)

    # Normalize audio levels
    if VIDEO.get("audio_normalize", True):
        print("   🔊 Normalizing audio levels...")
        normalize_audio(raw_path, final_path)
        # Clean up raw
        if os.path.exists(raw_path) and os.path.exists(final_path):
            os.remove(raw_path)
    else:
        os.rename(raw_path, final_path)

    duration = get_audio_duration(final_path)
    size_kb = os.path.getsize(final_path) / 1024
    print(f"   Voice: {VOICE['voice_id']}")
    print(f"   Duration: {duration:.1f}s | Size: {size_kb:.0f} KB")
    print("   ✅ Voiceover ready")

    return final_path


if __name__ == "__main__":
    main()
