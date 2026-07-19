"""
app/search.py
-------------
SearchEngine implements a layered search strategy over the in-memory
CommandDatabase:

    1. Exact match       - query equals a title or alias exactly
    2. Alias match       - query equals (normalized) an alias
    3. Partial/substring - query is contained in title/alias/description
    4. Fuzzy match       - difflib-based similarity, handles misspellings
    5. Persian search    - Persian text is normalized + keyword-translated
                            before running the same pipeline

The engine never invents data — it only ever returns CiscoCommand objects
that already exist in the database, ranked by a relevance score.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from app.commands import CiscoCommand, CommandDatabase
from utils.logger import get_logger
from utils.persian import contains_persian, normalize, translate_keywords

logger = get_logger(__name__)


@dataclass
class SearchResult:
    command: CiscoCommand
    score: float
    match_type: str  # "exact" | "alias" | "partial" | "fuzzy"


class SearchEngine:
    def __init__(self, db: CommandDatabase, fuzzy_threshold: float = 0.6):
        self._db = db
        self._fuzzy_threshold = fuzzy_threshold

    # ------------------------------------------------------------------ #
    def search(self, query: str, max_results: int = 8) -> list[SearchResult]:
        if not query or not query.strip():
            return []

        raw_query = query.strip()
        is_persian = contains_persian(raw_query)
        norm_query = normalize(raw_query) if is_persian else raw_query.lower().strip()
        translated_query = translate_keywords(raw_query) if is_persian else norm_query

        results: dict[str, SearchResult] = {}

        for cmd in self._db.commands:
            score, match_type = self._score_command(cmd, norm_query, translated_query)
            if score <= 0:
                continue
            existing = results.get(cmd.id)
            if existing is None or score > existing.score:
                results[cmd.id] = SearchResult(cmd, score, match_type)

        ranked = sorted(results.values(), key=lambda r: r.score, reverse=True)
        return ranked[:max_results]

    # ------------------------------------------------------------------ #
    def _score_command(
        self, cmd: CiscoCommand, norm_query: str, translated_query: str
    ) -> tuple[float, str]:
        title_norm = cmd.title.lower()
        alias_norms = [a.lower() for a in cmd.aliases]
        alias_norms_persian = [normalize(a) for a in cmd.aliases]

        # 1. Exact match on title or alias
        if norm_query == title_norm or norm_query in alias_norms:
            return 1.0, "exact"
        if norm_query in alias_norms_persian:
            return 1.0, "exact"

        # 2. Alias contains query as a whole normalized string (handles
        #    Persian aliases stored with different normalization forms)
        for a in alias_norms_persian:
            if a and (norm_query == a):
                return 0.98, "alias"

        # 3. Partial / substring match across title, aliases, description,
        #    category and all four platform command strings.
        haystacks = [title_norm, cmd.category.lower(), cmd.searchable_text()]
        haystacks.extend(alias_norms)
        haystacks.extend(alias_norms_persian)

        query_candidates = {norm_query, translated_query}
        best_partial = 0.0
        for q in query_candidates:
            if not q:
                continue
            for h in haystacks:
                if q in h:
                    # Longer, more specific queries that match count more.
                    coverage = len(q) / max(len(h), 1)
                    best_partial = max(best_partial, 0.75 + min(coverage, 0.2))
                elif h in q and len(h) >= 3:
                    best_partial = max(best_partial, 0.7)

        if best_partial > 0:
            return best_partial, "partial"

        # 4. Fuzzy match (misspelling correction) against title + aliases
        best_fuzzy = 0.0
        for q in query_candidates:
            if not q:
                continue
            for h in [title_norm, *alias_norms]:
                ratio = SequenceMatcher(None, q, h).ratio()
                best_fuzzy = max(best_fuzzy, ratio)

        if best_fuzzy >= self._fuzzy_threshold:
            # Scale into 0.4-0.65 range so exact/partial always outrank fuzzy.
            return 0.4 + (best_fuzzy - self._fuzzy_threshold) * 0.6, "fuzzy"

        return 0.0, ""

    # ------------------------------------------------------------------ #
    def best_match(self, query: str) -> SearchResult | None:
        results = self.search(query, max_results=1)
        return results[0] if results else None

    def top_candidates_for_ai(self, query: str, n: int = 5) -> list[CiscoCommand]:
        """
        Used by the AI fallback layer: returns the N closest existing
        commands (by loosened fuzzy score) so the LLM can only ever pick
        among real database entries — never invent a new one.
        """
        raw_query = query.strip()
        is_persian = contains_persian(raw_query)
        norm_query = normalize(raw_query) if is_persian else raw_query.lower()
        translated_query = translate_keywords(raw_query) if is_persian else norm_query

        scored = []
        for cmd in self._db.commands:
            text = cmd.searchable_text()
            ratio = max(
                SequenceMatcher(None, norm_query, text).ratio(),
                SequenceMatcher(None, translated_query, text).ratio(),
            )
            scored.append((ratio, cmd))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:n]]
