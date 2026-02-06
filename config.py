"""
Social AutoPilot — Configuration (Production-Ready)
Supports multi-account, DRY_RUN mode, variable posting times,
niche-based theming, and rotating video styles.
"""

import os

# ============================================================
# GLOBAL FLAGS
# ============================================================

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
ACTIVE_PROFILE = os.environ.get("BRAND_PROFILE", "default")

# ============================================================
# BRAND PROFILES (multi-account future-proof)
# Add more profiles here — each gets its own name, handle,
# niches, Ayrshare key, etc. The ACTIVE_PROFILE flag above
# selects which one runs.
# ============================================================

BRAND_PROFILES = {
    "default": {
        "channel_name": "Daily Growth Hub",
        "tagline": "Grow Every Day",
        "watermark_text": "@dailygrowthhub",
        "logo_path": None,  # Set to e.g. "assets/logo.png" to overlay a logo
        "cta_text": "Follow for daily tips! 🔔",
        "ayrshare_key_env": "AYRSHARE_API_KEY",  # env var name
        "platforms": ["instagram", "facebook", "linkedin", "tiktok", "twitter"],
        "niches": [
            "health_wellness",
            "wealth_finance",
            "ecommerce_business",
            "mental_wellbeing",
        ],
    },
    # Example second brand — uncomment and fill in to use:
    # "brand2": {
    #     "channel_name": "Wealth Mastery",
    #     "tagline": "Build Wealth Daily",
    #     "watermark_text": "@wealthmastery",
    #     "logo_path": None,
    #     "cta_text": "Follow for money tips! 💰",
    #     "ayrshare_key_env": "AYRSHARE_API_KEY_BRAND2",
    #     "platforms": ["instagram", "facebook", "linkedin", "tiktok", "twitter"],
    #     "niches": ["wealth_finance"],
    # },
}


def get_profile():
    """Return the active brand profile dict."""
    return BRAND_PROFILES[ACTIVE_PROFILE]


# ============================================================
# NICHE DEFINITIONS
# ============================================================

