import type { Env, CiscoCommand } from "./types";
import { getAllCommands } from "./db";

/**
 * When local search (exact/alias/partial/fuzzy) finds nothing, we ask an LLM
 * to pick the closest matching command *from our own database* by id.
 * The model is explicitly instructed to never invent a Cisco command — it
 * may only return an id that exists in our catalog, or "NONE".
 */
export async function aiResolveIntent(
  userQuery: string,
  env: Env
): Promise<{ command: CiscoCommand; confidence: "high" | "low" } | null> {
  if (env.AI_ENABLED !== "true" || !env.AI_API_KEY) {
    return null;
  }

  const catalog = getAllCommands().map((c) => ({
    id: c.id,
    title: c.title,
    category: c.category,
    aliases: c.aliases,
  }));

  const systemPrompt = [
    "You are an intent-mapping engine for a Cisco CLI command catalog.",
    "You will be given a user query (English or Persian/Farsi) and a JSON catalog of",
    "known commands (id, title, category, aliases).",
    "Your ONLY job is to pick the single best-matching catalog entry by id, or return NONE",
    "if nothing in the catalog is a reasonable match.",
    "You must NEVER invent a Cisco CLI command or return an id that is not in the catalog.",
    'Respond with ONLY a compact JSON object: {"id": "<catalog id or NONE>", "confidence": "high"|"low"}',
    "No prose, no markdown, no explanation.",
  ].join(" ");

  const userPrompt = `User query: ${userQuery}\n\nCatalog:\n${JSON.stringify(catalog)}`;

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": env.AI_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 200,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      }),
    });

    if (!res.ok) {
      console.error("AI resolve failed:", await res.text());
      return null;
    }

    const data = (await res.json()) as { content: { type: string; text?: string }[] };
    const textBlock = data.content.find((b) => b.type === "text");
    if (!textBlock?.text) return null;

    const cleaned = textBlock.text.replace(/```json|```/g, "").trim();
    const parsed = JSON.parse(cleaned) as { id: string; confidence: "high" | "low" };

    if (!parsed.id || parsed.id === "NONE") return null;

    const match = getAllCommands().find((c) => c.id === parsed.id);
    if (!match) return null; // guard: never trust an id outside our catalog

    return { command: match, confidence: parsed.confidence ?? "low" };
  } catch (err) {
    console.error("AI resolve error:", err);
    return null;
  }
}
