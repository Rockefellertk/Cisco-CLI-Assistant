// Usage:
//   BOT_TOKEN=xxxx node scripts/delete-webhook.mjs

const BOT_TOKEN = process.env.BOT_TOKEN;

if (!BOT_TOKEN) {
  console.error("Missing BOT_TOKEN. Usage: BOT_TOKEN=xxxx node scripts/delete-webhook.mjs");
  process.exit(1);
}

const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook`, {
  method: "POST",
});
const data = await res.json();
console.log(JSON.stringify(data, null, 2));
