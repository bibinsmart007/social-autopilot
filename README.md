# 🚀 Social AutoPilot — Production-Ready AI Video Automation

Fully automated daily AI-generated video content posted to Instagram & Facebook.
Runs on GitHub Actions — works 24/7 even with your laptop off.

## ✨ Features

- **Smart Content Calendar** — rotates niches evenly, never repeats same niche back-to-back
- **5 Video Styles** — motivational, listicle, story, did-you-know, problem-solution
- **Multi-Clip Videos** — 3-4 stock clips stitched with crossfade transitions
- **Ken Burns Effect** — slow zoom/pan on footage so clips don't look static
- **Niche-Colored Themes** — green (health), gold (wealth), blue (business), purple (mental)
- **Variable Posting Times** — different optimal time each day of the week
- **Platform-Specific Captions** — IG gets more hashtags, FB gets conversational tone
- **3 Dynamic Hashtags** — AI generates topic-specific tags alongside static ones
- **Retry with Backoff** — every API call retries 3x with exponential backoff
- **Graceful Failure** — if anything fails, skips today and sends Telegram error alert
- **Backup Scripts** — 30 pre-written scripts if Gemini API is unavailable
- **Fallback Clips** — local stock footage if Pexels is down
- **DRY_RUN Mode** — test everything without posting
- **History Tracking** — logs every post with full metadata
- **Weekly Summary** — Telegram report every Sunday
- **Script Archive** — all generated scripts saved with dates
- **Multi-Account Ready** — add more brand profiles without code changes

## 💰 Cost: $0/month

| Service         | Free Tier                         |
|-----------------|-----------------------------------|
| Gemini API      | 60 req/min (we use 1/day)         |
| Edge TTS        | Unlimited, completely free        |
| Pexels API      | 200 req/hr (we use ~5/day)        |
| FFmpeg          | Open source                       |
| Ayrshare        | 2 posts/day free                  |
| GitHub Actions  | 2000 min/mo (we use ~200)         |
| Telegram Bot    | Free                              |

## 📋 Quick Setup (~30 min)

### 1. Get Free API Keys

| Service | Get Key | Time |
|---------|---------|------|
| Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | 2 min |
| Pexels | [pexels.com/api](https://www.pexels.com/api/) | 2 min |
| Ayrshare | [ayrshare.com](https://www.ayrshare.com) → connect FB + IG | 10 min |
| Telegram | Message @BotFather → /newbot | 3 min |

### 2. Deploy to GitHub

1. Create a new repo called `social-autopilot`
2. Upload all files (keep folder structure)
3. **Settings → Secrets → Actions** — add these secrets:

| Secret | Value |
|--------|-------|
| `GEMINI_API_KEY` | Your Gemini key |
| `PEXELS_API_KEY` | Your Pexels key |
| `AYRSHARE_API_KEY` | Your Ayrshare key |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID |

### 3. Add Media

- Download 10+ BGM tracks from [pixabay.com/music](https://pixabay.com/music/) → put in `bgm/`
- Download 5 generic portrait clips from Pexels → put in `fallback_clips/`
- (Optional) Add `Montserrat-Bold.ttf` to `fonts/`

### 4. Test

- **Actions → "Daily Social Video" → Run workflow** (set dry_run = true first)
- Check your Telegram for the notification
- When happy, run again with dry_run = false

## 📅 Posting Schedule

| Day | UAE Time | UTC |
|-----|----------|-----|
| Monday | 8:00 AM | 04:00 |
| Tuesday | 12:00 PM | 08:00 |
| Wednesday | 6:00 PM | 14:00 |
| Thursday | 9:00 AM | 05:00 |
| Friday | 1:00 PM | 09:00 |
| Saturday | 10:00 AM | 06:00 |
| Sunday | 5:00 PM | 13:00 |

Edit the cron schedules in `.github/workflows/daily_video.yml` to change times.

## 🧪 DRY_RUN Mode

Test without posting:
- **Manual trigger:** Select `dry_run: true` when running workflow
- **Config:** Set `DRY_RUN = True` in config.py for local testing
- Video is generated and saved, but NOT posted to social media
- Telegram still sends a "DRY RUN" notification

## 🏢 Multi-Account Support

Add more brands in `config.py` → `BRAND_PROFILES`:

```python
BRAND_PROFILES = {
    "default": { ... },
    "brand2": {
        "channel_name": "Wealth Mastery",
        "ayrshare_key_env": "AYRSHARE_API_KEY_BRAND2",
        ...
    },
}
```

Set `BRAND_PROFILE=brand2` as an environment variable to use it.

## 📁 Project Structure

```
social-autopilot/
├── .github/workflows/daily_video.yml   # Cron scheduler
├── bgm/                    # Background music MP3s
├── fallback_clips/          # Emergency stock footage
├── fonts/                   # Custom fonts
├── data/
│   ├── backup_scripts.json  # 30 emergency fallback scripts
│   ├── content_calendar.json # Auto-managed niche/topic rotation
│   └── history.json         # Post log with analytics
├── scripts_archive/         # All generated scripts by date
├── config.py               # All settings in one place
├── utils.py                # Retry logic, JSON helpers
├── content_calendar.py     # Smart content rotation
├── generate_script.py      # AI script generation
├── generate_voice.py       # Text-to-speech
├── generate_video.py       # Video assembly
├── post_social.py          # Social media posting
├── notify.py               # Telegram notifications
├── history.py              # Post history tracking
├── main.py                 # Pipeline orchestrator
└── requirements.txt
```

## 🔄 Upgrade Path

| Component | Free → Paid | Monthly Cost |
|-----------|-------------|-------------|
| TTS | Edge TTS → ElevenLabs | +$5 |
| Video | FFmpeg → Creatomate API | +$18 |
| Avatar | None → HeyGen/D-ID | +$29 |
| Scripts | Gemini → Claude API | +$5 |
