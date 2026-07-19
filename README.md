# 🌐 Cisco CLI Assistant — Telegram Bot on Cloudflare Workers

A serverless Telegram bot that helps network engineers find Cisco CLI commands
across **IOS, IOS-XE, IOS-XR, and NX-OS** — in English or Persian — without
ever hallucinating a command.

Runs **100% serverlessly on Cloudflare Workers** using Telegram **webhooks**.
No VPS, no always-on process, no Docker container required. The free
Cloudflare Workers plan is enough for long-term personal use.

---

## Why this architecture (no polling, no server)

Telegram bots normally run in one of two modes:

1. **Polling** — a process repeatedly calls `getUpdates` in a loop. This
   requires something to keep running 24/7 (a VPS, a container, etc).
2. **Webhook** — Telegram itself pushes each update as an HTTPS POST request
   to a URL you control. Nothing needs to run continuously; your endpoint
   just needs to exist and respond quickly.

This project uses **mode 2**. Cloudflare Workers is a perfect fit because it:
- Only executes code when a request arrives (no idle server, no cost while idle)
- Terminates HTTPS for you automatically (Telegram requires HTTPS webhooks)
- Has a generous free tier (100,000 requests/day) — more than enough for
  personal or small-team use
- Has global edge locations, so replies are fast worldwide

---

## Project Structure

```
/src
  index.ts          Worker entrypoint — handles POST /webhook
  commands.ts        Routes /start, /search, etc. + natural language text
  callbacks.ts        Routes inline keyboard button taps
  telegram.ts         Minimal Telegram Bot API client (fetch-based)
  db.ts                In-memory command database + search engine
  ai.ts                Optional AI fallback layer (never invents commands)
  keyboards.ts         Message formatting + inline keyboards
  state.ts             KV-backed favorites/history per user
  types.ts             Shared TypeScript types
  handlers/
    start.ts, search.ts, category.ts, platform.ts, favorites.ts

/database
  commands.json        117 real Cisco CLI commands (expandable to thousands)
  aliases.json          Precomputed alias -> command id lookup index
  categories.json        Category list (English + Persian names)

/scripts
  set-webhook.mjs       Registers your Worker URL with Telegram
  delete-webhook.mjs     Removes the webhook

wrangler.toml           Cloudflare Workers configuration
package.json
tsconfig.json
.env.example
```

---

## How the search works

1. **Exact match** against title/aliases (normalized — case, Persian ZWNJ,
   Arabic/Persian letter variants, punctuation all normalized away)
2. **Alias-map lookup** — a precomputed dictionary of every known alias
   (English + Persian: `arp`, `show arp`, `نمایش arp`, `جدول arp`, ...)
3. **Partial substring match** against titles and aliases
4. **Fuzzy match** (Levenshtein distance) — tolerates misspellings in both
   English and Persian
5. **AI fallback** (optional) — only triggered if steps 1–4 find nothing.
   The AI is given your *entire command catalog* and instructed to return
   only an existing catalog `id`, or `NONE`. It is architecturally
   prevented from inventing new Cisco syntax — any id it returns that
   isn't in the catalog is discarded.

If nothing matches and the AI fallback is disabled or also finds nothing,
the bot tells the user clearly instead of guessing.

---

## Deployment

### 1. Prerequisites

