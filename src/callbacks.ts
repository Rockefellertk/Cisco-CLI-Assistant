import type { Env, TelegramCallbackQuery } from "./types";
import { TelegramClient } from "./telegram";
import { getById } from "./db";
import { formatCommandDetail, commandDetailKeyboard } from "./keyboards";
import { pushHistory, addFavorite } from "./state";
import { handleCategoryList, handleCategorySelect } from "./handlers/category";
import { handlePlatformMenu, handlePlatformSelect, handleRandom, handleConvert } from "./handlers/platform";
import { handleFavoritesList, handleHistoryList } from "./handlers/favorites";
import type { Platform } from "./types";

export async function routeCallback(cb: TelegramCallbackQuery, env: Env): Promise<void> {
  const tg = new TelegramClient(env.BOT_TOKEN);
  const chatId = cb.message?.chat.id;
  const userId = cb.from.id;
  const data = cb.data ?? "";

  if (!chatId) {
    await tg.answerCallbackQuery(cb.id);
    return;
  }

  const [action, payload] = data.split(":");

  switch (action) {
    case "cmd": {
      const cmd = getById(payload);
      if (!cmd) {
        await tg.answerCallbackQuery(cb.id, "Command not found.");
        return;
      }
      await pushHistory(env, userId, cmd.id);
      await tg.sendMessage(chatId, formatCommandDetail(cmd), { replyMarkup: commandDetailKeyboard(cmd) });
      await tg.answerCallbackQuery(cb.id);
      return;
    }
    case "cat": {
      await handleCategorySelect(tg, chatId, payload);
      await tg.answerCallbackQuery(cb.id);
      return;
    }
    case "plat": {
      await handlePlatformSelect(tg, chatId, payload as Platform);
      await tg.answerCallbackQuery(cb.id);
      return;
    }
    case "conv": {
      await handleConvert(tg, chatId, payload);
      await tg.answerCallbackQuery(cb.id);
      return;
    }
    case "fav_add": {
      const cmd = getById(payload);
      if (cmd) await addFavorite(env, userId, payload);
      await tg.answerCallbackQuery(cb.id, cmd ? `⭐ Added "${cmd.title}"` : "Not found");
      return;
    }
    case "menu": {
      await tg.answerCallbackQuery(cb.id);
      switch (payload) {
        case "search":
          await tg.sendMessage(chatId, "Type your search query, e.g. `show arp` or `نمایش bgp`.");
          return;
        case "category":
          return handleCategoryList(tg, chatId);
        case "random":
          return handleRandom(tg, chatId);
        case "favorites":
          return handleFavoritesList(tg, env, chatId, userId);
        case "history":
          return handleHistoryList(tg, env, chatId, userId);
        case "about": {
          const { handleAbout } = await import("./handlers/start");
          return handleAbout(tg, chatId);
        }
        default:
          return;
      }
    }
    default:
      await tg.answerCallbackQuery(cb.id);
      return;
  }
}
