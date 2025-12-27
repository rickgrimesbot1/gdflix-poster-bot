import os
from dotenv import load_dotenv

load_dotenv()

# Constants (read from environment; DO NOT hardcode secrets)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WORKERS_BASE = os.getenv("WORKERS_BASE", "https://gd.rickgrimesflix.workers.dev")
GDFLIX_API_KEY = os.getenv("GDFLIX_API_KEY", "")
GDFLIX_API_BASE = os.getenv("GDFLIX_API_BASE", "https://gdlink.dev/v2")
GDFLIX_FILE_BASE = os.getenv("GDFLIX_FILE_BASE", "https://gdlink.dev/file")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
DEV_LINK = os.getenv("DEV_LINK", "https://t.me/J1_CHANG_WOOK")
START_PHOTO_URL = os.getenv("START_PHOTO_URL", "")
HELP_PHOTO_URL = os.getenv("HELP_PHOTO_URL", "")
NETFLIX_API = os.getenv("NETFLIX_API", "https://nf.rickgrimesapi.workers.dev/?movieid=")
FREEIMAGE_API_KEY = os.getenv("FREEIMAGE_API_KEY", "")
FREEIMAGE_UPLOAD_API = os.getenv("FREEIMAGE_UPLOAD_API", "https://freeimage.host/api/1/upload")

OWNER_ID = int(os.getenv("OWNER_ID", "0")) if os.getenv("OWNER_ID") else None
ALLOWED_USERS = [int(x) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip().isdigit()]

# runtime set for authorized chats
AUTHORIZED_CHATS = set()