import type { Platform } from "../types";
import { PLATFORM_LABELS } from "../types";
import { TelegramClient } from "../telegram";
import { getAllCommands, getById } from "../db";
import { formatCommandDetail, commandDetailKeyboard } from "../keyboards";
import type { InlineKeyboardMarkup } from "../types";

export async function handlePlatformMenu(tg: TelegramClient, chatId: number): Promise<void> {
  const keyboard: InlineKeyboardMarkup = {
    inline_keyboard: [
      [
        { text: "IOS", callback_data: "plat:ios" },
        { text: "IOS-XE", callback_data: "plat:ios_xe" },
      ],
      [
        { text: "IOS-XR", callback_data: "plat:ios_xr" },
        { text: "NX-OS", callback_data: "plat:nx_os" },
      ],
    ],
  };
  await tg.sendMessage(chatId, "Choose a platform to see all supported commands:", { replyMarkup: keyboard });
}

export async function handlePlatformSelect(tg: TelegramClient, chatId: number, platform: Platform): Promise<void> {
  const commands = getAllCommands().filter((c) => c[platform]);
  const lines = commands.slice(0, 40).map((c) => `• *${c.title}*: \`${c[platform]}\``);
  const more = commands.length > 40 ? `\n\n_...and ${commands.length - 40} more. Use /search to narrow it down._` : "";
  await tg.sendMessage(
    chatId,
    `*${PLATFORM_LABELS[platform]} commands* (${commands.length} total):\n\n${lines.join("\n")}${more}`
  );
}

export async function handleRandom(tg: TelegramClient, chatId: number): Promise<void> {
  const { getRandom } = await import("../db");
  const cmd = getRandom();
  await tg.sendMessage(chatId, formatCommandDetail(cmd), { replyMarkup: commandDetailKeyboard(cmd) });
}

export async function handleConvert(tg: TelegramClient, chatId: number, commandId: string): Promise<void> {
  const cmd = getById(commandId);
  if (!cmd) {
    await tg.sendMessage(chatId, "Command not found.");
    return;
  }
  const platforms: Platform[] = ["ios", "ios_xe", "ios_xr", "nx_os"];
  const lines = platforms.map(
    (p) => `• *${PLATFORM_LABELS[p]}:* ${cmd[p] ? "`" + cmd[p] + "`" : "_not supported_"}`
  );
  await tg.sendMessage(chatId, `*🔁 Cross-platform equivalents for "${cmd.title}":*\n\n${lines.join("\n")}`, {
    replyMarkup: { inline_keyboard: [[{ text: "⬅ Back", callback_data: `cmd:${cmd.id}` }]] },
  });
}
