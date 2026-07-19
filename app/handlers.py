"""
app/handlers.py
----------------
All aiogram Router handlers: slash commands, callback queries, and the
natural-language free-text search handler. Business logic (search, AI
fallback, storage) is delegated to app/search.py, app/ai.py and
app/commands.py — handlers only orchestrate and format.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from app import formatting, keyboards
from app.ai import AIIntentResolver
from app.commands import CommandDatabase, UserDataStore
from app.config import Settings
from app.search import SearchEngine
from utils.logger import get_logger

logger = get_logger(__name__)

router = Router(name="main")

# ---------------------------------------------------------------------- #
# These are assigned by bot.py at startup (simple manual DI — no need for
# a framework at this scale, and it keeps handler signatures simple).
db: CommandDatabase
search_engine: SearchEngine
ai_resolver: AIIntentResolver
user_store: UserDataStore
settings: Settings


def bind(
    _db: CommandDatabase,
    _search_engine: SearchEngine,
    _ai_resolver: AIIntentResolver,
    _user_store: UserDataStore,
    _settings: Settings,
) -> None:
    global db, search_engine, ai_resolver, user_store, settings
    db = _db
    search_engine = _search_engine
    ai_resolver = _ai_resolver
    user_store = _user_store
    settings = _settings


# ------------------------------------------------------------------ /start
@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    text = (
        "\U0001f4e1 *Cisco CLI Assistant*\n\n"
        "Ask me for a Cisco command in plain English or Persian, e.g.:\n"
        "• `show arp`\n"
        "• `how do I check bgp neighbors?`\n"
        "• `چطور OSPF neighbor رو ببینم؟`\n\n"
        f"I know *{db.count()}* commands across *{len(db.categories)}* categories "
        "for IOS, IOS-XE, IOS-XR and NX-OS.\n\n"
        "Use /help to see all available commands."
    )
    await message.answer(text, parse_mode="Markdown")


# ------------------------------------------------------------------- /help
@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    text = (
        "*Available commands*\n\n"
        "/search <query> — search for a Cisco command\n"
        "/category — browse commands by category\n"
        "/platform <query> — pick a single platform's command\n"
        "/random — get a random command to learn\n"
        "/favorite — list your favorite commands\n"
        "/history — show your recent lookups\n"
        "/explain <query> — full detailed explanation\n"
        "/convert <query> — show equivalents across all 4 platforms\n"
        "/example <query> — show just the example + sample output\n"
        "/about — about this bot\n\n"
        "You can also just type your question naturally, in English or Persian."
    )
    await message.answer(text, parse_mode="Markdown")


# ------------------------------------------------------------------ /about
@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    ai_status = "enabled" if ai_resolver.enabled else "disabled"
    text = (
        "\U0001f6e0 *Cisco CLI Assistant*\n\n"
        "A command lookup assistant covering IOS, IOS-XE, IOS-XR and NX-OS.\n"
        f"Database: {db.count()} commands / {len(db.categories)} categories.\n"
        f"AI fallback layer: {ai_status}.\n\n"
        "This bot never invents Cisco CLI syntax — every answer comes from "
        "a curated local database. When unsure, it says so."
    )
    await message.answer(text, parse_mode="Markdown")


# ----------------------------------------------------------------- /search
@router.message(Command("search"))
async def cmd_search(message: Message, command: CommandObject) -> None:
    query = (command.args or "").strip()
    if not query:
        await message.answer("Usage: `/search <your question>`", parse_mode="Markdown")
        return
    await _run_search_and_reply(message, query)


# --------------------------------------------------------------- /category
@router.message(Command("category"))
async def cmd_category(message: Message, command: CommandObject) -> None:
    arg = (command.args or "").strip()
    if not arg:
        await message.answer(
            "*Pick a category:*",
            reply_markup=keyboards.categories_keyboard(db.categories),
            parse_mode="Markdown",
        )
        return
    await _send_category(message, arg)


async def _send_category(message: Message, category: str) -> None:
    cmds = db.by_category(category)
    if not cmds:
        await message.answer(f"No commands found in category `{category}`.", parse_mode="Markdown")
        return
    await message.answer(
        f"*{category}* — {len(cmds)} commands",
        reply_markup=keyboards.command_list_keyboard(cmds),
        parse_mode="Markdown",
    )


# --------------------------------------------------------------- /platform
@router.message(Command("platform"))
async def cmd_platform(message: Message, command: CommandObject) -> None:
    query = (command.args or "").strip()
    if not query:
        await message.answer("Usage: `/platform <your question>`", parse_mode="Markdown")
        return
    result = search_engine.best_match(query)
    if result is None:
        await message.answer(formatting.format_search_no_results(query), parse_mode="Markdown")
        return
    user_store.add_history(message.from_user.id, result.command.id)
    await message.answer(
        f"Pick a platform for *{result.command.title}*:",
        reply_markup=keyboards.platform_picker_keyboard(result.command),
        parse_mode="Markdown",
    )


# ----------------------------------------------------------------- /random
@router.message(Command("random"))
async def cmd_random(message: Message) -> None:
    cmd = db.random()
    user_store.add_history(message.from_user.id, cmd.id)
    await message.answer(
        formatting.format_command_summary(cmd),
        reply_markup=keyboards.random_again_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == keyboards.CB_RANDOM)
async def cb_random(callback: CallbackQuery) -> None:
    cmd = db.random()
    user_store.add_history(callback.from_user.id, cmd.id)
    await callback.message.edit_text(
        formatting.format_command_summary(cmd),
        reply_markup=keyboards.random_again_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


# --------------------------------------------------------------- /favorite
@router.message(Command("favorite"))
async def cmd_favorite(message: Message) -> None:
    ids = user_store.get_favorites(message.from_user.id)
    cmds = [db.get(i) for i in ids if db.get(i)]
    await message.answer(formatting.format_favorites_list(cmds), parse_mode="Markdown")


# ---------------------------------------------------------------- /history
@router.message(Command("history"))
async def cmd_history(message: Message) -> None:
    ids = user_store.get_history(message.from_user.id)
    cmds = [db.get(i) for i in ids if db.get(i)]
    await message.answer(formatting.format_history_list(cmds), parse_mode="Markdown")


# ---------------------------------------------------------------- /explain
@router.message(Command("explain"))
async def cmd_explain(message: Message, command: CommandObject) -> None:
    query = (command.args or "").strip()
    if not query:
        await message.answer("Usage: `/explain <your question>`", parse_mode="Markdown")
        return
    cmd = await _resolve_query(query)
    if cmd is None:
        await message.answer(formatting.format_search_no_results(query), parse_mode="Markdown")
        return
    user_store.add_history(message.from_user.id, cmd.id)
    is_fav = cmd.id in user_store.get_favorites(message.from_user.id)
    await message.answer(
        formatting.format_command_full(cmd),
        reply_markup=keyboards.command_detail_keyboard(cmd, is_fav),
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------- /convert
@router.message(Command("convert"))
async def cmd_convert(message: Message, command: CommandObject) -> None:
    query = (command.args or "").strip()
    if not query:
        await message.answer("Usage: `/convert <your question or command>`", parse_mode="Markdown")
        return
    cmd = await _resolve_query(query)
    if cmd is None:
        await message.answer(formatting.format_search_no_results(query), parse_mode="Markdown")
        return
    user_store.add_history(message.from_user.id, cmd.id)
    await message.answer(formatting.format_convert_table(cmd), parse_mode="Markdown")


# ---------------------------------------------------------------- /example
@router.message(Command("example"))
async def cmd_example(message: Message, command: CommandObject) -> None:
    query = (command.args or "").strip()
    if not query:
        await message.answer("Usage: `/example <your question>`", parse_mode="Markdown")
        return
    cmd = await _resolve_query(query)
    if cmd is None:
        await message.answer(formatting.format_search_no_results(query), parse_mode="Markdown")
        return
    user_store.add_history(message.from_user.id, cmd.id)
    text = (
        f"*{cmd.title}*\n\n*Example:*\n`{cmd.example}`\n\n"
        f"*Sample Output:*\n```\n{cmd.sample_output}\n```"
    )
    await message.answer(text, parse_mode="Markdown")


# ------------------------------------------------------------ callback: cmd
@router.callback_query(F.data.startswith(f"{keyboards.CB_CMD}:"))
async def cb_open_command(callback: CallbackQuery) -> None:
    cmd_id = callback.data.split(":", 1)[1]
    cmd = db.get(cmd_id)
    if cmd is None:
        await callback.answer("Command not found.", show_alert=True)
        return
    user_store.add_history(callback.from_user.id, cmd.id)
    is_fav = cmd.id in user_store.get_favorites(callback.from_user.id)
    await callback.message.answer(
        formatting.format_command_full(cmd),
        reply_markup=keyboards.command_detail_keyboard(cmd, is_fav),
        parse_mode="Markdown",
    )
    await callback.answer()


# --------------------------------------------------------- callback: explain
@router.callback_query(F.data.startswith(f"{keyboards.CB_EXPLAIN}:"))
async def cb_explain(callback: CallbackQuery) -> None:
    cmd_id = callback.data.split(":", 1)[1]
    cmd = db.get(cmd_id)
    if cmd is None:
        await callback.answer("Command not found.", show_alert=True)
        return
    is_fav = cmd.id in user_store.get_favorites(callback.from_user.id)
    await callback.message.edit_text(
        formatting.format_command_full(cmd),
        reply_markup=keyboards.command_detail_keyboard(cmd, is_fav),
        parse_mode="Markdown",
    )
    await callback.answer()


# --------------------------------------------------------- callback: convert
@router.callback_query(F.data.startswith(f"{keyboards.CB_CONVERT}:"))
async def cb_convert(callback: CallbackQuery) -> None:
    cmd_id = callback.data.split(":", 1)[1]
    cmd = db.get(cmd_id)
    if cmd is None:
        await callback.answer("Command not found.", show_alert=True)
        return
    await callback.message.answer(formatting.format_convert_table(cmd), parse_mode="Markdown")
    await callback.answer()


# -------------------------------------------------------- callback: platform
@router.callback_query(F.data.startswith(f"{keyboards.CB_PLATFORM}:"))
async def cb_platform(callback: CallbackQuery) -> None:
    _, cmd_id, platform = callback.data.split(":", 2)
    cmd = db.get(cmd_id)
    if cmd is None:
        await callback.answer("Command not found.", show_alert=True)
        return
    await callback.message.answer(
        formatting.format_platform_single(cmd, platform), parse_mode="Markdown"
    )
    await callback.answer()


# -------------------------------------------------------- callback: favorite
@router.callback_query(F.data.startswith(f"{keyboards.CB_FAVORITE}:"))
async def cb_favorite(callback: CallbackQuery) -> None:
    cmd_id = callback.data.split(":", 1)[1]
    cmd = db.get(cmd_id)
    if cmd is None:
        await callback.answer("Command not found.", show_alert=True)
        return
    now_fav = user_store.toggle_favorite(callback.from_user.id, cmd_id)
    await callback.answer("Added to favorites \u2b50" if now_fav else "Removed from favorites")
    try:
        await callback.message.edit_reply_markup(
            reply_markup=keyboards.command_detail_keyboard(cmd, now_fav)
        )
    except Exception:
        # message might already show that markup / be a different message type
        pass


# ------------------------------------------------------- callback: category
@router.callback_query(F.data.startswith(f"{keyboards.CB_CATEGORY}:"))
async def cb_category(callback: CallbackQuery) -> None:
    category = callback.data.split(":", 1)[1]
    cmds = db.by_category(category)
    if not cmds:
        await callback.answer("No commands in this category.", show_alert=True)
        return
    await callback.message.answer(
        f"*{category}* — {len(cmds)} commands",
        reply_markup=keyboards.command_list_keyboard(cmds),
        parse_mode="Markdown",
    )
    await callback.answer()


# ------------------------------------------------------------ free-text NLU
@router.message(F.text & ~F.text.startswith("/"))
async def handle_freetext(message: Message) -> None:
    query = message.text.strip()
    if not query:
        return
    await _run_search_and_reply(message, query)


# ------------------------------------------------------------------ helpers
async def _resolve_query(query: str):
    """Best deterministic match, falling back to the AI intent layer."""
    result = search_engine.best_match(query)
    if result is not None:
        return result.command
    if ai_resolver.enabled:
        candidates = search_engine.top_candidates_for_ai(query, n=6)
        return await ai_resolver.resolve(query, candidates)
    return None


async def _run_search_and_reply(message: Message, query: str) -> None:
    results = search_engine.search(query, max_results=settings.max_results)

    if not results:
        if ai_resolver.enabled:
            candidates = search_engine.top_candidates_for_ai(query, n=6)
            picked = await ai_resolver.resolve(query, candidates)
            if picked is not None:
                user_store.add_history(message.from_user.id, picked.id)
                is_fav = picked.id in user_store.get_favorites(message.from_user.id)
                await message.answer(
                    "\U0001f916 _No exact match — closest known command:_\n\n"
                    + formatting.format_command_full(picked),
                    reply_markup=keyboards.command_detail_keyboard(picked, is_fav),
                    parse_mode="Markdown",
                )
                return
        await message.answer(formatting.format_search_no_results(query), parse_mode="Markdown")
        return

    if len(results) == 1:
        cmd = results[0].command
        user_store.add_history(message.from_user.id, cmd.id)
        is_fav = cmd.id in user_store.get_favorites(message.from_user.id)
        await message.answer(
            formatting.format_command_full(cmd),
            reply_markup=keyboards.command_detail_keyboard(cmd, is_fav),
            parse_mode="Markdown",
        )
        return

    await message.answer(
        f"Found {len(results)} possible matches for `{query}`:",
        reply_markup=keyboards.search_results_keyboard(results),
        parse_mode="Markdown",
    )
