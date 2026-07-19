// ---------- Environment bindings (Cloudflare Workers) ----------
export interface Env {
  BOT_KV: KVNamespace;
  BOT_TOKEN: string;
  WEBHOOK_SECRET: string;
  AI_ENABLED?: string;
  AI_API_KEY?: string; // optional: Anthropic API key for the AI fallback layer
}

// ---------- Domain models ----------
export interface CiscoCommand {
  id: string;
  title: string;
  category: string;
  aliases: string[];
  description: string | null;
  ios: string | null;
  ios_xe: string | null;
  ios_xr: string | null;
  nx_os: string | null;
  syntax: string | null;
  example: string | null;
  sample_output: string | null;
  notes: string | null;
  privilege_level: string | null;
  configuration_mode: string | null;
  related_commands: string[];
  references: string[];
}

export interface Category {
  name: string;
  name_fa: string;
  count: number;
}

export type Platform = "ios" | "ios_xe" | "ios_xr" | "nx_os";

export const PLATFORM_LABELS: Record<Platform, string> = {
  ios: "IOS",
  ios_xe: "IOS-XE",
  ios_xr: "IOS-XR",
  nx_os: "NX-OS",
};

// ---------- Telegram minimal types ----------
export interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
  callback_query?: TelegramCallbackQuery;
}

export interface TelegramMessage {
  message_id: number;
  from?: TelegramUser;
  chat: TelegramChat;
  date: number;
  text?: string;
}

export interface TelegramUser {
  id: number;
  is_bot: boolean;
  first_name: string;
  username?: string;
  language_code?: string;
}

export interface TelegramChat {
  id: number;
  type: string;
}

export interface TelegramCallbackQuery {
  id: string;
  from: TelegramUser;
  message?: TelegramMessage;
  data?: string;
}

export interface InlineKeyboardButton {
  text: string;
  callback_data?: string;
}

export interface InlineKeyboardMarkup {
  inline_keyboard: InlineKeyboardButton[][];
}

// ---------- User state stored in KV ----------
export interface UserState {
  favorites: string[]; // command ids
  history: string[]; // command ids, most recent first, capped
  lastSearch?: string;
}
