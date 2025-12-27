import re
import html
import urllib.parse
import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("bot.utils")

LANG_MAP = {
    "en": "English",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "hi": "Hindi",
    "kn": "Kannada",
    "mr": "Marathi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}

def scrape_appletv_page(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    script = soup.find("script", type="application/ld+json")
    if not script or not script.string:
        return None
    try:
        import json
        data = json.loads(script.string)
    except Exception:
        return None
    title = data.get("name", "Unknown")
    year = ""
    if data.get("datePublished"):
        year = data["datePublished"][:4]
    # Landscape
    landscape = "Not Found"
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        landscape = re.sub(r"/\d+x\d+\.jpg$", "/3840x2160.jpg", og["content"])
    # Portrait
    portrait = "Not Found"
    if data.get("image"):
        portrait = re.sub(r"/\d+x\d+\.jpg$", "/2000x3000.jpg", data["image"])
    return {"title": title, "year": year, "landscape": landscape, "portrait": portrait}

def is_allowed(user_id: int, allowed_users: list):
    if not allowed_users:
        return True
    return user_id in allowed_users

def change_quality(num):
    try:
        num = int(num)
    except Exception:
        return str(num)
    if num > 2160:
        return f"{num}p"
    elif num > 1080:
        return "2160p"
    elif num > 720:
        return "1080p"
    elif num > 540:
        return "720p"
    elif num > 480:
        return "540p"
    elif num > 360:
        return "480p"
    else:
        return f"{num}p"

def human_readable_size(size_bytes):
    try:
        size_bytes = int(size_bytes)
    except Exception:
        return "Unknown"
    if size_bytes <= 0:
        return "Unknown"
    gb = size_bytes / (1024 ** 3)
    if gb >= 1:
        return f"{gb:.1f}GB"
    mb = size_bytes / (1024 ** 2)
    return f"{mb:.1f}MB"

def parse_duration_to_seconds(dur: str):
    if not dur:
        return None
    try:
        h = m = s = 0
        mh = re.search(r'(\d+)\s*h', dur)
        if mh:
            h = int(mh.group(1))
        mm = re.search(r'(\d+)\s*(mn|min)', dur)
        if mm:
            m = int(mm.group(1))
        ms = re.search(r'(\d+)\s*s', dur)
        if ms:
            s = int(ms.group(1))
        total = h * 3600 + m * 60 + s
        if total > 0:
            return total
    except Exception:
        pass
    return None

def extract_bitrate_from_string(s: str):
    if not s:
        return None
    matches = re.findall(
        r'([0-9][0-9 .]*)(\s*(?:kb/s|kbps|Mb/s|mb/s|bits/s))',
        s,
        flags=re.IGNORECASE
    )
    if not matches:
        return None
    num, unit = matches[-1]
    num = num.replace(" ", "")
    unit = unit.lower().replace("kbps", "kb/s")
    return f"{num}{unit}"

def boldify_body(text: str) -> str:
    lines = text.splitlines()
    out = []
    for line in lines:
        if not line.strip():
            out.append("")
            continue
        esc = html.escape(line.rstrip())
        if esc.startswith("<b>") and esc.endswith("</b>"):
            out.append(esc)
        else:
            out.append(f"<b>{esc}</b>")
    return "\n".join(out)

def ensure_line_bold(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return line
    if stripped.startswith("<b>") and stripped.endswith("</b>"):
        return line
    return f"<b>{stripped}</b>"

def strip_extension(name: str) -> str:
    base = name.split("?")[0]
    m = re.match(r"^(.*)\.([A-Za-z0-9]{1,4})$", base)
    if m:
        return m.group(1)
    return base

def get_remote_size(url: str):
    try:
        r = requests.head(url, allow_redirects=True, timeout=20, verify=False)
        cl = r.headers.get("content-length") or r.headers.get("Content-Length")
        if cl:
            return int(cl)
    except Exception as e:
        logger.warning(f"HEAD size failed: {e}")
    return None

def is_gdrive_link(url: str) -> bool:
    return "drive.google.com" in (url or "")

def is_workers_link(url: str) -> bool:
    return "gd.rickgrimesflix.workers.dev" in (url or "")

def extract_workers_path(url: str):
    try:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or ""
        if "/0:" in path:
            return url
    except Exception:
        pass
    return None

def extract_drive_id(url: str):
    m = re.search(r"/file/d/([^/]+)", url or "")
    if m:
        return m.group(1)
    parsed = urllib.parse.urlparse(url or "")
    qs = urllib.parse.parse_qs(parsed.query)
    if "id" in qs and qs["id"]:
        return qs["id"][0]
    return None

def extract_drive_id_from_workers(url: str):
    parsed = urllib.parse.urlparse(url or "")
    qs = urllib.parse.parse_qs(parsed.query)
    if "id" in qs and qs["id"]:
        return qs["id"][0]
    return None

def workers_link_from_drive_id(file_id: str, workers_base: str):
    return f"{workers_base}/0:findpath?id={file_id}"

def make_full_bold(text: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            out.append("")
            continue
        if line.startswith("<b>") and line.endswith("</b>"):
            out.append(line)
        else:
            out.append(f"<b>{line}</b>")
    return "\n".join(out)

# helper used in manual poster handler (lifted out so it's testable)
def get_reply_base(message):
    return (message.reply_to_message.caption or message.reply_to_message.text) if (message.reply_to_message) else None

def build_header_from_text(base_text: str):
    # Accepts a header block text and applies the same filters as original
    if not base_text:
        return None
    parts = base_text.split("\n\n", 1)
    header_block = parts[0]
    header_lines = header_block.splitlines()
    filtered_lines = []
    for l in header_lines:
        s = l.strip()
        if not s:
            filtered_lines.append("")
            continue
        if "Language:" in s or "Source:" in s or s.startswith("🌐"):
            continue
        if s.startswith("📁") and (s == "📁" or s == "📁 "):
            continue
        s = re.sub(r"^📁\s*", "", s)
        s = re.sub(r"\s*-\s*\[", " [", s)
        filtered_lines.append(ensure_line_bold(s))
    if not any(line.strip() for line in filtered_lines):
        return None
    return "\n".join(filtered_lines)

def boldify_full_caption(base: str):
    lines = base.splitlines()
    out = []
    for l in lines:
        if l.strip():
            line = re.sub(r"\s*-\s*\[", " [", l)
            out.append(ensure_line_bold(line))
        else:
            out.append("")
    return "\n".join(out)