NICHES = {
    "health_wellness": {
        "color": "#2ECC71",        # Green
        "color_name": "green",
        "text_color": "white",
        "accent": "#27AE60",
        "topics": [
            "morning routines for energy",
            "gut health secrets",
            "sleep optimization tips",
            "natural immunity boosters",
            "hydration and health",
            "benefits of walking daily",
            "stress and physical health",
            "anti-inflammatory foods",
            "posture and back pain",
            "breathing exercises for health",
            "intermittent fasting basics",
            "superfoods you should eat daily",
            "screen time and eye health",
            "cold shower benefits",
            "stretching for desk workers",
            "meal prep for busy people",
            "benefits of morning sunlight",
            "how sugar affects your body",
            "simple detox habits",
            "exercise without a gym",
        ],
        "base_hashtags": [
            "#healthtips", "#wellness", "#healthylifestyle",
            "#nutrition", "#selfcare", "#healthyliving",
            "#wellnesstips", "#holistichealth", "#fitlife",
            "#healthyhabits",
        ],
        "search_terms": [
            "healthy lifestyle", "wellness", "fitness",
            "nutrition", "health tips", "exercise", "yoga",
        ],
    },
    "wealth_finance": {
        "color": "#F1C40F",        # Gold
        "color_name": "gold",
        "text_color": "black",
        "accent": "#F39C12",
        "topics": [
            "compound interest explained simply",
            "budgeting rules that work",
            "passive income ideas for beginners",
            "investing mistakes to avoid",
            "emergency fund importance",
            "debt payoff strategies",
            "saving money on daily expenses",
            "side hustle ideas 2025",
            "financial freedom roadmap",
            "money mindset shifts",
            "understanding credit scores",
            "real estate investing basics",
            "stock market for beginners",
            "negotiating salary tips",
            "automating your savings",
            "frugal habits of millionaires",
            "how to start investing with little money",
            "avoiding lifestyle inflation",
            "building multiple income streams",
            "financial mistakes in your 20s and 30s",
        ],
        "base_hashtags": [
            "#financetips", "#moneytips", "#investing",
            "#personalfinance", "#wealthbuilding", "#financialfreedom",
            "#budgeting", "#passiveincome", "#moneymindset",
            "#financialliteracy",
        ],
        "search_terms": [
            "finance", "money", "investing",
            "wealth", "savings", "business success",
        ],
    },
    "ecommerce_business": {
        "color": "#3498DB",        # Blue
        "color_name": "blue",
        "text_color": "white",
        "accent": "#2980B9",
        "topics": [
            "starting an online store in 2025",
            "product photography tips",
            "social media marketing for small business",
            "email marketing basics",
            "customer retention strategies",
            "dropshipping pros and cons",
            "branding tips for small businesses",
            "pricing strategies that work",
            "turning followers into customers",
            "AI tools for business owners",
            "ecommerce SEO basics",
            "building trust with customers online",
            "content marketing for ecommerce",
            "best platforms for selling online",
            "scaling a one-person business",
            "writing product descriptions that sell",
            "handling negative reviews",
            "shipping and logistics simplified",
            "building an email list from scratch",
            "creating urgency without being pushy",
        ],
        "base_hashtags": [
            "#ecommerce", "#onlinebusiness", "#entrepreneur",
            "#smallbusiness", "#businesstips", "#digitalmarketing",
            "#hustle", "#startup", "#sidehustle",
            "#businessowner",
        ],
        "search_terms": [
            "business", "ecommerce", "entrepreneur",
            "startup", "marketing", "online store",
        ],
    },
    "mental_wellbeing": {
        "color": "#9B59B6",        # Purple
        "color_name": "purple",
        "text_color": "white",
        "accent": "#8E44AD",
        "topics": [
            "managing anxiety naturally",
            "building self-confidence",
            "digital detox benefits",
            "gratitude practice for happiness",
            "overcoming procrastination",
            "setting healthy boundaries",
            "mindfulness for beginners",
            "dealing with negative thoughts",
            "building resilience",
            "journaling for mental health",
            "morning affirmations that work",
            "letting go of perfectionism",
            "social media and mental health",
            "building positive habits",
            "finding purpose and meaning",
            "coping with loneliness",
            "how to stay motivated",
            "power of saying no",
            "overcoming self-doubt",
            "creating a calming evening routine",
        ],
        "base_hashtags": [
            "#mentalhealth", "#mindfulness", "#selfcare",
            "#anxiety", "#motivation", "#mentalhealthawareness",
            "#positivity", "#mindset", "#selfimprovement",
            "#growthmindset",
        ],
        "search_terms": [
            "meditation", "mindfulness", "calm",
            "peaceful", "mental health", "wellbeing", "nature",
        ],
    },
}

# ============================================================
# VIDEO STYLES (rotate daily for variety)
# ============================================================

VIDEO_STYLES = {
    "motivational_quote": {
        "description": "Inspirational quote with emotional buildup",
        "prompt_hint": "Start with a powerful quote. Build emotion. End with an actionable takeaway.",
        "text_position": "center",
        "text_size_multiplier": 1.2,
    },
    "listicle_tips": {
        "description": "Numbered tips (3-5 actionable points)",
        "prompt_hint": "Present 3-5 numbered tips. Each tip should be concise and actionable. Use a countdown or list format.",
        "text_position": "top",
        "text_size_multiplier": 1.0,
    },
    "story_narrative": {
        "description": "Mini-story that teaches a lesson",
        "prompt_hint": "Tell a short relatable story or scenario. Create tension, then resolve it with a lesson. Make it personal and emotional.",
        "text_position": "bottom",
        "text_size_multiplier": 1.0,
    },
    "did_you_know": {
        "description": "Surprising fact that hooks curiosity",
        "prompt_hint": "Start with 'Did you know...' or a shocking statistic. Then explain why it matters and what to do about it.",
        "text_position": "center",
        "text_size_multiplier": 1.1,
    },
    "problem_solution": {
        "description": "Present a common problem, then the solution",
        "prompt_hint": "Start by describing a frustrating problem the audience faces. Agitate the pain. Then present a clear, simple solution.",
        "text_position": "top",
        "text_size_multiplier": 1.0,
    },
}

# ============================================================
# VIDEO TECHNICAL SETTINGS
# ============================================================

