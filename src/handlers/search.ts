import type { Env } from "../types";
import { TelegramClient } from "../telegram";
import { search } from "../db";
import { aiResolveIntent } from "../ai";
import { formatCommandDetail, commandDetailKeyboard, searchResultsKeyboard } from "../keyboards";
import { pushHistory } from "../state";

export async function handleSearch(
  tg: TelegramClient,
  env: Env,
  chatId: number,
  userId: number,
  query: string
): Promise<void> {
  const trimmed = query.trim();
  if (!trimmed) {
    await tg.sendMessage(chatId, "Please tell me what you're looking for, e.g. `show arp` or `نمایش bgp`.");
    return;
  }

  const results = search(trimmed, 8);

  if (results.length === 0) {
    // Fall back to AI intent resolution — never invents commands, only maps
    // to an existing catalog entry.
    const aiMatch = await aiResolveIntent(trimmed, env);
    if (aiMatch) {
      await pushHistory(env, userId, aiMatch.command.id);
      const prefix =
        aiMatch.confidence === "low"
          ? "_I couldn't find an exact match, but this might be what you're looking for:_\n\n"
          : "";
      await tg.sendMessage(chatId, prefix + formatCommandDetail(aiMatch.command), {
        replyMarkup: commandDetailKeyboard(aiMatch.command),
      });
      return;
    }

    await tg.sendMessage(
      chatId,
      `❌ I couldn't find a command matching *"${trimmed}"* in the catalog, and I'm not confident enough to guess.\n\nTry rephrasing, or browse /category to explore what's available.`
    );
    return;
  }

  if (results.length === 1) {
    await pushHistory(env, userId, results[0].command.id);
    await tg.sendMessage(chatId, formatCommandDetail(results[0].command), {
      replyMarkup: commandDetailKeyboard(results[0].command),
    });
    return;
  }

  // Multiple candidates: show a picker
  const keyboard = searchResultsKeyboard(results.map((r) => ({ id: r.command.id, title: r.command.title })));
  await tg.sendMessage(chatId, `Found *${results.length}* possible matches for *"${trimmed}"*:`, {
    replyMarkup: keyboard,
  });
}
