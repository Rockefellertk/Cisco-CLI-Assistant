"""
app/ai.py
---------
AI fallback layer, used ONLY when the deterministic SearchEngine
(app/search.py) finds nothing usable.

Design principle — "Never invent Cisco CLI":
    The LLM is NEVER asked to generate a command from scratch. It is
    given the user's query plus a shortlist of REAL candidate commands
    already present in the local database (produced by
    SearchEngine.top_candidates_for_ai) and asked to pick the single
    best matching candidate id, or return "NONE" if nothing fits.
    The bot then looks that id up in the local database. This makes
    hallucinated commands structurally impossible: the AI's output
    space is constrained to ids that already exist.

If AI_ENABLED=false (default) or no API key is configured, this layer
is skipped entirely and the bot just reports "command not found".
"""

from __future__ import annotations

import json

import httpx

from app.commands import CiscoCommand
from app.config import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_OPENAI_URL = "https://api.openai.com/v1/chat/completions"

_SYSTEM_PROMPT = (
    "You are an intent-matching assistant for a Cisco CLI command lookup tool. "
    "You will be given a user's natural-language question (possibly in Persian "
    "or English) and a numbered list of candidate Cisco commands that already "
    "exist in a trusted local database. Your ONLY job is to pick the number of "
    "the single candidate that best matches what the user is asking for. "
    "If none of the candidates are a reasonable match, respond with exactly: NONE. "
    "You must NEVER invent, guess, or output a Cisco command that is not one of "
    "the given candidates. Respond with ONLY the number (or NONE) and nothing else."
)


class AIIntentResolver:
    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def enabled(self) -> bool:
        if not self._settings.ai_enabled:
            return False
        if self._settings.ai_provider == "anthropic":
            return bool(self._settings.anthropic_api_key)
        if self._settings.ai_provider == "openai":
            return bool(self._settings.openai_api_key)
        return False

    async def resolve(
        self, user_query: str, candidates: list[CiscoCommand]
    ) -> CiscoCommand | None:
        """Return the candidate the LLM picked, or None."""
        if not self.enabled or not candidates:
            return None

        numbered = "\n".join(
            f"{i + 1}. {c.title} (category: {c.category}, aliases: "
            f"{', '.join(c.aliases[:5])})"
            for i, c in enumerate(candidates)
        )
        user_prompt = (
            f"User question: {user_query!r}\n\n"
            f"Candidates:\n{numbered}\n\n"
            "Which candidate number best matches the user's question? "
            "Reply with only the number, or NONE."
        )

        try:
            if self._settings.ai_provider == "anthropic":
                reply = await self._call_anthropic(user_prompt)
            else:
                reply = await self._call_openai(user_prompt)
        except Exception:
            logger.exception("AI intent resolution failed; falling back to no-match")
            return None

        return self._parse_choice(reply, candidates)

    @staticmethod
    def _parse_choice(
        reply: str | None, candidates: list[CiscoCommand]
    ) -> CiscoCommand | None:
        if not reply:
            return None
        cleaned = reply.strip().splitlines()[0].strip().rstrip(".")
        if cleaned.upper() == "NONE":
            return None
        try:
            idx = int(cleaned) - 1
        except ValueError:
            return None
        if 0 <= idx < len(candidates):
            return candidates[idx]
        return None

    async def _call_anthropic(self, user_prompt: str) -> str | None:
        headers = {
            "x-api-key": self._settings.anthropic_api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self._settings.anthropic_model,
            "max_tokens": 16,
            "system": _SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(_ANTHROPIC_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            for block in data.get("content", []):
                if block.get("type") == "text":
                    return block.get("text")
        return None

    async def _call_openai(self, user_prompt: str) -> str | None:
        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key or ''}",
            "content-type": "application/json",
        }
        payload = {
            "model": self._settings.openai_model,
            "max_tokens": 16,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(_OPENAI_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0]["message"]["content"]
        return None
