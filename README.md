# Office Telegram Bot

A Telegram bot that monitors Google Sheets for expiring items and sends automatic alerts. The bot checks every 15 minutes for items that need renewal based on configured time and value thresholds.

## Features

- Automated monitoring every 15 minutes
- **Daily summary at 7:00 AM** - Get a complete list of all expired accounts (H <= 0) to focus on for the day
- **Quiet hours (22:30 PM - 7:00 AM)** - No alerts sent during night time to avoid disturbances
- Google Sheets integration
- Telegram alerts with formatted messages
- Group whitelist management
- Manual check and renewal commands
- Reply-based confirmation system
- Docker deployment ready
- UTC+7 timezone support

## Requirements

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Google Cloud Project with Sheets API enabled
- Telegram Bot Token
- Google Service Account credentials

## Tech Stack

- **python-telegram-bot** - Telegram bot framework
- **google-api-python-client** - Google Sheets API
- **APScheduler** - Job scheduling
- **Docker** - Containerization

## Project Structure

```
office-tele-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── handlers.py          # Telegram command handlers
│   ├── scheduler.py         # 15-minute check scheduler
│   ├── sheets_manager.py    # Google Sheets operations
│   ├── alert_manager.py     # Alert logic and formatting
│   └── config.py            # Configuration management
├── credentials/
│   └── google_credentials.json  # Google API credentials (you need to add this)
├── data/
│   └── whitelist.json       # Auto-generated whitelisted groups
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Google Cloud Setup

#### Enable Google Sheets API:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Library"
4. Search for "Google Sheets API"
5. Click "Enable"

#### Create Service Account:
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `telegram-bot-service`
   - ID: `telegram-bot-service`
4. Click "Create and Continue"
5. Grant role: "Editor" (or create custom role with Sheets access)
6. Click "Done"

#### Download Credentials:
1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" format
5. Download the file and save it as `credentials/google_credentials.json`

#### Share Google Sheet:
1. Open your Google Sheet
2. Click "Share" button
3. Add the service account email (found in the JSON file under `client_email`)
4. Give "Editor" permissions
5. Copy the Sheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

### 2. Telegram Bot Setup

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions:
   - Choose a name for your bot (e.g., "Office Monitor Bot")
   - Choose a username (must end in 'bot', e.g., "office_monitor_bot")
4. Copy the bot token provided by BotFather
5. Optional: Set bot description and profile picture using BotFather commands

### 3. Project Configuration

#### Clone or Download the Project:
```bash
cd "C:\Users\arcrek_T14g2\Desktop\office tele"
```

#### Create Environment File:

Copy the example file and edit it:
```bash
cp env.example .env
```

Or create a `.env` file in the project root with the following content:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
GOOGLE_SHEET_ID=your_sheet_id_from_url
GOOGLE_CREDENTIALS_PATH=./credentials/google_credentials.json
TIMEZONE=Asia/Bangkok
CHECK_INTERVAL_MINUTES=15
```

**Important:** Replace the placeholder values with your actual credentials.

See `env.example` for detailed instructions on obtaining each value.

#### Place Google Credentials:
Copy your downloaded `google_credentials.json` file to the `credentials/` folder.

### 4. Google Sheet Format

Your Google Sheet should have the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| A | Email | user@example.com |
| B | Password | SecretPass123 |
| C | Product Type (optional) | copilot / 365 / etc |
| G | Last Renewal Date | 2025-11-12 |
| H | Days Remaining (int) | 5 |
| I | Expiry Time (HH:MM:SS) | 15:30:00 |

**Alert Condition:** Bot sends alert when `H <= 0` AND `I < current_time` (UTC+7)

**Alert Title Logic:**
- If column C contains "copilot" (case-insensitive) → Alert shows "🔔 Renew Copilot:"
- Otherwise → Alert shows "🔔 Renew 365:"

## Deployment

### Option 1: Docker Deployment (Recommended)

The Docker container is optimized for:
- **Security**: Non-root user, read-only filesystem, dropped capabilities
- **Size**: ~150MB (Alpine) vs ~1GB (standard Python image)
- **Performance**: Fast startup, minimal resource usage

#### Build and Run:
```bash
docker-compose up -d
```

#### View Logs:
```bash
docker-compose logs -f
```

#### Stop Bot:
```bash
docker-compose down
```

#### Restart Bot:
```bash
docker-compose restart
```

#### Important: Data Directory Permissions

When deploying with Docker (especially on Linux or via Portainer), ensure the `data` directory has correct permissions:

```bash
# Set ownership to UID 1000 (matches container user)
sudo chown -R 1000:1000 ./data

# Set appropriate permissions
chmod -R 755 ./data
```

