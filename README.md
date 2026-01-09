# Rick Bot (Modular)

A modular rewrite of your Telegram bot split into clean modules:

- Core: GDFlix + TMDB + Manual Poster
- OTT Poster Scrapers: Prime, Zee5, Hulu, Viki, SunNXT, Aha, etc.
- UCER: per-user settings (GDFlix key, up to 6 index URLs, full file name toggle, audio format toggle)
- State: persistent local JSON + optional remote backup
- Admin Panel

## Features

- /get, /info, /ls, /tmdb, manual poster (send photo or reply)
- Streaming poster scrapers:
  - /amzn, /airtel, /zee5, /hulu, /viki, /mmax, /snxt, /aha, /dsnp, /apple, /bms, /iq, /hbo, /up, /uj, /wetv, /sl, /tk, /nf
- /ucer UI to configure per-user settings
- /admin panel for toggling global GDFlix mode, stats

## Requirements

- Python 3.11+
- Mediainfo binary installed (`mediainfo` on PATH)
- Environment variables (see `.env.example`)

## Setup

1) Install dependencies:
```
pip install -r requirements.txt
```

2) Copy `.env.example` to `.env` and fill in values (or export env vars another way).

3) Run:
```
python -m app.main
```

## Project Structure

```
app/
  handlers/
    __init__.py
    start_help.py
    core.py
    streaming.py
    ucer.py
    admin.py
    posters_ui.py
  services/
    __init__.py
    gdflix.py
    tmdb.py
    mediainfo.py
  __init__.py
  config.py
  state.py
  utils.py
  keyboards.py
  main.py
requirements.txt
.env.example
README.md
```

Notes:
- All secrets are loaded from env. Do not hardcode tokens in code.
- Optional remote state persistence via `STATE_REMOTE_URL` (GET/POST JSON).
- If you had custom workers domains per user, add them in /ucer → Index URLs.
