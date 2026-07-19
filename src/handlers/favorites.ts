import type { Env } from "../types";
import { TelegramClient } from "../telegram";
import { getUserState, addFavorite, removeFavorite } from "../state";
import { getById } from "../db";
import { searchResultsKeyboard } from "../keyboards";

export async function handleFavoritesList(tg: TelegramClient, env: Env, chatId: number, userId: number): Promise<void> {
  const state = await getUserState(env, userId);
  if (state.favorites.length === 0) {
    await tg.sendMessage(chatId, "⭐ You have no favorites yet. Open any command and tap *Add to favorites*.");
    return;
  }
  const items = state.favorites
    .map((id) => getById(id))
    .filter((c): c is NonNullable<typeof c> => Boolean(c));
  const keyboard = searchResultsKeyboard(items.map((c) => ({ id: c.id, title: c.title })));
  await tg.sendMessage(chatId, `*⭐ Your favorites* (${items.length}):`, { replyMarkup: keyboard });
}

export async function handleAddFavorite(
  tg: TelegramClient,
  env: Env,
  chatId: number,
  userId: number,
  commandId: string,
  callbackQueryId: string
): Promise<void> {
  const cmd = getById(commandId);
  if (!cmd) {
    await tg.answerCallbackQuery(callbackQueryId, "Command not found.");
    return;
  }
  await addFavorite(env, userId, commandId);
  await tg.answerCallbackQuery(callbackQueryId, `⭐ Added "${cmd.title}" to favorites`);
}

export async function handleHistoryList(tg: TelegramClient, env: Env, chatId: number, userId: number): Promise<void> {
  const state = await getUserState(env, userId);
  if (state.history.length === 0) {
    await tg.sendMessage(chatId, "🕓 No history yet. Search for a command to get started.");
    return;
  }
  const items = state.history
    .map((id) => getById(id))
    .filter((c): c is NonNullable<typeof c> => Boolean(c));
  const keyboard = searchResultsKeyboard(items.map((c) => ({ id: c.id, title: c.title })));
  await tg.sendMessage(chatId, `*🕓 Recently viewed* (${items.length}):`, { replyMarkup: keyboard });
}
