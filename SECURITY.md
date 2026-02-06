# Security Policy

## How API Keys Are Protected

This project uses **GitHub Actions Secrets** to store all API keys securely.
Keys are **never** hardcoded in source code.

### Architecture

| Layer | Protection |
|-------|------------|
| Code | All keys loaded via `os.environ.get()` - zero hardcoded values |
| Storage | GitHub encrypted secrets (AES-256) |
| Runtime | Secrets injected as env vars only during workflow runs |
| Git | `.gitignore` blocks `.env`, `secrets.*`, `credentials.*`, `*.key`, `*.pem` |
| Push | GitHub Push Protection blocks commits containing detected secrets |
| Scanning | GitHub Secret Scanning alerts on accidental exposure |
| Logs | GitHub Actions automatically masks secret values in logs |

### Required Secrets

Add these in **Settings > Secrets and variables > Actions**:

| Secret Name | Source | Purpose |
|-------------|--------|--------|
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | AI script generation |
| `PEXELS_API_KEY` | [pexels.com/api](https://www.pexels.com/api/) | Stock video clips |
| `AYRSHARE_API_KEY` | [ayrshare.com](https://www.ayrshare.com) | Social media posting |
| `TELEGRAM_BOT_TOKEN` | @BotFather on Telegram | Notifications |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | Notification target |

### Security Rules

1. **Never** paste API keys into any `.py`, `.yml`, or `.json` file
2. **Never** share your `.env` file or commit it to git
3. **Always** use GitHub Secrets for CI/CD (encrypted at rest)
4. **Rotate** keys immediately if you suspect exposure
5. **Monitor** the Security tab for any alerts

### If a Key Is Exposed

1. Revoke the compromised key immediately at the provider's dashboard
2. Generate a new key
3. Update the GitHub Secret with the new value
4. Check GitHub's Security tab for any alerts

### Reporting Vulnerabilities

Use GitHub's private vulnerability reporting (enabled on this repo)
to report any security issues.
