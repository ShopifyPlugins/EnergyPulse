import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ENTSO-E Transparency Platform
ENTSOE_API_KEY = os.getenv("ENTSOE_API_KEY", "")

# Default bidding zone (Germany/Luxembourg)
DEFAULT_BIDDING_ZONE = os.getenv("DEFAULT_BIDDING_ZONE", "DE_LU")

# LSTM model
MODEL_PATH = os.getenv("MODEL_PATH", "models/lstm_price.pt")
SEQUENCE_LENGTH = int(os.getenv("SEQUENCE_LENGTH", "168"))  # 7 days hourly
PREDICTION_HOURS = int(os.getenv("PREDICTION_HOURS", "24"))

# Scheduler
DAILY_FORECAST_HOUR = int(os.getenv("DAILY_FORECAST_HOUR", "20"))  # 20:00 Berlin