Without these permissions, the bot won't be able to save whitelisted groups to `data/whitelist.json`.

**See [DOCKER_SECURITY.md](DOCKER_SECURITY.md) for detailed security features and best practices.**

### Option 2: Local Python Deployment

#### Install Dependencies:
```bash
pip install -r requirements.txt
```

#### Run Bot:
```bash
python -m bot.main
```

## Bot Commands

### `/start`
Display welcome message and available commands.

**Usage:**
```
/start
```

### `/startmon`
Enable monitoring for the current group. Only whitelisted groups receive alerts.

**Usage:**
```
/startmon
```

**Note:** This command only works in groups, not in private chats.

### `/renew <email>`
Manually trigger renewal for a specific email address. Updates columns G (date) and I (time) in the sheet.

**Usage:**
```
/renew user@example.com
```

### `/check`
Manually run the check function to see if any alerts should be triggered.

**Usage:**
```
/check
```

### Reply "done"
Reply with the word "done" to any alert message to mark it as renewed.

**Usage:**
1. Bot sends an alert message
2. Reply to that message with: `done`
3. Bot updates the sheet automatically

## Alert Format

When an alert is triggered, the bot sends a message in this format:

**For Office 365:**
```
🔔 Renew 365:
Email: `user@example.com`
Password: `SecretPassword`
    - Email and password are copiable
Giờ hết hạn: 15:30:00
```

**For Copilot (when column C contains "copilot"):**
```
🔔 Renew Copilot:
Email: `user@example.com`
Password: `SecretPassword`
    - Email and password are copiable
Giờ hết hạn: 15:30:00
```

- Email and password are formatted as monospace (copyable)
- Time shown is from column I of the sheet
- Alert title changes based on column C content
- Emojis are only used in the message, not in code

### Daily Summary Format

**Sent every day at 7:00 AM UTC+7:**
```
📊 Daily Summary - 2025-12-05
Total expired accounts: 5
==============================

🤖 Copilot Accounts (2):
• user1@example.com - Expires: 14:30:00
• user2@example.com - Expires: 16:45:00

📦 Office 365 Accounts (3):
• user3@example.com - Expires: 09:15:00
• user4@example.com - Expires: 11:20:00
• user5@example.com - Expires: 18:00:00
```

- Shows all accounts where H <= 0 (regardless of time)
- Grouped by account type (Copilot vs Office 365)
- Helps teams plan their day and prioritize renewals

## Quiet Hours

The bot respects quiet hours to avoid disturbing users during night time:

- **Quiet Period:** 22:30 PM (10:30 PM) to 7:00 AM (UTC+7)
- **Behavior:** Regular 15-minute alert checks are skipped during this time
- **Daily Summary:** Still sent at 7:00 AM (marks the end of quiet hours)
- **Logging:** All skipped checks are logged for monitoring
- **Manual Commands:** `/check`, `/renew`, and reply "done" still work during quiet hours

**Example:**
- 22:25 PM - Alerts sent normally ✅
- 22:30 PM - Quiet hours begin, alerts skipped 🌙
- 11:00 PM - Check runs but no alerts sent (logged)
- 3:00 AM - Check runs but no alerts sent (logged)
- 7:00 AM - Daily summary sent, quiet hours end ☀️
- 7:15 AM - Regular alerts resume ✅

## How It Works

### Monitoring Cycle

1. **Every 15 minutes**, the bot automatically:
   - Checks if current time is within quiet hours (22:30 PM - 7:00 AM)
   - If in quiet hours, skips sending alerts (logs the skip)
   - If not in quiet hours, proceeds with normal checks:
     - Reads data from Google Sheet (columns A, B, C, G, H, I)
     - Checks each row for alert condition: `H <= 0` AND `I < current_time`
     - Determines alert type based on column C (Copilot or 365)
     - Sends alerts to all whitelisted groups
     - Tracks alert message IDs for reply handling

2. **Every day at 7:00 AM UTC+7**, the bot sends a daily summary:
   - Reads all rows from Google Sheet
   - Collects all accounts where `H <= 0` (ignores time comparison)
   - Groups accounts by type (Copilot vs Office 365)
   - Sends formatted summary to all whitelisted groups
   - Helps teams focus on what needs attention that day

3. **When user replies "done"**:
   - Bot identifies which row the alert belongs to
   - Updates column G with current date (UTC+7)
   - Updates column I with current time (UTC+7)
   - Sends confirmation message

4. **Manual renewal via `/renew`**:
   - Bot finds the row with matching email
   - Updates columns G and I
   - Sends confirmation message

