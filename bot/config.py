import os
from dotenv import load_dotenv
import pytz

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'SLOT OFFICE TRIAL')
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', './credentials/google_credentials.json')
TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Bangkok'))
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '15'))
WHITELIST_FILE = './data/whitelist.json'

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

if not GOOGLE_SHEET_ID:
    raise ValueError("GOOGLE_SHEET_ID is not set in environment variables")

