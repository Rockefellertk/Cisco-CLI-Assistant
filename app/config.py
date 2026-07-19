"""
app/config.py
-------------
Loads configuration from environment variables / a .env file.
Kept dependency-light (python-dotenv only) and fails fast with a clear
error message if required settings are missing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    val = os.getenv(name)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default


def _get_list(name: str) -> list[str]:
    val = os.getenv(name, "")
    return [x.strip() for x in val.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    # --- Telegram ---
    bot_token: str

    # --- Storage ---
    database_dir: Path = field(default_factory=lambda: BASE_DIR / "database")

    # --- Logging ---
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"

    # --- AI fallback layer ---
    ai_enabled: bool = False
    ai_provider: str = "anthropic"  # "anthropic" | "openai"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # --- Search tuning ---
    fuzzy_threshold: float = 0.6  # 0..1, higher = stricter
    max_results: int = 8

    # --- Misc ---
    admin_ids: list[int] = field(default_factory=list)
    history_limit: int = 20

    @staticmethod
    def load() -> "Settings":
        token = os.getenv("BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "BOT_TOKEN is not set. Copy .env.example to .env and fill in "
                "the token you got from @BotFather."
            )

        admin_ids_raw = _get_list("ADMIN_IDS")
        admin_ids = [int(x) for x in admin_ids_raw if x.isdigit()]

        return Settings(
            bot_token=token,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/bot.log"),
            ai_enabled=_get_bool("AI_ENABLED", False),
            ai_provider=os.getenv("AI_PROVIDER", "anthropic"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            fuzzy_threshold=float(os.getenv("FUZZY_THRESHOLD", "0.6")),
            max_results=_get_int("MAX_RESULTS", 8),
            admin_ids=admin_ids,
            history_limit=_get_int("HISTORY_LIMIT", 20),
        )


settings = Settings.load()
