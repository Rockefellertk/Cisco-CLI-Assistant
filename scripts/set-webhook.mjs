// Usage:
//   BOT_TOKEN=xxxx WORKER_URL=https://your-worker.your-subdomain.workers.dev WEBHOOK_SECRET=yyyy node scripts/set-webhook.mjs
//
// This registers your Cloudflare Worker's /webhook endpoint with Telegram so
// Telegram pushes updates to it directly (no polling, no server to keep running).

const BOT_TOKEN = process.env.BOT_TOKEN;
const WORKER_URL = process.env.WORKER_URL;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;

if (!BOT_TOKEN || !WORKER_URL || !WEBHOOK_SECRET) {
  console.error("Missing required env vars. Usage:");
  console.error(
    "  BOT_TOKEN=xxxx WORKER_URL=https://your-worker.workers.dev WEBHOOK_SECRET=yyyy node scripts/set-webhook.mjs"
  );
  process.exit(1);
}

const webhookUrl = `${WORKER_URL.replace(/\/$/, "")}/webhook`;

const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/setWebhook`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    url: webhookUrl,
    secret_token: WEBHOOK_SECRET,
    allowed_updates: ["message", "callback_query"],
    drop_pending_updates: true,
  }),
});

const data = await res.json();
console.log(JSON.stringify(data, null, 2));

if (data.ok) {
  console.log(`\n✅ Webhook set to ${webhookUrl}`);
} else {
  console.error("\n❌ Failed to set webhook.");
  process.exit(1);
}
