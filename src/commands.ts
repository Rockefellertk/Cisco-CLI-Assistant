import type { Env, TelegramMessage } from "./types";
import { TelegramClient } from "./telegram";
import { handleStart, handleHelp, handleAbout } from "./handlers/start";
import { handleSearch } from "./handlers/search";
import { handleCategoryList } from "./handlers/category";
import { handlePlatformMenu, handleRandom } from "./handlers/platform";
import { handleFavoritesList, handleHistoryList } from "./handlers/favorites";

/** Parses "/command arg1 arg2" into { command, args }. */
function parseCommand(text: string): { command: string; args: string } | null {
  const match = text.match(/^\/([a-zA-Z_]+)(?:@\w+)?\s*(.*)$/s);
  if (!match) return null;
  return { command: match[1].toLowerCase(), args: match[2].trim() };
}

export async function routeMessage(message: TelegramMessage, env: Env): Promise<void> {
  const chatId = message.chat.id;
  const userId = message.from?.id ?? chatId;
  const text = message.text?.trim();
  if (!text) return;

  const tg = new TelegramClient(env.BOT_TOKEN);
  const parsed = text.startsWith("/") ? parseCommand(text) : null;

  if (parsed) {
    switch (parsed.command) {
      case "start":
        return handleStart(tg, chatId);
      case "help":
        return handleHelp(tg, chatId);
      case "about":
        return handleAbout(tg, chatId);
      case "search":
        return handleSearch(tg, env, chatId, userId, parsed.args);
      case "explain":
        return handleSearch(tg, env, chatId, userId, parsed.args);
      case "example":
        return handleSearch(tg, env, chatId, userId, parsed.args);
      case "convert":
        return handleSearch(tg, env, chatId, userId, parsed.args);
      case "category":
        return handleCategoryList(tg, chatId);
      case "platform":
        return handlePlatformMenu(tg, chatId);
      case "random":
        return handleRandom(tg, chatId);
      case "favorite":
      case "favorites":
        return handleFavoritesList(tg, env, chatId, userId);
      case "history":
        return handleHistoryList(tg, env, chatId, userId);
      default:
        await tg.sendMessage(chatId, "Unknown command. Type /help to see what I can do.");
        return;
    }
  }

  // Natural language message (English or Persian) — treat as a search query.
  return handleSearch(tg, env, chatId, userId, text);
}
