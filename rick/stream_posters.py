import requests
import logging
import urllib.parse
from .tmdb import download_poster_bytes

logger = logging.getLogger("bot.stream_posters")

def fetch_json(url: str):
    try:
        r = requests.get(url, timeout=30)
    except Exception as e:
        return None, str(e)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    try:
        return r.json(), None
    except Exception:
        return None, "Invalid JSON"

def send_formatted_reply(msg, data, poster_label: str, portrait_label: str):
    title = data.get("title") or "Unknown"
    year = data.get("year") or data.get("release_year") or data.get("releaseYear") or data.get("date")
    full_title = f"{title} - ({year})" if year else title
    portrait = data.get("poster") or data.get("portrait") or data.get("vertical") or data.get("image")
    landscape = data.get("landscape") or data.get("backdrop") or data.get("horizontal") or data.get("cover")
    text = (
        f"<b>{poster_label} {landscape or 'Not Found'}</b>\n\n"
        f"<b>{portrait_label} {portrait or 'Not Found'}</b>\n\n"
        f"<b>{full_title}</b>\n\n"
        "<b><blockquote>Powered By: <a href='https://t.me/ott_posters_club'>Ott Posters Club 🎞️</a></blockquote></b>"
    )
    # caller should edit message or send new message; here just return text and landscape/portrait
    return text, landscape, portrait

async def handle_stream_poster(update, context, api_url: str, poster_label: str, portrait_label: str):
    msg = await update.message.reply_text("🔍 Fetching...")
    data, err = await context.application.run_in_executor(None, lambda: fetch_json(api_url))
    if err:
        return await msg.edit_text(f"❌ Failed: <code>{err}</code>", parse_mode="HTML")
    text, landscape, portrait = send_formatted_reply(msg, data, poster_label, portrait_label)
    await msg.edit_text(text=text, parse_mode="HTML", disable_web_page_preview=False)

# convenience wrappers for commands (call handle_stream_poster with appropriate API)
def _make_api(url):
    return lambda update, context: None  # placeholder in module; actual command functions in handlers import handle_stream_poster