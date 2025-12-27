import subprocess
import tempfile
import os
import logging
import requests
from .utils import parse_duration_to_seconds, extract_bitrate_from_string

logger = logging.getLogger("bot.mediainfo")

def get_mediainfo_text(url: str):
    temp_path = None
    target = url
    try:
        if url.startswith("http://") or url.startswith("https://"):
            logger.info(f"Downloading partial data for mediainfo from: {url}")
            r = requests.get(url, stream=True, timeout=60, verify=False)
            r.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
                temp_path = f.name
                downloaded = 0
                limit = 50 * 1024 * 1024
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if downloaded >= limit:
                        break
            target = temp_path
        out = subprocess.check_output(["mediainfo", target], stderr=subprocess.STDOUT)
        return out.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"mediainfo failed: {e}")
        return None
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def parse_file_info(TEXT, no_vid=False, file_size=None):
    if not TEXT:
        return None, None
    try:
        tracks = TEXT.split('\n\n')
    except Exception:
        return None, None
    VIDEO_CODEC_MAP = {"AVC": "H.264", "HEVC": "H.265", "VP9": "VP9", "AV1": "AV1"}
    AUDIO_CODEC_MAP = {'E-AC-3 JOC': 'DDPA', "E-AC-3": "DDP", "AC-3": "DD", "AAC LC": "AAC"}
    output = []
    raw_blocks = []
    for track in tracks:
        values = {}
        for line in track.split('\n'):
            try:
                key, value = line.split(':', 1)
                values[key.strip()] = value.strip()
            except Exception:
                pass
        if values:
            output.append(values)
            raw_blocks.append(track)
    general_track = None
    video_track = None
    for d in output:
        if not general_track and 'Duration' in d:
            general_track = d
        if not video_track and ('Height' in d or 'Width' in d or d.get('Format') in VIDEO_CODEC_MAP):
            video_track = d
    duration_seconds = None
    if general_track and 'Duration' in general_track:
        dur = general_track['Duration']
        duration_seconds = parse_duration_to_seconds(dur)
    AUDIOS = []
    IDX = 1
    for idx, i in enumerate(output):
        if 'Channel(s)' in i:
            raw_block = raw_blocks[idx]
            CHANNELS = i['Channel(s)'].replace(' channels', '')
            if CHANNELS == '2':
                CHANNELS = '2.0'
            if CHANNELS == '6':
                CHANNELS = '5.1'
            if CHANNELS == '8':
                CHANNELS = '7.1'
            BITRATE = ''
            LANGUAGE = ''
            CODEC = ''
            for k, v in i.items():
                lk = k.lower()
                if 'bit rate' in lk or 'bitrate' in lk:
                    candidate = extract_bitrate_from_string(v)
                    if candidate:
                        BITRATE = candidate
                        break
            if not BITRATE:
                candidate = extract_bitrate_from_string(raw_block)
                if candidate:
                    BITRATE = candidate
            if 'Language' in i:
                LANGUAGE = i['Language']
            if 'Format' in i:
                try:
                    CODEC = AUDIO_CODEC_MAP.get(i['Format'])
                    if not CODEC:
                        CODEC = i['Format']
                except Exception:
                    CODEC = i['Format']
                if 'Commercial name' in i:
                    CODEC = f"{i['Commercial name']} ".replace('Dolby Digital Plus with Dolby Atmos', 'Dolby Atmos').strip()
            upper_codec = (CODEC or "").upper()
            ch = CHANNELS
            if not BITRATE:
                if "HE-AAC" in upper_codec or "HE AAC" in upper_codec:
                    if ch == "2.0":
                        BITRATE = "96kb/s"
                    elif ch == "5.1":
                        BITRATE = "192kb/s"
                    elif ch == "7.1":
                        BITRATE = "256kb/s"
                elif "AAC" in upper_codec:
                    if ch == "2.0":
                        BITRATE = "128kb/s"
                    elif ch == "5.1":
                        BITRATE = "320kb/s"
                    elif ch == "7.1":
                        BITRATE = "448kb/s"
                elif "ATMOS" in upper_codec:
                    BITRATE = "768kb/s"
                elif "DDP" in upper_codec or "DD+" in upper_codec or "E-AC-3" in upper_codec:
                    if ch == "5.1":
                        BITRATE = "640kb/s"
            AUDIO_JSON = {'ID': IDX, 'CHANNELS': CHANNELS, 'BITRATE': BITRATE, 'LANGUAGE': LANGUAGE, 'CODEC': CODEC}
            AUDIOS.append(AUDIO_JSON)
            IDX += 1
    text = ""
    org_aud = None
    if AUDIOS:
        text += '🎧 <b>Audio:</b>\n'
    for audio in AUDIOS:
        line = f"{audio['ID']}. "
        line += f"{audio['LANGUAGE']} "
        if audio['ID'] == 1:
            org_aud = audio['LANGUAGE']
        if audio.get('CODEC'):
            line += f"| {audio['CODEC']} "
        if audio.get('CHANNELS'):
            line += f"{audio['CHANNELS']} "
        if audio.get('BITRATE'):
            line += f"@ {audio['BITRATE']}"
        text += f"<b>{line.strip()}</b>\n"
    return text, org_aud