import logging
import requests
from .config import GDFLIX_API_KEY, GDFLIX_API_BASE

logger = logging.getLogger("bot.gdflix")

def gdflix_share_file(file_id: str):
    if not GDFLIX_API_KEY or not GDFLIX_API_BASE:
        logger.warning("GDFLIX_API_KEY or GDFLIX_API_BASE not set")
        return None
    url = f"{GDFLIX_API_BASE}/share"
    params = {"key": GDFLIX_API_KEY, "id": file_id}
    try:
        r = requests.get(url, params=params, timeout=30, verify=False)
        r.raise_for_status()
        data = r.json()
        logger.info(f"GdFlix raw response for {file_id}: {data}")
        if data.get("error"):
            logger.warning(f"GdFlix error: {data.get('message')}")
            return None
        return data
    except Exception as e:
        logger.warning(f"GdFlix HTTP error: {e}")
        return None