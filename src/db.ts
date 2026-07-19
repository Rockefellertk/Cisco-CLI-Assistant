import commandsData from "../database/commands.json";
import aliasesData from "../database/aliases.json";
import categoriesData from "../database/categories.json";
import type { CiscoCommand, Category } from "./types";

const COMMANDS = commandsData as unknown as CiscoCommand[];
const ALIAS_MAP = aliasesData as unknown as Record<string, string[]>;
const CATEGORIES = categoriesData as unknown as Category[];

const BY_ID = new Map<string, CiscoCommand>(COMMANDS.map((c) => [c.id, c]));

/** Normalizes English + Persian text for matching: lowercases, strips Persian
 *  diacritics/ZWNJ, unifies Arabic/Persian "ي/ك" to Persian "ی/ک", collapses
 *  whitespace, and trims. */
export function normalize(input: string): string {
  let s = input.toLowerCase().trim();
  s = s.replace(/[\u200c\u064b-\u065f]/g, ""); // ZWNJ + Arabic diacritics
  s = s.replace(/\u064a/g, "\u06cc"); // Arabic Yeh -> Persian Yeh
  s = s.replace(/\u0643/g, "\u06a9"); // Arabic Kaf -> Persian Kaf
  s = s.replace(/[?؟!.,]/g, "");
  s = s.replace(/\s+/g, " ");
  return s.trim();
}

/** Levenshtein distance, used for misspelling-tolerant fuzzy search. */
function levenshtein(a: string, b: string): number {
  const m = a.length;
  const n = b.length;
  if (m === 0) return n;
  if (n === 0) return m;
  const dp: number[] = new Array(n + 1);
  for (let j = 0; j <= n; j++) dp[j] = j;
  for (let i = 1; i <= m; i++) {
    let prev = dp[0];
    dp[0] = i;
    for (let j = 1; j <= n; j++) {
      const temp = dp[j];
      dp[j] = Math.min(
        dp[j] + 1,
        dp[j - 1] + 1,
        prev + (a[i - 1] === b[j - 1] ? 0 : 1)
      );
      prev = temp;
    }
  }
  return dp[n];
}

export interface SearchResult {
  command: CiscoCommand;
  score: number; // lower is better
  matchType: "exact" | "alias" | "partial" | "fuzzy";
}

/**
 * Multi-stage search:
 *  1. Exact title/alias match (normalized)
 *  2. Alias-map lookup
 *  3. Partial substring match against title + aliases
 *  4. Fuzzy match (Levenshtein) to tolerate misspellings, EN + FA
 */
export function search(rawQuery: string, limit = 8): SearchResult[] {
  const q = normalize(rawQuery);
  if (!q) return [];

  const results = new Map<string, SearchResult>();

  const consider = (cmd: CiscoCommand, score: number, type: SearchResult["matchType"]) => {
    const existing = results.get(cmd.id);
    if (!existing || score < existing.score) {
      results.set(cmd.id, { command: cmd, score, matchType: type });
    }
  };

  // Stage 1 + 2: exact / alias map
  if (ALIAS_MAP[q]) {
    for (const id of ALIAS_MAP[q]) {
      const cmd = BY_ID.get(id);
      if (cmd) consider(cmd, 0, "exact");
    }
  }

  // Stage 3: partial substring match
  for (const cmd of COMMANDS) {
    const haystacks = [cmd.title, ...cmd.aliases].map(normalize);
    for (const h of haystacks) {
      if (h === q) {
        consider(cmd, 0, "exact");
      } else if (h.includes(q) || q.includes(h)) {
        const score = Math.abs(h.length - q.length) + 1;
        consider(cmd, score, "partial");
      }
    }
  }

  // Stage 4: fuzzy (only if we don't already have strong matches, or to
  // supplement — always run for short queries to catch misspellings)
  if (results.size < limit) {
    for (const cmd of COMMANDS) {
      const haystacks = [cmd.title, ...cmd.aliases].map(normalize);
      for (const h of haystacks) {
        // compare against each word for multi-word aliases
        const dist = levenshtein(q, h);
        const threshold = Math.max(1, Math.floor(Math.min(q.length, h.length) * 0.34));
        if (dist <= threshold) {
          consider(cmd, 10 + dist, "fuzzy");
        }
      }
    }
  }

  return Array.from(results.values())
    .sort((a, b) => a.score - b.score)
    .slice(0, limit);
}

export function getById(id: string): CiscoCommand | undefined {
  return BY_ID.get(id);
}

export function getByCategory(category: string): CiscoCommand[] {
  return COMMANDS.filter((c) => c.category === category);
}

export function getAllCategories(): Category[] {
  return CATEGORIES;
}

export function getRandom(): CiscoCommand {
  return COMMANDS[Math.floor(Math.random() * COMMANDS.length)];
}

export function getAllCommands(): CiscoCommand[] {
  return COMMANDS;
}

export function totalCommandCount(): number {
  return COMMANDS.length;
}
