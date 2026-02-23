from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
KNOWN_CHATS = {
    "me": os.getenv("TELEGRAM_CHAT_ID"),
    "group": os.getenv("TELEGRAM_GROUP_ID"),
}
# TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")
GROQ_API_KEY =  os.getenv("GROQ_API_KEY")
SERPAPI_KEY= os.getenv("SERPAPI_KEY")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing from .env file")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_TOKEN is missing from .env file")

if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY is missing from .env file")

MAX_HISTORY = 20
RECENT_LOGS_DAYS = 1

MODEL_MAIN = "llama-3.3-70b-versatile"
MODEL_CLASSIFIER = "llama-3.1-8b-instant"

CONTEXT_BUDGETS = {
    "casual":    400,
    "tool":      600,
    "knowledge": 2000,
    "personal":  3000,
}
MAX_CONTEXT_TOKENS = 4000
MAX_TOOL_ITERATIONS = 5

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = "HarshitaJ02"

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID= os.getenv("NOTION_PAGE_ID")
NOTION_VERSION= "2022-06-28"

