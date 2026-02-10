import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# LLM API (OpenAI-compatible endpoint — works with OpenAI, Claude, local models)
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Business
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "My Business")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

# Database
DB_PATH = os.getenv("DB_PATH", "data/bizbot.db")

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
TOP_K = int(os.getenv("TOP_K", "3"))
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10"))
