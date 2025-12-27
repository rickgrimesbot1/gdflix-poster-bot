import requests
import logging
import re
from .config import TMDB_API_KEY

logger = logging.getLogger("bot.tmdb")

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

def pick_language(tmdb_lang_code, audio_lang):
    if audio_lang:
        return audio_lang
    code = (tmdb_lang_code or "").lower()
    if code in LANG_MAP:
        return LANG_MAP[code]
    if code:
        return code.upper()
    return "Unknown"

def tmdb_strict_match(raw_title: str, year: str):
    if not TMDB_API_KEY:
        logger.warning("TMDB_API_KEY not set")
        return None, None, None, None, None
    sxe = re.search(r"\bS(\d{1,2})E(\d{1,2})\b", raw_title, flags=re.IGNORECASE)
    if sxe:
        search_title = raw_title[:sxe.start()].strip()
    else:
        s_only = re.search(r"\bS(\d{1,2})\b", raw_title, flags=re.IGNORECASE)
        if s_only:
            search_title = raw_title[:s_only.start()].strip()
        else:
            search_title = raw_title.strip()
    if not search_title:
        search_title = raw_title.strip()
    have_year = year != "????"
    def search_movie():
        params = {"api_key": TMDB_API_KEY, "query": search_title, "include_adult": "false", "page": 1}
        if have_year:
            params["year"] = year
        try:
            r = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=10)
            if r.status_code != 200:
                logger.warning(f"TMDB movie HTTP {r.status_code}: {r.text[:200]}")
                return []
            data = r.json()
            results = data.get("results") or []
            if not have_year:
                return results
            exact = []
            for it in results:
                rd = it.get("release_date") or ""
                if rd[:4] == year:
                    exact.append(it)
            return exact
        except Exception as e:
            logger.warning(f"TMDB movie search failed: {e}")
            return []
    def search_tv():
        params = {"api_key": TMDB_API_KEY, "query": search_title, "include_adult": "false", "page": 1}
        if have_year:
            params["first_air_date_year"] = year
        try:
            r = requests.get("https://api.themoviedb.org/3/search/tv", params=params, timeout=10)
            if r.status_code != 200:
                logger.warning(f"TMDB tv HTTP {r.status_code}: {r.text[:200]}")
                return []
            data = r.json()
            results = data.get("results") or []
            if not have_year:
                return results
            exact = []
            for it in results:
                fd = it.get("first_air_date") or ""
                if fd[:4] == year:
                    exact.append(it)
            return exact
        except Exception as e:
            logger.warning(f"TMDB tv search failed: {e}")
            return []
    item = None
    ctype = None
    m_results = search_movie()
    if m_results:
        item = m_results[0]
        ctype = "movie"
    if not item:
        t_results = search_tv()
        if t_results:
            item = t_results[0]
            ctype = "tv"
    if not item and not have_year:
        try:
            r = requests.get("https://api.themoviedb.org/3/search/multi", params={"api_key": TMDB_API_KEY, "query": search_title, "include_adult": "false", "page": 1}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                res = data.get("results") or []
                if res:
                    item = res[0]
                    mt = item.get("media_type")
                    if mt in ("movie", "tv"):
                        ctype = mt
                    else:
                        ctype = "movie"
            else:
                logger.warning(f"TMDB multi HTTP {r.status_code}: {r.text[:200]}")
        except Exception as e:
            logger.warning(f"TMDB multi search failed: {e}")
    if not item:
        logger.warning(f"TMDB: no match for '{search_title}' ({year})")
        return None, None, None, None, None
    tmdb_id = item.get("id")
    tmdb_title = item.get("title") or item.get("name") or search_title
    if item.get("release_date"):
        tmdb_year = item["release_date"][:4]
    elif item.get("first_air_date"):
        tmdb_year = item["first_air_date"][:4]
    else:
        tmdb_year = year
    lang_code = item.get("original_language", "")
    poster_path = item.get("poster_path")
    poster_url = None
    if poster_path:
        poster_url = "https://image.tmdb.org/t/p/original" + poster_path
    tmdb_url = None
    if tmdb_id:
        if item.get("media_type") == "tv" or ctype == "tv":
            ctype = "tv"
        elif ctype is None:
            ctype = "movie"
        if ctype == "tv":
            tmdb_url = f"https://www.themoviedb.org/tv/{tmdb_id}"
        else:
            tmdb_url = f"https://www.themoviedb.org/movie/{tmdb_id}"
    return tmdb_title, tmdb_year, lang_code, poster_url, tmdb_url

def get_tmdb_backdrop_from_tmdb_url(tmdb_url: str):
    if not tmdb_url or not TMDB_API_KEY:
        return None
    m = re.search(r"themoviedb\.org/(movie|tv)/(\d+)", tmdb_url)
    if not m:
        return None
    ctype, tmdb_id = m.group(1), m.group(2)
    try:
        api_url = f"https://api.themoviedb.org/3/{ctype}/{tmdb_id}/images"
        params = {"api_key": TMDB_API_KEY, "include_image_language": "en,null"}
        r = requests.get(api_url, params=params, timeout=10)
        if r.status_code != 200:
            logger.warning(f"TMDB images HTTP {r.status_code}: {r.text[:200]}")
            return None
        data = r.json()
        backdrops = data.get("backdrops") or []
        if not backdrops:
            logger.warning("No TMDB backdrops found.")
            return None
        chosen = None
        for b in backdrops:
            if b.get("iso_639_1") == "en":
                chosen = b
                break
        if not chosen:
            for b in backdrops:
                if b.get("iso_639_1") in (None, "", "xx"):
                    chosen = b
                    break
        if not chosen:
            chosen = backdrops[0]
        file_path = chosen.get("file_path")
        if not file_path:
            return None
        url = "https://image.tmdb.org/t/p/original" + file_path
        logger.info(f"TMDB backdrop URL: {url}")
        return url
    except Exception as e:
        logger.warning(f"get_tmdb_backdrop_from_tmdb_url failed: {e}")
        return None

def download_poster_bytes(url: str):
    if not url:
        return None
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and r.content:
            return r.content
        logger.warning(f"Poster download HTTP {r.status_code}")
    except Exception as e:
        logger.warning(f"Poster download failed: {e}")
    return None