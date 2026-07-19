"""
app/keyboards.py
-----------------
All inline keyboard builders live here, kept separate from handlers so
layout can be tweaked without touching business logic.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.commands import PLATFORM_LABELS, CiscoCommand

CB_CMD = "cmd"          # cmd:<id>                 -> open a command's detail view
CB_CATEGORY = "cat"      # cat:<name>                -> list commands in a category
CB_CATEGORIES = "cats"   # cats                      -> show category picker
CB_PLATFORM = "plat"     # plat:<id>:<platform>      -> show single-platform view
CB_CONVERT = "conv"      # conv:<id>                 -> show cross-platform table
CB_FAVORITE = "fav"      # fav:<id>                  -> toggle favorite
CB_RANDOM = "rand"       # rand                      -> new random command
CB_EXPLAIN = "expl"      # expl:<id>                 -> full explanation view
CB_BACK_RESULTS = "back" # back                      -> not used across sessions (stateless)
CB_NOOP = "noop"


def command_detail_keyboard(cmd: CiscoCommand, is_favorite: bool) -> InlineKeyboardMarkup:
    fav_label = "\u2b50 Remove Favorite" if is_favorite else "\u2606 Add Favorite"
    rows = [
        [
            InlineKeyboardButton(text="\U0001f5c2 Explain", callback_data=f"{CB_EXPLAIN}:{cmd.id}"),
            InlineKeyboardButton(text="\U0001f504 Convert", callback_data=f"{CB_CONVERT}:{cmd.id}"),
        ],
        [
            InlineKeyboardButton(text=fav_label, callback_data=f"{CB_FAVORITE}:{cmd.id}"),
        ],
        [
            InlineKeyboardButton(
                text=f"\U0001f4c2 {cmd.category}", callback_data=f"{CB_CATEGORY}:{cmd.category}"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def platform_picker_keyboard(cmd: CiscoCommand) -> InlineKeyboardMarkup:
    row = [
        InlineKeyboardButton(
            text=PLATFORM_LABELS[p], callback_data=f"{CB_PLATFORM}:{cmd.id}:{p}"
        )
        for p in ("ios", "ios_xe", "ios_xr", "nx_os")
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row])


def categories_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    rows = []
    row: list[InlineKeyboardButton] = []
    for i, cat in enumerate(categories, start=1):
        row.append(InlineKeyboardButton(text=cat, callback_data=f"{CB_CATEGORY}:{cat}"))
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def search_results_keyboard(results) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{r.command.title}", callback_data=f"{CB_CMD}:{r.command.id}")]
        for r in results
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def command_list_keyboard(commands: list[CiscoCommand]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=c.title, callback_data=f"{CB_CMD}:{c.id}")]
        for c in commands
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def random_again_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="\U0001f3b2 Another random", callback_data=CB_RANDOM)]]
    )
