import type { Env } from "../types";
import { TelegramClient } from "../telegram";
import { mainMenuKeyboard } from "../keyboards";
import { totalCommandCount } from "../db";

export async function handleStart(tg: TelegramClient, chatId: number): Promise<void> {
  const text = [
    "*🌐 Cisco CLI Assistant*",
    "",
    `I help you find Cisco CLI commands across *IOS, IOS-XE, IOS-XR, and NX-OS* — fast, and without hallucinating commands.`,
    "",
    `📚 Database: *${totalCommandCount()} commands* and growing.`,
    "",
    "Just type what you need, in English or Persian:",
    "• `show arp`",
    "• `how do I check bgp neighbors?`",
    "• `نمایش جدول مک`",
    "",
    "Or use the menu below.",
  ].join("\n");

  await tg.sendMessage(chatId, text, { replyMarkup: mainMenuKeyboard() });
}

export async function handleHelp(tg: TelegramClient, chatId: number): Promise<void> {
  const text = [
    "*Available commands:*",
    "",
    "/search `<query>` — search for a command",
    "/category — browse by technology category",
    "/platform — filter by Cisco OS",
    "/random — get a random command",
    "/favorite — view your saved commands",
    "/history — view recently viewed commands",
    "/explain `<query>` — detailed explanation of a command",
    "/convert `<command>` — show equivalents across all platforms",
    "/example `<query>` — show example + sample output",
    "/about — about this bot",
    "",
    "You can also just type naturally — no need to remember exact syntax.",
  ].join("\n");

  await tg.sendMessage(chatId, text);
}

export async function handleAbout(tg: TelegramClient, chatId: number): Promise<void> {
  const text = [
    "*🌐 Cisco CLI Assistant*",
    "",
    "A serverless Telegram bot for network engineers, running on Cloudflare Workers.",
    "",
    `Commands in database: *${totalCommandCount()}*`,
    "Platforms: IOS, IOS-XE, IOS-XR, NX-OS",
    "",
    "This bot never invents Cisco CLI syntax. If a command isn't in the catalog and can't be confidently matched, it will say so clearly instead of guessing.",
  ].join("\n");

  await tg.sendMessage(chatId, text);
}
