import type { InlineKeyboardMarkup } from "./types";

const API_BASE = "https://api.telegram.org/bot";

export class TelegramClient {
  private base: string;

  constructor(botToken: string) {
    this.base = `${API_BASE}${botToken}`;
  }

  private async call<T = unknown>(method: string, payload: Record<string, unknown>): Promise<T> {
    const res = await fetch(`${this.base}/${method}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const errText = await res.text();
      console.error(`Telegram API error on ${method}:`, errText);
    }
    return (await res.json()) as T;
  }

  async sendMessage(
    chatId: number,
    text: string,
    options: { replyMarkup?: InlineKeyboardMarkup; parseMode?: "Markdown" | "HTML" } = {}
  ) {
    return this.call("sendMessage", {
      chat_id: chatId,
      text,
      parse_mode: options.parseMode ?? "Markdown",
      reply_markup: options.replyMarkup,
      disable_web_page_preview: true,
    });
  }

  async editMessageText(
    chatId: number,
    messageId: number,
    text: string,
    options: { replyMarkup?: InlineKeyboardMarkup; parseMode?: "Markdown" | "HTML" } = {}
  ) {
    return this.call("editMessageText", {
      chat_id: chatId,
      message_id: messageId,
      text,
      parse_mode: options.parseMode ?? "Markdown",
      reply_markup: options.replyMarkup,
      disable_web_page_preview: true,
    });
  }

  async answerCallbackQuery(callbackQueryId: string, text?: string) {
    return this.call("answerCallbackQuery", {
      callback_query_id: callbackQueryId,
      text,
    });
  }

  async setMyCommands(commands: { command: string; description: string }[]) {
    return this.call("setMyCommands", { commands });
  }
}

/**
 * Escapes special characters for Telegram's legacy Markdown parse mode
 * (we intentionally use legacy Markdown, not MarkdownV2, to keep escaping
 * simple — only _ * ` [ need escaping in that mode).
 */
export function escapeMarkdown(text: string): string {
  return text.replace(/([_*`[])/g, "\\$1");
}
