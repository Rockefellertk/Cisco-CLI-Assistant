# Cisco CLI Assistant — Telegram Bot

A production-ready Telegram bot that helps network engineers quickly find
Cisco CLI commands across **IOS, IOS-XE, IOS-XR and NX-OS** — in English
or Persian, exact phrasing or natural language.

**Core principle: this bot never invents Cisco CLI.** Every answer comes
from a curated local JSON database. If nothing matches, it says so
instead of guessing. The optional AI layer is constrained to *picking*
among real, existing database entries — it cannot generate a new one
(see `app/ai.py` for how that's enforced).

---

## Features

- Natural language search, English + Persian (`show arp`, `چطور BGP Neighbor رو ببینم؟`)
- 100+ curated commands across 48 categories (routing, BGP/OSPF/ISIS,
  MPLS/SR, EVPN/VXLAN, QoS/ACL/NAT, AAA, FHRP, multicast, L2 switching,
  security, telemetry, and more)
- Per-command detail: purpose, syntax, arguments, example, sample output,
  notes, platform support, privilege level, configuration mode
- Exact / alias / partial / fuzzy (misspelling-tolerant) / Persian search
- `/convert` — see a command's equivalent across all 4 platforms at once
- Favorites & recent history (per user, JSON-backed, swappable for SQLite)
- Optional AI fallback for intent understanding when no local match is
  found — constrained to existing DB entries only

---

## Project Structure

```
/app
  bot.py          # entry point / wiring
  handlers.py     # Telegram command & callback handlers
  commands.py     # data models + in-memory DB + user data store
  search.py       # exact/alias/partial/fuzzy/Persian search engine
  ai.py           # constrained AI intent-matching fallback
  keyboards.py    # inline keyboard builders
  config.py       # .env-based configuration
/database
  commands.json     # generated command database (100+ entries)
  aliases.json       # flat alias -> command id index (debug/reference)
  categories.json     # category list
  generate_db.py        # regenerate the JSON files from curated source data
  user_data.json          # created at runtime: per-user favorites/history
/utils
  logger.py       # logging setup
  persian.py      # Persian text normalization + keyword translation
README.md
requirements.txt
.env.example
Dockerfile
docker-compose.yml
```

---

## Installation

Requires **Python 3.12+**.

```bash
git clone <your-repo-url> cisco-cli-bot
cd cisco-cli-bot
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

The command database is already generated and committed at
`database/commands.json`. If you edit `database/generate_db.py` to add
more commands, regenerate it with:

```bash
python database/generate_db.py
```

---

## Environment Variables

Set these in `.env` (see `.env.example`):

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | **Yes** | Token from @BotFather |
| `ADMIN_IDS` | No | Comma-separated Telegram user IDs (reserved for future admin features) |
| `LOG_LEVEL` | No | `DEBUG` / `INFO` / `WARNING` / `ERROR` (default `INFO`) |
| `LOG_FILE` | No | Path to rotating log file (default `logs/bot.log`) |
| `FUZZY_THRESHOLD` | No | 0.0–1.0 fuzzy-match strictness (default `0.6`) |
| `MAX_RESULTS` | No | Max search results shown as buttons (default `8`) |
| `HISTORY_LIMIT` | No | Max recent lookups stored per user (default `20`) |
| `AI_ENABLED` | No | `true`/`false` — enable the AI fallback layer (default `false`) |
| `AI_PROVIDER` | No | `anthropic` or `openai` |
| `ANTHROPIC_API_KEY` | If using Anthropic | Your Anthropic API key |
| `ANTHROPIC_MODEL` | No | Default `claude-sonnet-4-6` |
| `OPENAI_API_KEY` | If using OpenAI | Your OpenAI API key |
| `OPENAI_MODEL` | No | Default `gpt-4o-mini` |

---

## BotFather Setup

1. Open Telegram, message **[@BotFather](https://t.me/BotFather)**.
2. Send `/newbot`, choose a display name, then a unique username ending
   in `bot` (e.g. `CiscoCliAssistantBot`).
3. BotFather replies with an API token — copy it into `BOT_TOKEN` in `.env`.
4. Optional but recommended:
   - `/setdescription` — short description shown on the bot's profile
   - `/setabouttext` — about text
   - `/setcommands` — paste the list below so Telegram shows a slash-command menu:
     ```
     start - Welcome message
     help - List all bot commands
     search - Search for a Cisco command
     category - Browse commands by category
     platform - Pick a single platform's command
     random - Get a random command
     favorite - List your favorite commands
     history - Show your recent lookups
     explain - Full detailed explanation
     convert - Show equivalents across all platforms
     example - Show example + sample output
     about - About this bot
     ```

---

## Running Locally

```bash
source .venv/bin/activate
python -m app.bot
```

The bot uses long polling, so no public URL or webhook is required for
local development.

---

## Deploying to Docker

```bash
docker compose up -d --build
```

This builds the image, regenerates the database at build time, and runs
the bot with your `.env` file and a persisted `database/user_data.json` /
`logs/` volume. View logs with `docker compose logs -f`.

Manual (no compose):

```bash
docker build -t cisco-cli-bot .
docker run -d --name cisco-cli-bot --env-file .env \
  -v $(pwd)/logs:/app/logs \
  cisco-cli-bot
```

---

## Deploying to Railway

1. Push this repository to GitHub.
2. In Railway, click **New Project → Deploy from GitHub repo** and select it.
3. Railway will detect the `Dockerfile` automatically and build/deploy it.
   If it instead defaults to Nixpacks, set the build to use the
   Dockerfile explicitly in the service settings (**Settings → Build →
   Builder: Dockerfile**).
4. Under **Variables**, add `BOT_TOKEN` and any other variables from
   `.env.example` you need.
5. Since this bot runs on long polling (not a webhook), make sure the
   service is deployed as a **Worker/Background service**, not exposed
   as an HTTP service — Railway doesn't need to route traffic to it.
6. Deploy. Check the **Logs** tab for `Bot is polling for updates.`

---

## Deploying to Cloudflare Workers — important caveat

Cloudflare Workers run on the V8 isolate runtime and are designed for
short-lived request/response handlers, not long-running background
processes. **aiogram's default long-polling loop cannot run on Workers**,
and Workers do not support arbitrary outbound Python processes.

If you specifically want Cloudflare in the deployment path, the
supported pattern is:

1. Switch the bot to **webhook mode** instead of polling (aiogram
   supports this via `aiogram.webhook`), running the actual Python
   process on a normal host (Railway, a VPS, Docker, etc. — anywhere
   that can keep a process alive), exposing an HTTP endpoint like
   `/webhook/<secret>`.
2. Optionally put a **Cloudflare Worker in front of that endpoint** as a
   lightweight reverse proxy / edge cache / rate-limiter, forwarding
   Telegram's webhook POSTs to your real backend with `fetch()`.
3. Register the webhook with Telegram:
   `https://api.telegram.org/bot<token>/setWebhook?url=<your-worker-or-backend-url>`

This project ships configured for **long polling** (simplest, no public
URL needed) via Docker/Railway. Treat "Cloudflare Workers" as an edge
proxy in front of a webhook deployment, not as the Python runtime itself
— running the actual bot process there isn't something this bot (or
Python in general) supports today.

---

## Extending the Database

`database/generate_db.py` is the source of truth — it's a Python script
that builds `commands.json` from a curated, hand-verified list so the
schema stays consistent as you scale toward thousands of commands. To
add a command:

1. Add a new `COMMANDS.append(rec(...))` block following the existing
   pattern (id, title, category, aliases, per-platform command, syntax,
   example, sample output, notes, etc).
2. Run `python database/generate_db.py`.
3. Restart the bot — the database is loaded once into memory at startup.

For platforms where a command doesn't apply, use the `NA` sentinel
(`"Not supported on this platform"`) already defined in the script —
the bot detects this and displays "not supported" instead of a blank
or fabricated command.

---

## Roadmap / Future Features

- Bookmarks sync across devices (currently per-Telegram-account, already supported)
- Inline mode (`@YourBot show arp` from any chat)
- Group chat support with reduced verbosity
- Voice query transcription
- Auto-generated topology diagrams
- Cisco configuration generator & validator
- Guided troubleshooting assistant flows

---

## License

MIT — do whatever you like, no warranty.
