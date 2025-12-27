import re
import urllib.parse
from io import BytesIO
import requests
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from .config import (
    BOT_TOKEN, WORKERS_BASE, GDFLIX_FILE_BASE, DEV_LINK,
    START_PHOTO_URL, HELP_PHOTO_URL, OWNER_ID, ALLOWED_USERS, AUTHORIZED_CHATS,
    NETFLIX_API, FREEIMAGE_API_KEY, FREEIMAGE_UPLOAD_API
)
from .utils import (
    scrape_appletv_page, is_allowed, change_quality, human_readable_size,
    parse_duration_to_seconds, extract_bitrate_from_string, boldify_body,
    ensure_line_bold, strip_extension, get_remote_size, is_gdrive_link,
    is_workers_link, extract_workers_path, extract_drive_id, extract_drive_id_from_workers,
    workers_link_from_drive_id, make_full_bold, get_reply_base, build_header_from_text,
    boldify_full_caption
)
from .gdflix import gdflix_share_file
from .mediainfo import get_mediainfo_text, parse_file_info
from .tmdb import tmdb_strict_match, pick_language, get_tmdb_backdrop_from_tmdb_url, download_poster_bytes
from .stream_posters import handle_stream_poster, send_formatted_reply, fetch_json

logger = logging.getLogger("bot.handlers")

