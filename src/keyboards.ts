import type { CiscoCommand, InlineKeyboardMarkup, Category, Platform } from "./types";
import { PLATFORM_LABELS } from "./types";
import { escapeMarkdown } from "./telegram";

/** Full detail card for a command: purpose, syntax, args, example, output, notes, etc. */
export function formatCommandDetail(cmd: CiscoCommand): string {
  const lines: string[] = [];
  lines.push(`*${escapeMarkdown(cmd.title)}*`);
  lines.push(`_Category: ${escapeMarkdown(cmd.category)}_`);
  lines.push("");

  if (cmd.description) {
    lines.push(`*Purpose:*\n${cmd.description}`);
    lines.push("");
  }

  lines.push("*Platform Support:*");
  const platforms: Platform[] = ["ios", "ios_xe", "ios_xr", "nx_os"];
  for (const p of platforms) {
    const val = cmd[p];
    lines.push(`• *${PLATFORM_LABELS[p]}:* ${val ? "\`" + val + "\`" : "_not supported / no direct equivalent_"}`);
  }
  lines.push("");

  if (cmd.syntax) {
    lines.push(`*Syntax:*\n\`${cmd.syntax}\``);
    lines.push("");
  }
  if (cmd.example) {
    lines.push(`*Example:*\n\`${cmd.example}\``);
    lines.push("");
  }
  if (cmd.sample_output) {
    lines.push(`*Sample Output:*\n\`\`\`\n${cmd.sample_output}\n\`\`\``);
    lines.push("");
  }
  if (cmd.privilege_level || cmd.configuration_mode) {
    lines.push(
      `*Privilege Level:* ${cmd.privilege_level ?? "N/A"}\n*Configuration Mode:* ${cmd.configuration_mode ?? "N/A"}`
    );
    lines.push("");
  }
  if (cmd.notes) {
    lines.push(`*Notes:*\n${cmd.notes}`);
    lines.push("");
  }

  return lines.join("\n").trim();
}

/** Compact one-line summary used in search result lists. */
export function formatCommandSummary(cmd: CiscoCommand): string {
  const primary = cmd.ios ?? cmd.ios_xe ?? cmd.ios_xr ?? cmd.nx_os ?? "";
  return `*${escapeMarkdown(cmd.title)}* — \`${primary}\``;
}

export function searchResultsKeyboard(commandIds: { id: string; title: string }[]): InlineKeyboardMarkup {
  return {
    inline_keyboard: commandIds.map((c) => [{ text: c.title, callback_data: `cmd:${c.id}` }]),
  };
}

export function commandDetailKeyboard(cmd: CiscoCommand): InlineKeyboardMarkup {
  const rows = [
    [
      { text: "⭐ Add to favorites", callback_data: `fav_add:${cmd.id}` },
      { text: "🔁 Convert", callback_data: `conv:${cmd.id}` },
    ],
  ];
  if (cmd.related_commands.length > 0) {
    rows.push(
      cmd.related_commands.slice(0, 3).map((id) => ({ text: `↪ ${id}`, callback_data: `cmd:${id}` }))
    );
  }
  return { inline_keyboard: rows };
}

export function categoriesKeyboard(categories: Category[]): InlineKeyboardMarkup {
  const rows: { text: string; callback_data: string }[][] = [];
  for (let i = 0; i < categories.length; i += 2) {
    const row = categories.slice(i, i + 2).map((c) => ({
      text: `${c.name} (${c.count})`,
      callback_data: `cat:${c.name}`,
    }));
    rows.push(row);
  }
  return { inline_keyboard: rows };
}

export function mainMenuKeyboard(): InlineKeyboardMarkup {
  return {
    inline_keyboard: [
      [
        { text: "🔍 Search", callback_data: "menu:search" },
        { text: "📂 Categories", callback_data: "menu:category" },
      ],
      [
        { text: "🎲 Random", callback_data: "menu:random" },
        { text: "⭐ Favorites", callback_data: "menu:favorites" },
      ],
      [
        { text: "🕓 History", callback_data: "menu:history" },
        { text: "ℹ️ About", callback_data: "menu:about" },
      ],
    ],
  };
}

export function convertKeyboard(cmd: CiscoCommand): InlineKeyboardMarkup {
  return { inline_keyboard: [[{ text: "⬅ Back", callback_data: `cmd:${cmd.id}` }]] };
}
