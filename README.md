# LinkedIn Comment Automation

Automated LinkedIn comment generation and posting bot.

## Overview

This tool monitors your LinkedIn feed, generates AI-powered comment drafts using proven LinkedIn engagement templates, and posts them on your behalf after approval.

## Features

- **Feed Monitoring**: Daily monitoring of posts matching your keywords
- **AI Comment Generation**: 3 variants per post using 2026 engagement templates
- **Approval Workflow**: Review before posting (or auto-approve)
- **Multi-platform API**: Uses Apify for fetching, Publora for publishing
- **Voice Profiles**: Match your commenting style (professional, analytical, casual, witty, nuanced)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LI_AT_COOKIE="your_linkedin_cookie"
export JSESSIONID_COOKIE="your_jsessionid"
export APIFY_TOKEN="your_apify_token"
export OPENROUTER_API_KEY="sk-or-..."
export PUBLORA_API_KEY="your_publora_key"

# Monitor feed (generates drafts for approval)
python main.py --tone professional

# Comment on a specific post
python main.py --post-url "https://www.linkedin.com/feed/update/..." --tone analytical

# Auto-post mode (no approval needed)
python main.py --auto-approve --tone witty
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LI_AT_COOKIE` | LinkedIn session cookie | Yes |
| `JSESSIONID_COOKIE` | LinkedIn session ID | Yes |
| `APIFY_TOKEN` | Apify API token for scraping | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI | Yes |
| `PUBLORA_API_KEY` | Publora key for publishing | No |
| `VOICE_PROFILE_PATH` | Path to voice profile JSON | No |

## GitHub Actions

The daily workflow runs automatically via `.github/workflows/daily-comments.yml`.

To manually trigger:
1. Go to Actions tab
2. Select "Daily LinkedIn Comment Bot"
3. Click "Run workflow"

## Comment Templates

Based on [linkedin-skills](https://github.com/sergebulaev/linkedin-skills) research:

| Code | Template | Best For |
|------|----------|----------|
| T1 | Missing-Piece | Platform posts, product critiques |
| T2 | Answer-the-Closing-Question | Posts ending with "?" |
| T3 | Data-First | Statistics-backed posts |
| T4 | Practitioner Observation | Experience sharing |
| T5 | Counter-with-Concession | Controversial takes |
| T6 | Quotable-Reframe | Wisdom posts |
| T7 | Ask-a-Sharper-Question | Question-posing posts |