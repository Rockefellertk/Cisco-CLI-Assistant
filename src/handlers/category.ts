import { TelegramClient } from "../telegram";
import { getAllCategories, getByCategory } from "../db";
import { categoriesKeyboard, searchResultsKeyboard } from "../keyboards";

export async function handleCategoryList(tg: TelegramClient, chatId: number): Promise<void> {
  const categories = getAllCategories().filter((c) => c.count > 0);
  await tg.sendMessage(chatId, "*📂 Browse by category:*", {
    replyMarkup: categoriesKeyboard(categories),
  });
}

export async function handleCategorySelect(tg: TelegramClient, chatId: number, category: string): Promise<void> {
  const commands = getByCategory(category);
  if (commands.length === 0) {
    await tg.sendMessage(chatId, `No commands found in category *${category}*.`);
    return;
  }
  const keyboard = searchResultsKeyboard(commands.map((c) => ({ id: c.id, title: c.title })));
  await tg.sendMessage(chatId, `*${category}* — ${commands.length} command(s):`, { replyMarkup: keyboard });
}
