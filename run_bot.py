# run_bot.py
import os
import sys
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Ensure current directory is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

if __name__ == "__main__":
    # Check if Telegram bot token is set
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
        print("Error: TELEGRAM_BOT_TOKEN not set. Please add it to your .env file.")
        sys.exit(1)

    print("Starting ROK Server Notifier Bot...")
    from utils.telegram_bot import run_bot

    run_bot()