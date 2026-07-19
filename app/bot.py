"""
app/bot.py
----------
Application entry point. Wires together config, the in-memory command
database, the search engine, the AI fallback layer and the aiogram
Dispatcher, then starts long-polling.

Run with:  python -m app.bot   (from the project root)
"""

from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app import handlers
from app.ai import AIIntentResolver
from app.commands import CommandDatabase, UserDataStore
from app.config import settings
from app.search import SearchEngine
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


async def main() -> None:
    setup_logging(level=settings.log_level, log_file=settings.log_file)
    logger.info("Starting Cisco CLI Assistant bot...")

    db = CommandDatabase(settings.database_dir)
    search_engine = SearchEngine(db, fuzzy_threshold=settings.fuzzy_threshold)
    ai_resolver = AIIntentResolver(settings)
    user_store = UserDataStore(
        settings.database_dir / "user_data.json", history_limit=settings.history_limit
    )

    if ai_resolver.enabled:
        logger.info("AI fallback layer ENABLED (provider=%s)", settings.ai_provider)
    else:
        logger.info("AI fallback layer disabled (set AI_ENABLED=true to turn on)")

    handlers.bind(db, search_engine, ai_resolver, user_store, settings)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher()
    dp.include_router(handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot is polling for updates.")
    await dp.start_polling(bot)


def run() -> None:
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")


if __name__ == "__main__":
    run()