## Troubleshooting

### Bot Not Starting

**Check credentials:**
```bash
docker-compose logs
```

Look for error messages about missing environment variables or invalid credentials.

**Verify .env file exists and contains correct values.**

### Not Receiving Alerts

1. **Check if group is whitelisted:**
   - Run `/startmon` in the group
   - Check `data/whitelist.json` file

2. **Verify sheet access:**
   - Ensure service account email is added to sheet with Editor permissions
   - Check if GOOGLE_SHEET_ID is correct

3. **Check sheet data:**
   - Verify columns H and I contain valid data
   - Ensure alert conditions are met (H <= 0, I < current_time)

### Google Sheets API Errors

**Permission Denied:**
- Share the sheet with the service account email
- Grant Editor permissions

**Invalid Credentials:**
- Verify `google_credentials.json` is valid
- Check if API is enabled in Google Cloud Console

**Quota Exceeded:**
- Google Sheets API has usage quotas
- Default: 500 requests per 100 seconds per project
- With 15-minute checks, this should be sufficient

### Docker Issues

**Port Already in Use:**
This bot doesn't expose ports, so this shouldn't be an issue.

**Data Volume Permission Errors (Docker/Portainer):**

If the bot can't save changes to `whitelist.json` when running in Docker (especially with Portainer stacks), it's likely a permission issue:

**Problem:** The container runs as user `botuser` (UID 1000, GID 1000) but the host directory doesn't have write permissions.

**Solution on Linux host:**
```bash
# Navigate to your project directory
cd /path/to/bot-alert-office

# Create data directory if it doesn't exist
mkdir -p data

# Create initial whitelist.json
cat > data/whitelist.json << 'EOF'
{
  "group_ids": []
}
EOF

# Set correct ownership (UID:GID 1000:1000)
sudo chown -R 1000:1000 data

# Set appropriate permissions
chmod -R 755 data
chmod 644 data/whitelist.json
```

**Verify permissions:**
```bash
ls -la data/
# Should show: drwxr-xr-x 2 1000 1000 ... for directory
#              -rw-r--r-- 1 1000 1000 ... for whitelist.json
```

**Note:** The docker-compose files include `:rw` flag on the data volume mount to ensure it's writable even when the container filesystem is read-only for security.

**General Permission Errors:**
```bash
sudo chown -R $USER:$USER ./data ./credentials
```

## Maintenance

### Update Bot Code

```bash
docker-compose down
git pull  # if using git
docker-compose build
docker-compose up -d
```

### Backup Whitelist

The whitelist is stored in `data/whitelist.json`. Back it up periodically:

```bash
cp data/whitelist.json data/whitelist.json.backup
```

### View Running Containers

```bash
docker ps
```

### Check Resource Usage

```bash
docker stats office-telegram-bot
```

## Security Considerations

1. **Never commit sensitive files:**
   - `.env`
   - `credentials/google_credentials.json`
   - `data/whitelist.json`

2. **Use environment variables** for all sensitive configuration

3. **Restrict Google Sheet access** to only the service account

4. **Keep bot token secure** - don't share it or commit it to version control

5. **Regularly rotate credentials** and update the bot configuration

## Logging

Logs include:
- Bot startup and initialization
- Alert checks and triggers (every 15 minutes)
- Quiet hours skips (22:30 PM - 7:00 AM)
- Daily summary checks (7:00 AM)
- Command executions
- Sheet updates
- Errors and exceptions

View logs:
```bash
# Docker
docker-compose logs -f

# Local
# Logs printed to console
```

## Requirements Summary

Based on project requirements:
- ✅ Telegram bot that monitors and sends alerts
- ✅ NO emoji use in code
- ✅ Emoji ONLY in telegram messages
- ✅ Docker deployable
- ✅ Detailed deploy instructions
- ✅ Google Sheet API integration
- ✅ Check every 15 minutes (columns H and I)
- ✅ Alert condition: H <= 0 AND I < current_time (UTC+7)
- ✅ **Quiet hours (22:30 PM - 7:00 AM)**: No alerts sent during night time
- ✅ **Daily summary at 7:00 AM**: All accounts with H <= 0 (regardless of time)
- ✅ Dynamic alert titles based on column C (Copilot vs 365)
- ✅ `/startmon` command for group whitelist
- ✅ `/renew <email>` command for manual updates
- ✅ `/check` command for manual checks
- ✅ "done" reply triggers update function
- ✅ Update function: Set G to current date, I to current time (UTC+7)

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs for error messages
3. Verify all setup steps are completed
4. Check Google Cloud Console for API issues

## License

This project is for internal office use.