- A free [Cloudflare account](https://dash.cloudflare.com/sign-up)
- Node.js 18+ installed locally
- A Telegram account

### 2. Create your bot with BotFather

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`, follow the prompts (choose a name and a username ending in `bot`)
3. BotFather will give you a **bot token** like `123456789:AAExample...` — save it

### 3. Install dependencies

```bash
git clone <this-repo>   # or unzip the provided archive
cd cisco-cli-bot
npm install
```

### 4. Log in to Cloudflare

```bash
npx wrangler login
```

### 5. Create the KV namespace (for favorites/history storage)

```bash
npx wrangler kv namespace create BOT_KV
npx wrangler kv namespace create BOT_KV --preview
```

Copy the `id` and `preview_id` values from the output into `wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "BOT_KV"
id = "paste-id-here"
preview_id = "paste-preview-id-here"
```

### 6. Set secrets

Secrets are stored encrypted by Cloudflare — never commit them to `.env`:

```bash
npx wrangler secret put BOT_TOKEN
# paste the token from BotFather when prompted

npx wrangler secret put WEBHOOK_SECRET
# paste a random string, e.g. generate one with: openssl rand -hex 24

# Optional — only if you want the AI fallback layer for unmatched queries:
npx wrangler secret put AI_API_KEY
```

If you skip `AI_API_KEY`, the bot still works perfectly — it simply won't
attempt AI-based intent mapping for queries the catalog search can't match,
and will say so instead of guessing.

### 7. Deploy

```bash
npm run deploy
```

Wrangler will print your Worker URL, e.g.:
```
https://cisco-cli-assistant-bot.yoursubdomain.workers.dev
```

### 8. Register the Telegram webhook

```bash
BOT_TOKEN=123456789:AAExample... \
WORKER_URL=https://cisco-cli-assistant-bot.yoursubdomain.workers.dev \
WEBHOOK_SECRET=the-same-random-string-from-step-6 \
node scripts/set-webhook.mjs
```

You should see `"ok": true` in the response. Your bot is now live — open it
in Telegram and send `/start`.

---

## Running locally (development)

You can develop and test locally with `wrangler dev`, which runs a local
copy of your Worker. Telegram can't reach `localhost` directly, so either:

- Use `wrangler dev --remote` and point a temporary webhook at the tunnel
  URL Wrangler gives you, **or**
- Use a tunneling tool (e.g. `cloudflared tunnel`) to expose your local dev
  server, then run `set-webhook.mjs` against that tunnel URL temporarily.

```bash
npm run dev
```

Remember to set `BOT_TOKEN` and `WEBHOOK_SECRET` as local dev vars too
(create a `.dev.vars` file — Wrangler loads this automatically and it's
gitignored):

```
BOT_TOKEN=123456789:AAExample...
WEBHOOK_SECRET=your-random-string
AI_API_KEY=
```

---

## Environment Variables / Secrets summary

| Name             | Type      | Required | Set via                          |
|-------------------|-----------|----------|-----------------------------------|
| `BOT_TOKEN`        | secret    | ✅        | `wrangler secret put BOT_TOKEN`    |
| `WEBHOOK_SECRET`    | secret    | ✅        | `wrangler secret put WEBHOOK_SECRET` |
| `AI_API_KEY`         | secret    | optional | `wrangler secret put AI_API_KEY`    |
| `AI_ENABLED`          | var       | —        | `wrangler.toml` `[vars]` (default `"true"`) |
| `BOT_KV`                | KV binding | ✅        | `wrangler.toml` `[[kv_namespaces]]` |

---

## Cost / free-tier notes

- **Workers Free plan**: 100,000 requests/day, 10ms CPU time per request —
  a personal or small-team bot will not come close to these limits.
- **Workers KV Free plan**: 100,000 reads/day, 1,000 writes/day, 1GB storage
  — plenty for storing per-user favorites/history.
- No credit card is required to stay on the free tier for this workload.
- If you exceed free-tier limits (very unlikely for personal use), Cloudflare
  will notify you before any charges — it does not silently bill you.

---

## Extending the database

`database/commands.json` is a flat array of command objects. To add more
commands:

1. Add new entries following the existing schema (see any entry for the
   shape: `id`, `title`, `category`, `aliases`, `description`, `ios`,
   `ios_xe`, `ios_xr`, `nx_os`, `syntax`, `example`, `sample_output`,
   `notes`, `privilege_level`, `configuration_mode`, `related_commands`,
   `references`).
2. Regenerate `database/aliases.json` (a flat alias→id index used for fast
   exact-match lookup) — or just add your aliases directly to both files.
3. Redeploy with `npm run deploy`.

The database is bundled directly into the Worker at build time and loaded
once per isolate — no external database calls are needed for search, which
keeps responses fast.

To scale to thousands of commands without bloating a single JSON file, you
can later split `commands.json` by category and lazy-load with dynamic
`import()`, or move the catalog into Cloudflare D1 (SQL) or KV.

---

## Bot Commands Reference

| Command             | Description |
|----------------------|-------------|
| `/start`               | Welcome message + main menu |
| `/help`                 | List all commands |
| `/search <query>`         | Search for a command |
| `/category`                 | Browse by technology category |
| `/platform`                   | Filter commands by Cisco OS |
| `/random`                       | Get a random command |
| `/favorite`                       | View saved commands |
| `/history`                          | View recently viewed commands |
| `/explain <query>`                    | Full detailed explanation |
| `/convert <query>`                      | Cross-platform equivalents |
| `/example <query>`                        | Example + sample output |
| `/about`                                    | About this bot |

You can also just type naturally in English or Persian — no `/` needed.

---

## Roadmap (not yet implemented)

- Bookmark sync across devices
- Inline mode (`@YourBot show arp` from any chat)
- Group chat support with reduced verbosity
- Voice query transcription
- Topology diagram generation
- Cisco configuration generator / validator
- Interactive troubleshooting assistant

---

## Notes on the AI fallback layer

The AI layer is **opt-in** (only active if `AI_API_KEY` is set) and is
architecturally constrained: it receives your entire command catalog and is
instructed to respond with only an existing catalog id or `NONE`. The
Worker discards any id that isn't actually in the catalog before using it.
This means the AI layer can help with *intent recognition* (understanding
what you meant) but can never fabricate a Cisco command that isn't already
verified in your database.