# --- Streaming wrappers use handle_stream_poster from stream_posters ---
async def amzn(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/amzn <primevideo url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://amzn.rickheroko.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "AMZN Poster:", "Portrait:")

async def airtel(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/airtel <airtel url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://hgbots.vercel.app/bypaas/airtel.php?url={encoded}"
    await handle_stream_poster(update, context, api, "AIRTEL Poster:", "Portrait:")

async def zee5(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/zee5 <zee5 url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://hgbots.vercel.app/bypaas/zee.php?url={encoded}"
    await handle_stream_poster(update, context, api, "ZEE5 Poster:", "Portrait:")

async def hulu(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/hulu <hulu url>")
        return
    user = update.effective_user
    if not is_allowed(user.id, ALLOWED_USERS):
        await update.message.reply_text("Not allowed.")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://hulu.rickheroko.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "Hulu Poster:", "")

async def viki(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/viki <viki.com url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://netflix.primejcw.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "VIKI Poster:", "Portrait:")

async def snxt(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/snxt <sunnxt url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://snxt.rickgrimesapi.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "SNXT Poster:", "Portrait:")

async def mmax(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/mmax <manoramamax url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://mmax.rickgrimesapi.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "ManoramaMax Poster:", "Portrait:")

async def aha_cmd(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/aha <aha url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://aha.rickgrimesapi.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "Aha Poster:", "Portrait:")

async def dsnp(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/dsnp <disney+ url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://dsnp.rickgrimesapi.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "Dsnp Poster:", "Portrait:")

async def apple(update, context):
    url = " ".join(context.args).strip()
    if not url:
        await update.message.reply_text("Usage:\n/apple <AppleTv url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://appletv.rickheroko.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "AppleTV Poster:", "Portrait:")

async def bms(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/bms <BookMyShow url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://bookmyshow-dcbots.jibinlal232.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "BookMyShow Poster:", "Portrait:")

async def iq(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/iq <IQIYI url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://iq.rickgrimesapi.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "iQIYI Poster:", "Portrait:")

async def hbo(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/hbo <HBOMAX url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://hbomax.rickgrimesapi.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "HBOMAX Poster:", "Portrait:")

async def up(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/UltraPlay <UltraPlay url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://ultraplay.rickheroko.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "UltraPlay Poster:", "Portrait:")

async def uj(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/UltraJhakaas <UltraJhakaas url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://ultrajhakaas.rickheroko.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "UltraJhakaas Poster:", "Portrait:")

async def wetv(update, context):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Usage:\n/wetv <wetv url>")
        return
    encoded = urllib.parse.quote_plus(url)
    api = f"https://wetv.the-zake.workers.dev/?url={encoded}"
    await handle_stream_poster(update, context, api, "WeTv Poster:", "Portrait:")

# ------------------------
# /nf Command (Netflix poster via worker) – URL or id
# ------------------------
async def nf(update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not is_allowed(user.id, ALLOWED_USERS):
        await update.message.reply_text("Not allowed.")
        return
    if chat.type in ("group", "supergroup") and chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("This group is not authorized.\nBot owner must send /authorize here.")
        return
    raw = " ".join(context.args).strip()
    if not raw:
        await update.message.reply_text("Usage:\n/nf <netflix url or id>")
        return
    movie_id = None
    if raw.startswith("http"):
        m = re.search(r"/title/(\d+)", raw)
        if m:
            movie_id = m.group(1)
    if not movie_id:
        if re.fullmatch(r"\d+", raw):
            movie_id = raw
        else:
            m = re.search(r"/title/(\d+)", raw)
            if m:
                movie_id = m.group(1)
    if not movie_id:
        await update.message.reply_text("Could not extract Netflix movie id.")
        return
    api_url = f"{NETFLIX_API}{movie_id}"
    status_msg = await update.message.reply_text("🔍 Fetching Netflix data…")
    try:
        r = requests.get(api_url, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await update.message.reply_text(f"❌ Netflix API error:\n<code>{str(e)}</code>", parse_mode="HTML")
        return
    portrait = data.get("portrait") or data.get("poster")
    landscape = data.get("landscape") or data.get("backdrop")
    title = data.get("title") or data.get("name") or "Unknown"
    year = data.get("year") or data.get("releaseYear") or "2025"
    def esc(v):
        return (v and (v)) or "Not Found"
    text = (
        f"<b>Netflix Poster:</b> <b>{esc(landscape)}</b>\n\n"
        f"<b>Portrait:</b> <b><a href='{esc(portrait)}'>Click</a></b>\n\n"
        f"<b>{esc(title)} ({esc(year)})</b>\n\n"
        "<b><blockquote>Powered By: <a href='https://t.me/ott_posters_club'>Ott Posters Club 🎞️</a></blockquote></b>"
    )
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=False)

# Image host (/host)
async def host_command(update, context):
    msg = update.message
    image_bytes = None
    if msg.reply_to_message and msg.reply_to_message.photo:
        photo = msg.reply_to_message.photo[-1]
        file = await photo.get_file()
        image_bytes = await file.download_as_bytearray()
    elif context.args:
        image_url = context.args[0]
        try:
            r = requests.get(image_url, timeout=20)
            if r.status_code != 200:
                await msg.reply_text("❌ Image download failed")
                return
            image_bytes = r.content
        except Exception:
            await msg.reply_text("❌ Invalid image URL")
            return
    else:
        await msg.reply_text("❌ Image reply or\n`/host <image_url>` uce", parse_mode=ParseMode.MARKDOWN)
        return
    status = await msg.reply_text("⏫ Uploading image...")
    try:
        files = {"source": ("image.jpg", image_bytes)}
        data = {"key": FREEIMAGE_API_KEY}
        res = requests.post(FREEIMAGE_UPLOAD_API, data=data, files=files, timeout=30)
        js = res.json()
        if js.get("success"):
            url = js["image"]["url"]
            await status.edit_text(f"✅ <b>Image Hosted Successfully</b>\n\n🔗 <code>{url}</code>", parse_mode=ParseMode.HTML, disable_web_page_preview=False)
        else:
            await status.edit_text("❌ Upload failed")
    except Exception as e:
        await status.edit_text(f"❌ Error:\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)

# Helpers: start/help/authorize/welcome etc.
async def start_command(update, context):
    user = update.effective_user
    name = user.first_name or "User"
    uid = user.id
    username = user.username
    if username:
        profile_url = f"https://t.me/{username}"
        profile_line = f"<b>Profile:</b> <a href=\"{profile_url}\">{profile_url}</a>\n"
    else:
        profile_line = ""
    text = (
        f"<b>Hello {name}!</b>\n"
        f"<b>User ID:</b> <code>{uid}</code>\n"
        f"{profile_line}\n"
        f"<b>I am a Google Drive to GDFlix TMDB Poster Generator Bot 🫨</b>\n\n"
        f"<b>/get</b> <b>Send Google Drive link, I will generate GDFlix link, TMDB poster and MediaInfo.</b>\n\n"
    )
    keyboard = [[InlineKeyboardButton("🤓 Bot Developer", url=DEV_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if START_PHOTO_URL:
        try:
            await update.message.reply_photo(photo=START_PHOTO_URL, caption=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            return
        except Exception:
            pass
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def help_command(update, context):
    text = (
        "<b>🤖 GDFlix TMDB Bot - Help</b>\n\n"
        "🟢 <b>Basic</b>\n"
        "/start - Show welcome message\n"
        "/help - Show this help menu\n"
        "/authorize - (Owner only) Authorize this group for /get, /info, /ls etc.\n\n"
        "Commands: /get, /info, /ls, /tmdb and streaming poster commands\n    "
    )
    keyboard = [[InlineKeyboardButton("🤓 Bot Developer", url=DEV_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if HELP_PHOTO_URL:
        try:
            await update.message.reply_photo(photo=HELP_PHOTO_URL, caption=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            return
        except Exception:
            pass
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def my_chat_member_handler(update, context):
    chat_member = update.my_chat_member
    chat = chat_member.chat
    old_status = chat_member.old_chat_member.status
    new_status = chat_member.new_chat_member.status
    bot_id = context.bot.id
    if chat.type in ("group", "supergroup"):
        if chat_member.new_chat_member.user.id == bot_id:
            if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
                text = (
                    f"<b>Hello {chat.title} 👋</b>\n\n"
                    f"<b>I am a Google Drive to GDFlix TMDB Poster Generator Bot 🫨</b>\n\n"
                    f"<b>Owner must use /authorize in this group first.</b>\n"
                )
                keyboard = [[InlineKeyboardButton("🤓 Bot Developer", url=DEV_LINK)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if START_PHOTO_URL:
                    try:
                        await chat.send_photo(photo=START_PHOTO_URL, caption=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                        return
                    except Exception:
                        pass
                await chat.send_message(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def authorize_command(update, context):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("Use /authorize inside the group you want to authorize.")
        return
    if OWNER_ID and user.id != OWNER_ID:
        await update.message.reply_text("Only bot owner can authorize this group.")
        return
    AUTHORIZED_CHATS.add(chat.id)
    await update.message.reply_text("<b>Authorized!</b> Enjoy 😎", parse_mode=ParseMode.HTML)

# /get command (port of original: GDrive -> GdFlix + TMDB + MediaInfo)
async def get_command(update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not is_allowed(user.id, ALLOWED_USERS):
        await update.message.reply_text("Not allowed.")
        return
    if chat.type in ("group", "supergroup") and chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("This group is not authorized.\nBot owner must send /authorize here.")
        return
    if not context.args:
        await update.message.reply_text("Usage:\n/get <one or more links>")
        return
    all_text = update.message.text or ""
    parts = all_text.split()
    urls = [p for p in parts if p.startswith("http")]
    if not urls:
        await update.message.reply_text("No valid links found.")
        return
    if len(urls) > 8:
        await update.message.reply_text("Maximum 8 links allowed in one /get.")
        return
    status_msg = await update.message.reply_text("Wait :- 50%\n▰▰▰▰▰▱▱▱▱▱")
    try:
        drive_ids = []
        media_source_url = None
        for url in urls:
            if is_gdrive_link(url):
                did = extract_drive_id(url)
                if did:
                    drive_ids.append(did)
            elif is_workers_link(url):
                did = extract_drive_id_from_workers(url)
                if did:
                    drive_ids.append(did)
                else:
                    wpath = extract_workers_path(url)
                    if wpath and media_source_url is None:
                        media_source_url = wpath
        items = []
        first_name_for_tmdb = None
        first_size_bytes = None
        for did in drive_ids:
            gd_res = gdflix_share_file(did)
            if not gd_res:
                continue
            raw_name = gd_res.get("name") or "Unknown"
            display_name = strip_extension(raw_name)
            size = gd_res.get("size") or 0
            size_str = human_readable_size(size)
            key = gd_res.get("key")
            if key:
                link = f"{GDFLIX_FILE_BASE}/{key}"
            else:
                link = f"{GDFLIX_FILE_BASE}/{did}"
            items.append({"id": did, "name": display_name, "size_str": size_str, "size_bytes": size, "link": link})
            if not first_name_for_tmdb:
                first_name_for_tmdb = raw_name
            if first_size_bytes is None:
                first_size_bytes = size
        if not media_source_url:
            first_drive_id = None
            if items:
                first_drive_id = items[0]["id"]
            elif drive_ids:
                first_drive_id = drive_ids[0]
            if first_drive_id:
                media_source_url = workers_link_from_drive_id(first_drive_id, WORKERS_BASE)
        if not media_source_url and not items:
            try:
                await status_msg.delete()
            except Exception:
                pass
            await update.message.reply_text("No valid GdFlix data or workers link to read media info.")
            return
        parsed_mediainfo = ""
        org_aud_lang = None
        if media_source_url:
            mediainfo_text = get_mediainfo_text(media_source_url)
            if mediainfo_text:
                parsed_mediainfo, org_aud_lang = parse_file_info(mediainfo_text, file_size=first_size_bytes)
                if not first_name_for_tmdb:
                    m = re.search(r"Complete name\s*:\s*(.+)", mediainfo_text)
                    if m:
                        first_name_for_tmdb = m.group(1).strip()
        final_title = "Unknown"
        final_year = "????"
        final_lang = pick_language(None, org_aud_lang)
        poster_url = None
        tmdb_url = None
        if first_name_for_tmdb:
            base_title, file_year = strip_extension(first_name_for_tmdb), "????"
            # try to extract year from filename
            base_title, file_year = (lambda n: __import__("re").sub(r"[._]+", " ", n).strip(), "????")(first_name_for_tmdb)  # minimal safe fallback
            # use extract_title_year_from_filename logic if needed; simplified here:
            base_title, file_year = (first_name_for_tmdb, "????")
            tmdb_title, tmdb_year, tmdb_lang_code, poster_url, tmdb_url = tmdb_strict_match(base_title, file_year)
            final_title = tmdb_title or base_title or "Unknown"
            final_year = tmdb_year or file_year or "????"
            final_lang = pick_language(tmdb_lang_code, org_aud_lang)
        header_lines = [f"<b>🎬 {final_title} - ({final_year})</b>"]
        lines = []
        lines.extend(header_lines)
        lines.append("")
        for it in items:
            lines.append(f"<b>{it['name']} [{it['size_str']}]</b>")
            lines.append(f"<b>{it['link']}</b>")
            lines.append("")
        if not items and media_source_url:
            try:
                fname = urllib.parse.unquote(urllib.parse.urlparse(media_source_url).path.rsplit("/", 1)[-1])
                display_name = strip_extension(fname)
            except Exception:
                display_name = "Unknown"
            size_bytes = get_remote_size(media_source_url)
            size_str = human_readable_size(size_bytes) if size_bytes else "Unknown"
            lines.append(f"<b>{display_name} [{size_str}]</b>")
            lines.append(f"<b>{media_source_url}</b>")
            lines.append("")
        if parsed_mediainfo:
            lines.append(parsed_mediainfo.rstrip())
        msg = "\n".join(lines)
        msg = re.sub(r" {2,}", " ", msg)
        context.chat_data["last_caption"] = msg
        context.chat_data["tmdb_header"] = "\n".join(header_lines)
        try:
            await status_msg.delete()
        except Exception:
            pass
        poster_bytes = download_poster_bytes(poster_url) if poster_url else None
        if poster_bytes:
            bio = BytesIO(poster_bytes)
            bio.name = "poster.jpg"
            await update.message.reply_photo(photo=bio, caption=msg, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.warning(f"/get failed: {e}")
        try:
            await status_msg.delete()
        except Exception:
            pass
        await update.message.reply_text(f"⚠️ Something went wrong.\n\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)

# /info command
async def info_command(update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not is_allowed(user.id, ALLOWED_USERS):
        await update.message.reply_text("Not allowed.")
        return
    if chat.type in ("group", "supergroup") and chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("This group is not authorized.\nBot owner must send /authorize here.")
        return
    if not context.args:
        await update.message.reply_text("Usage:\n/info <direct download link>")
        return
    parts = (update.message.text or "").split()
    urls = [p for p in parts if p.startswith("http")]
    if not urls:
        await update.message.reply_text("No valid link found.")
        return
    url = urls[0]
    status_msg = await update.message.reply_text("Wait :- 50%\n▰▰▰▰▰▱▱▱▱▱")
    try:
        size_bytes = get_remote_size(url)
        size_str = human_readable_size(size_bytes) if size_bytes else "Unknown"
        mediainfo_text = get_mediainfo_text(url)
        if not mediainfo_text:
            try:
                await status_msg.delete()
            except Exception:
                pass
            await update.message.reply_text("Could not read media info from this link.")
            return
        parsed_mediainfo, org_aud_lang = parse_file_info(mediainfo_text, file_size=size_bytes)
        filename = None
        m = re.search(r"Complete name\s*:\s*(.+)", mediainfo_text)
        if m:
            filename = m.group(1).strip()
        if not filename:
            parsed = urllib.parse.urlparse(url)
            filename = urllib.parse.unquote(parsed.path.rsplit("/", 1)[-1]) or "Unknown"
        display_name = strip_extension(filename)
        base_title, file_year = (display_name, "????")
        tmdb_title, tmdb_year, tmdb_lang_code, poster_url, tmdb_url = tmdb_strict_match(base_title, file_year)
        final_title = tmdb_title or base_title or "Unknown"
        final_year = tmdb_year or file_year or "????"
        final_lang = pick_language(tmdb_lang_code, org_aud_lang)
        header_lines = [f"<b>🎬 {final_title} - ({final_year})</b>"]
        lines = []
        lines.extend(header_lines)
        lines.append("")
        lines.append(f"<b>{display_name} [{size_str}]</b>")
        lines.append("")
        if parsed_mediainfo:
            lines.append(parsed_mediainfo.rstrip())
        msg = "\n".join(lines)
        msg = re.sub(r" {2,}", " ", msg)
        context.chat_data["last_caption"] = msg
        context.chat_data["tmdb_header"] = "\n".join(header_lines)
        try:
            await status_msg.delete()
        except Exception:
            pass
        poster_bytes = download_poster_bytes(poster_url) if poster_url else None
        if poster_bytes:
            bio = BytesIO(poster_bytes)
            bio.name = "poster.jpg"
            await update.message.reply_photo(photo=bio, caption=msg, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.warning(f"/info failed: {e}")
        try:
            await status_msg.delete()
        except Exception:
            pass
        await update.message.reply_text(f"⚠️ /info failed.\n\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)

# /ls command
async def ls_command(update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not is_allowed(user.id, ALLOWED_USERS):
        await update.message.reply_text("Not allowed.")
        return
    if chat.type in ("group", "supergroup") and chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("This group is not authorized.\nBot owner must send /authorize here.")
        return
    if not context.args:
        await update.message.reply_text("Usage:\n/ls <Google Drive link or workers path>")
        return
    parts = (update.message.text or "").split()
    urls = [p for p in parts if p.startswith("http")]
    if not urls:
        await update.message.reply_text("No valid link found.")
        return
    url = urls[0]
    if not (is_gdrive_link(url) or is_workers_link(url)):
        await update.message.reply_text("Only Google Drive or workers links are supported for /ls.")
        return
    status_msg = await update.message.reply_text("Wait :- 50%\n▰▰▰▰▰▱▱▱▱▱")
    try:
        drive_id = None
        is_workers_path = False
        if is_gdrive_link(url):
            drive_id = extract_drive_id(url)
        elif is_workers_link(url):
            drive_id = extract_drive_id_from_workers(url)
            if not drive_id and extract_workers_path(url):
                is_workers_path = True
        if not drive_id and not is_workers_path:
            try:
                await status_msg.delete()
            except Exception:
                pass
            await update.message.reply_text("Could not extract Drive ID from this link.")
            return
        gd_res = None
        raw_name = None
        display_name = None
        size = 0
        gdlink = None
        if drive_id:
            gd_res = gdflix_share_file(drive_id)
            if not gd_res:
                try:
                    await status_msg.delete()
                except Exception:
                    pass
                await update.message.reply_text("GdFlix did not return any data for this file.")
                return
            raw_name = gd_res.get("name") or "Unknown"
            display_name = strip_extension(raw_name)
            size = gd_res.get("size") or 0
            key = gd_res.get("key")
            if key:
                gdlink = f"{GDFLIX_FILE_BASE}/{key}"
            else:
                gdlink = f"{GDFLIX_FILE_BASE}/{drive_id}"
        else:
            gdlink = url
            fname = urllib.parse.unquote(urllib.parse.urlparse(url).path.rsplit("/", 1)[-1])
            raw_name = fname or "Unknown"
            display_name = strip_extension(raw_name)
            size = get_remote_size(url) or 0
        if drive_id:
            media_source_url = workers_link_from_drive_id(drive_id, WORKERS_BASE)
        else:
            media_source_url = url
        parsed_mediainfo = ""
        org_aud_lang = None
        mediainfo_text = get_mediainfo_text(media_source_url)
        if mediainfo_text:
            parsed_mediainfo, org_aud_lang = parse_file_info(mediainfo_text, file_size=size)
        base_title, file_year = strip_extension(raw_name), "????"
        tmdb_title, tmdb_year, tmdb_lang_code, poster_url_unused, tmdb_url = tmdb_strict_match(base_title, file_year)
        final_title = tmdb_title or base_title or "Unknown"
        final_year = tmdb_year or file_year or "????"
        final_lang = pick_language(tmdb_lang_code, org_aud_lang)
        backdrop_url = get_tmdb_backdrop_from_tmdb_url(tmdb_url) if tmdb_url else None
        header_lines = [f"<b>🎬 {final_title} - ({final_year})</b>"]
        lines = []
        lines.extend(header_lines)
        lines.append("")
        lines.append(f"<b>{display_name} [{human_readable_size(size)}]</b>")
        lines.append(f"<b>{gdlink}</b>")
        lines.append("")
        if parsed_mediainfo:
            lines.append(parsed_mediainfo.rstrip())
        msg = "\n".join(lines)
        msg = re.sub(r" {2,}", " ", msg)
        context.chat_data["last_caption"] = msg
        context.chat_data["tmdb_header"] = "\n".join(header_lines)
        try:
            await status_msg.delete()
        except Exception:
            pass
        poster_bytes = download_poster_bytes(backdrop_url) if backdrop_url else None
        if poster_bytes:
            bio = BytesIO(poster_bytes)
            bio.name = "backdrop.jpg"
            await update.message.reply_photo(photo=bio, caption=msg, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.warning(f"/ls failed: {e}")
        try:
            await status_msg.delete()
        except Exception:
            pass
        await update.message.reply_text(f"⚠️ /ls failed.\n\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)

# /tmdb command
async def tmdb_command(update, context):
    if not context.args:
        await update.message.reply_text("Usage:\n/tmdb <title/year or TMDB URL>")
        return
    raw = " ".join(context.args).strip()
    tmdb_title = None
    tmdb_year = "????"
    lang_code = None
    poster_url = None
    tmdb_url = None
    try:
        if raw.startswith("http") and "themoviedb.org" in raw:
            m = re.search(r"themoviedb\.org/(movie|tv)/(\d+)", raw)
            if not m:
                await update.message.reply_text("Invalid TMDB URL.")
                return
            ctype, tmdb_id = m.group(1), m.group(2)
            api_url = f"https://api.themoviedb.org/3/{ctype}/{tmdb_id}"
            r = requests.get(api_url, params={"api_key": __import__("os").getenv("TMDB_API_KEY")}, timeout=10)
            if r.status_code != 200:
                await update.message.reply_text(f"TMDB error: HTTP {r.status_code}")
                return
            data = r.json()
            tmdb_title = data.get("title") or data.get("name") or "Unknown"
            if data.get("release_date"):
                tmdb_year = data["release_date"][:4]
            elif data.get("first_air_date"):
                tmdb_year = data["first_air_date"][:4]
            lang_code = data.get("original_language", "")
            poster_path = data.get("poster_path")
            if poster_path:
                poster_url = "https://image.tmdb.org/t/p/original" + poster_path
            tmdb_url = f"https://www.themoviedb.org/{ctype}/{tmdb_id}"
        else:
            query = raw
            m = re.search(r"(19|20)\d{2}", query)
            if m:
                year = m.group(0)
                title = query[:m.start()].strip()
            else:
                year = "????"
                title = query.strip()
            if not title:
                title = query.strip()
            t_title, t_year, t_lang, poster_url, tmdb_url = tmdb_strict_match(title, year)
            tmdb_title = t_title or title or "Unknown"
            tmdb_year = t_year or year or "????"
            lang_code = t_lang
        final_lang = pick_language(lang_code, None)
        header_lines = [f"<b>🎬 {tmdb_title} - ({tmdb_year})</b>"]
        caption = "\n".join(header_lines)
        caption = re.sub(r" {2,}", " ", caption)
        context.chat_data["last_caption"] = caption
        context.chat_data["tmdb_header"] = "\n".join(header_lines)
        poster_bytes = download_poster_bytes(poster_url) if poster_url else None
        if poster_bytes:
            bio = BytesIO(poster_bytes)
            bio.name = "poster.jpg"
            await update.message.reply_photo(photo=bio, caption=caption, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.warning(f"/tmdb failed: {e}")
        await update.message.reply_text(f"⚠️ TMDB lookup failed.\n\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)

# Manual poster handler (photo with caption)
async def manual_poster_handler(update, context):
    msg = update.message
    if not msg or not msg.photo:
        return
    is_reply = msg.reply_to_message is not None
    body = msg.caption
    caption_to_send = None
    def get_reply_base_local():
        if not is_reply:
            return None
        rt = msg.reply_to_message
        return rt.caption or rt.text
    if body:
        if is_reply:
            header = build_header_from_text(context.chat_data.get("tmdb_header") or get_reply_base_local())
            body_bold = boldify_body(body)
            if header:
                caption_to_send = header + "\n\n" + body_bold
            else:
                caption_to_send = body_bold
        else:
            caption_to_send = boldify_body(body)
    else:
        base = None
        if context.chat_data.get("last_caption"):
            base = context.chat_data["last_caption"]
        elif is_reply:
            base = get_reply_base_local()
        if base:
            caption_to_send = boldify_full_caption(base)
        else:
            await msg.reply_text("First use /tmdb or /get (or send caption) then send poster photo 🙂")
            return
    photo = msg.photo[-1]
    await msg.chat.send_photo(photo=photo.file_id, caption=caption_to_send, parse_mode=ParseMode.HTML)

# rk (repost streaming poster) — simplified; uses make_full_bold
async def rk(update, context):
    msg = update.message
    if not msg.reply_to_message:
        await msg.reply_text("❌ /rk must be used as reply to /get post")
        return
    if not context.args:
        await msg.reply_text("❌ Usage:\n/rk <streaming link>")
        return
    stream_url = context.args[0]
    raw_caption = msg.reply_to_message.caption or msg.reply_to_message.text
    if not raw_caption:
        await msg.reply_text("❌ Replied message has no caption")
        return
    base_caption = make_full_bold(raw_caption)
    status = await msg.reply_text("🔍 Fetching streaming poster...")
    encoded = urllib.parse.quote_plus(stream_url)
    api_map = {
        "netflix.com": f"https://nf.rickgrimesapi.workers.dev/?url={encoded}",
        "primevideo.com": f"https://amzn.rickheroko.workers.dev/?url={encoded}",
        "sunnxt.com": f"https://snxt.rickgrimesapi.workers.dev/?url={encoded}",
        "zee5.com": f"https://hgbots.vercel.app/bypaas/zee.php?url={encoded}",
        "aha.video": f"https://aha.rickgrimesapi.workers.dev/?url={encoded}",
        "manoramamax.com": f"https://mmax.rickgrimesapi.workers.dev/?url={encoded}",
        "viki.com": f"https://netflix.primejcw.workers.dev/?url={encoded}",
        "iq.com": f"https://iq.rickgrimesapi.workers.dev/?url={encoded}",
        "hbomax.com": f"https://hbomax.rickgrimesapi.workers.dev/?url={encoded}",
        "apple.com": f"https://appletv.rickheroko.workers.dev/?url={encoded}",
        "disneyplus.com": f"https://dsnp.rickgrimesapi.workers.dev/?url={encoded}",
        "ultraplay": f"https://ultraplay.rickgrimesapi.workers.dev/?url={encoded}",
    }
    api_url = None
    for key, api in api_map.items():
        if key in stream_url:
            api_url = api
            break
    if not api_url:
        await status.edit_text("❌ Unsupported streaming platform")
        return
    try:
        r = requests.get(api_url, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        await status.edit_text(f"❌ API error\n<code>{e}</code>", parse_mode=ParseMode.HTML)
        return
    landscape = data.get("landscape") or data.get("backdrop") or data.get("horizontal")
    if not landscape:
        await status.edit_text("❌ Landscape poster not found")
        return
    poster_bytes = download_poster_bytes(landscape)
    if not poster_bytes:
        await status.edit_text("❌ Poster download failed")
        return
    bio = BytesIO(poster_bytes)
    bio.name = "streaming_landscape.jpg"
    await status.delete()
    await msg.reply_to_message.reply_photo(photo=bio, caption=base_caption, parse_mode=ParseMode.HTML)