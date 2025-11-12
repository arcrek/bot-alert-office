# Quick Start Guide

Get your Office Telegram Bot running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.11+ or Docker installed
- [ ] Telegram account
- [ ] Google account with access to the target sheet

## Step 1: Get Telegram Bot Token (2 minutes)

1. Open Telegram, search for [@BotFather](https://t.me/BotFather)
2. Send: `/newbot`
3. Choose name: `Office Monitor Bot`
4. Choose username: `your_office_monitor_bot`
5. **Copy the token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Setup Google Sheets API (5 minutes)

1. Go to: https://console.cloud.google.com/
2. Create new project: `telegram-bot-project`
3. Enable API:
   - Search "Google Sheets API"
   - Click Enable
4. Create Service Account:
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Name: `telegram-bot`
   - Role: `Editor`
   - Create Key → JSON
5. **Download the JSON file**
6. Open your Google Sheet → Share → Add service account email (from JSON)

## Step 3: Configure Bot (1 minute)

1. Copy `google_credentials.json` to `credentials/` folder

2. Create `.env` file:
```bash
cp env.example .env
```

3. Edit `.env` and fill in your values:
```env
TELEGRAM_BOT_TOKEN=paste_your_bot_token_here
GOOGLE_SHEET_ID=paste_sheet_id_from_url
GOOGLE_CREDENTIALS_PATH=./credentials/google_credentials.json
TIMEZONE=Asia/Bangkok
CHECK_INTERVAL_MINUTES=15
```

**Get Sheet ID from URL:**
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
                                        ^^^^^^^^^^^^^^^^
```

**See `env.example` for detailed instructions!**

## Step 4: Run Bot

### With Docker (Recommended - Secure & Optimized):
```bash
docker-compose up -d
docker-compose logs -f
```

Docker container is:
- 🔒 Secure: Non-root user, read-only filesystem
- 📦 Lightweight: ~150MB total size
- ⚡ Fast: Starts in ~5 seconds

### Without Docker:
```bash
pip install -r requirements.txt
python -m bot.main
```

## Step 5: Activate Monitoring (30 seconds)

1. Add your bot to your Telegram group
2. In the group, send: `/startmon`
3. Done! Bot will check every 15 minutes

## Test It

Send `/check` in your group to manually trigger a check.

## Sheet Format

Make sure your Google Sheet has these columns:

| A (Email) | B (Password) | C (Type) | G (Date) | H (Days) | I (Time) |
|-----------|--------------|----------|----------|----------|----------|
| user@example.com | pass123 | 365 | 2025-11-12 | 0 | 15:30:00 |
| dev@example.com | pass456 | copilot | 2025-11-12 | 0 | 16:00:00 |

**Note:** Column C is optional. If it contains "copilot", the alert will say "Renew Copilot" instead of "Renew 365"

## Need Help?

See the full [README.md](README.md) for detailed instructions and troubleshooting.

## Commands Summary

- `/startmon` - Enable alerts for this group
- `/check` - Manual check
- `/renew user@example.com` - Manual renewal
- Reply "done" to alerts - Mark as renewed