VIDEO = {
    "duration_seconds": 55,
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "clip_duration": 6,
    "clips_per_video": 4,           # Download 3-4 clips and stitch
    "crossfade_duration": 0.8,      # Smooth crossfade between clips
    "ken_burns_zoom": 1.08,         # Slow zoom factor (1.0 = no zoom)
    "text_font_size": 52,
    "title_font_size": 64,
    "bgm_volume": 0.20,            # 20% BGM volume
    "voice_volume": 1.0,
    "audio_normalize": True,
}

# ============================================================
# VOICE SETTINGS (Edge TTS — free)
# ============================================================

VOICE = {
    "voice_id": "en-US-ChristopherNeural",
    "rate": "+5%",
    "pitch": "+0Hz",
}

# ============================================================
# POSTING SCHEDULE (variable times per day of week)
# All times in UTC. UAE (GST) = UTC+4, so subtract 4 hours.
# Mon 8AM UAE = 4AM UTC, etc.
# ============================================================

POSTING_SCHEDULE = {
    "Monday":    "04:00",   # 8 AM UAE
    "Tuesday":   "08:00",   # 12 PM UAE
    "Wednesday": "14:00",   # 6 PM UAE
    "Thursday":  "05:00",   # 9 AM UAE
    "Friday":    "09:00",   # 1 PM UAE
    "Saturday":  "06:00",   # 10 AM UAE
    "Sunday":    "13:00",   # 5 PM UAE
}

POSTING = {
    "caption_max_length": 2200,
    "ig_max_hashtags": 25,
    "fb_max_hashtags": 5,
}

# ============================================================
# RETRY SETTINGS
# ============================================================

RETRY = {
    "max_attempts": 3,
    "base_delay": 2,        # seconds — exponential backoff: 2, 4, 8
    "max_delay": 30,
}

# ============================================================
# FILE PATHS
# ============================================================

PATHS = {
    "bgm_dir": "bgm/",
    "fonts_dir": "fonts/",
    "temp_dir": "temp/",
    "output_dir": "output/",
    "fallback_clips_dir": "fallback_clips/",
    "scripts_archive_dir": "scripts_archive/",
    "backup_scripts": "data/backup_scripts.json",
    "content_calendar": "data/content_calendar.json",
    "history": "data/history.json",
}

# ============================================================
# SCRIPT GENERATION PROMPT (enhanced for virality)
# ============================================================

SCRIPT_PROMPT = """You are an elite viral social media scriptwriter who has generated
millions of views on Instagram Reels and Facebook Reels.

Create a {duration}-second video script.

TOPIC: {topic}
NICHE: {niche}
STYLE: {style_name} — {style_hint}

VIRAL RULES:
1. HOOK (first 3 seconds): Start with something that stops the scroll — a bold
   controversial statement, a shocking number, a relatable pain point, or a
   direct question. This is the MOST important part.
2. BODY: Deliver value using the {style_name} style. Use short punchy sentences.
   Create emotional peaks. Use contrast ("most people do X, but winners do Y").
3. CTA: End with a specific call-to-action — ask them to follow, save, or share.
   Make it feel urgent or exclusive.

EMOTIONAL STORYTELLING: Connect every point to how it FEELS, not just what it IS.
Use phrases like "imagine waking up...", "you know that feeling when...",
"here's what nobody tells you..."

TARGET: {word_count} words total for {duration} seconds of narration.

RESPOND ONLY IN THIS JSON FORMAT (no markdown, no backticks):
{{
    "hook": "The scroll-stopping opening line (max 15 words)",
    "body": [
        "Point 1 — 1-2 sentences",
        "Point 2 — 1-2 sentences",
        "Point 3 — 1-2 sentences",
        "Point 4 — 1-2 sentences (optional)"
    ],
    "cta": "Specific call-to-action closing line",
    "ig_caption": "Instagram caption with emojis, line breaks (\\n), value teaser, then CTA",
    "fb_caption": "Facebook caption — more conversational, storytelling tone, fewer hashtags",
    "title_text": "3-5 word on-screen title",
    "dynamic_hashtags": ["#tag1", "#tag2", "#tag3"]
}}
"""
