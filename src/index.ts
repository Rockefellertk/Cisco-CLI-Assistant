import type { Env, TelegramUpdate } from "./types";
import { routeMessage } from "./commands";
import { routeCallback } from "./callbacks";

/**
 * Cloudflare Worker fetch handler.
 *
 * Only one route matters: POST /webhook — this is what you register with
 * Telegram via setWebhook. Telegram pushes updates to this URL; there is no
 * polling loop, no long-running process, and no VPS/dedicated server
 * involved. The Worker wakes up on each incoming update and goes back to
 * sleep, which is what makes this free on Cloudflare's Workers Free plan for
 * normal personal-bot traffic volumes.
 */
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/webhook" && request.method === "POST") {
      // Verify the request actually came from Telegram using the secret
      // token you configured with setWebhook (see scripts/set-webhook.mjs).
      const secretHeader = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
      if (env.WEBHOOK_SECRET && secretHeader !== env.WEBHOOK_SECRET) {
        return new Response("Forbidden", { status: 403 });
      }

      let update: TelegramUpdate;
      try {
        update = await request.json();
      } catch {
        return new Response("Bad Request", { status: 400 });
      }

      // Respond to Telegram immediately, and do the actual work in the
      // background via waitUntil so Telegram doesn't time out / retry.
      ctx.waitUntil(handleUpdate(update, env));
      return new Response("OK", { status: 200 });
    }

    if (url.pathname === "/" || url.pathname === "") {
      return new Response("Cisco CLI Assistant bot is running.", { status: 200 });
    }

    return new Response("Not Found", { status: 404 });
  },
};

async function handleUpdate(update: TelegramUpdate, env: Env): Promise<void> {
  try {
    if (update.message) {
      await routeMessage(update.message, env);
    } else if (update.callback_query) {
      await routeCallback(update.callback_query, env);
    }
  } catch (err) {
    console.error("Error handling update:", err);
  }
}
