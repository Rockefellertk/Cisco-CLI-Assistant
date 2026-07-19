"""
app/commands.py
----------------
Data models (dataclasses) for a Cisco CLI command record, plus the
in-memory CommandDatabase that loads database/commands.json once at
startup and serves fast lookups to the rest of the app.

Also contains a tiny JSON-backed UserDataStore for per-user favorites
and search history (Feature #13 note: easy to swap for SQLite later —
this module is the only place that touches storage).
"""

from __future__ import annotations

import json
import random
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)

PLATFORMS = ("ios", "ios_xe", "ios_xr", "nx_os")
PLATFORM_LABELS = {
    "ios": "IOS",
    "ios_xe": "IOS-XE",
    "ios_xr": "IOS-XR",
    "nx_os": "NX-OS",
}
NOT_SUPPORTED_MARKERS = {"not supported on this platform", "n/a", "na", ""}


@dataclass(frozen=True)
class CiscoCommand:
    id: str
    title: str
    category: str
    aliases: list[str]
    description: str
    ios: str
    ios_xe: str
    ios_xr: str
    nx_os: str
    syntax: str
    example: str
    sample_output: str
    notes: str
    privilege_level: str
    configuration_mode: str
    related_commands: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "CiscoCommand":
        return cls(
            id=d["id"],
            title=d["title"],
            category=d["category"],
            aliases=list(d.get("aliases", [])),
            description=d.get("description", ""),
            ios=d.get("ios", ""),
            ios_xe=d.get("ios_xe", ""),
            ios_xr=d.get("ios_xr", ""),
            nx_os=d.get("nx_os", ""),
            syntax=d.get("syntax", ""),
            example=d.get("example", ""),
            sample_output=d.get("sample_output", ""),
            notes=d.get("notes", ""),
            privilege_level=d.get("privilege_level", ""),
            configuration_mode=d.get("configuration_mode", ""),
            related_commands=list(d.get("related_commands", [])),
            references=list(d.get("references", [])),
        )

    def platform_command(self, platform: str) -> str:
        return getattr(self, platform, "")

    def is_supported(self, platform: str) -> bool:
        val = self.platform_command(platform).strip().lower()
        return val not in NOT_SUPPORTED_MARKERS

    def searchable_text(self) -> str:
        """All text fields concatenated, used for substring/fuzzy search."""
        parts = [
            self.title,
            self.description,
            self.category,
            " ".join(self.aliases),
            self.ios,
            self.ios_xe,
            self.ios_xr,
            self.nx_os,
        ]
        return " ".join(p for p in parts if p).lower()


class CommandDatabase:
    """Loads commands.json once and keeps everything in memory."""

    def __init__(self, database_dir: Path):
        self._database_dir = database_dir
        self._commands: list[CiscoCommand] = []
        self._by_id: dict[str, CiscoCommand] = {}
        self._categories: list[str] = []
        self._load()

    def _load(self) -> None:
        commands_path = self._database_dir / "commands.json"
        categories_path = self._database_dir / "categories.json"

        if not commands_path.exists():
            raise FileNotFoundError(
                f"Database file not found: {commands_path}. "
                "Run database/generate_db.py first."
            )

        with open(commands_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self._commands = [CiscoCommand.from_dict(c) for c in raw["commands"]]
        self._by_id = {c.id: c for c in self._commands}

        if categories_path.exists():
            with open(categories_path, "r", encoding="utf-8") as f:
                self._categories = json.load(f).get("categories", [])
        else:
            self._categories = sorted({c.category for c in self._commands})

        logger.info(
            "Loaded %d commands across %d categories from %s",
            len(self._commands),
            len(self._categories),
            commands_path,
        )

    @property
    def commands(self) -> list[CiscoCommand]:
        return self._commands

    @property
    def categories(self) -> list[str]:
        return self._categories

    def get(self, command_id: str) -> Optional[CiscoCommand]:
        return self._by_id.get(command_id)

    def by_category(self, category: str) -> list[CiscoCommand]:
        return [c for c in self._commands if c.category.lower() == category.lower()]

    def random(self) -> CiscoCommand:
        return random.choice(self._commands)

    def count(self) -> int:
        return len(self._commands)


class UserDataStore:
    """
    Minimal JSON-backed persistence for favorites & search history.
    Structure: { "<user_id>": {"favorites": [ids], "history": [ids]} }

    Guarded by a lock since aiogram handlers can run concurrently within
    the single-process event loop; file writes are cheap at this scale
    and this keeps the implementation dependency-free. Swap for SQLite
    (see README) once usage grows.
    """

    def __init__(self, path: Path, history_limit: int = 20):
        self._path = path
        self._history_limit = history_limit
        self._lock = threading.Lock()
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            with open(self._path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {}
            self._save()

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def _user(self, user_id: int) -> dict:
        key = str(user_id)
        if key not in self._data:
            self._data[key] = {"favorites": [], "history": []}
        return self._data[key]

    def add_history(self, user_id: int, command_id: str) -> None:
        with self._lock:
            u = self._user(user_id)
            if command_id in u["history"]:
                u["history"].remove(command_id)
            u["history"].insert(0, command_id)
            u["history"] = u["history"][: self._history_limit]
            self._save()

    def get_history(self, user_id: int) -> list[str]:
        return list(self._user(user_id)["history"])

    def toggle_favorite(self, user_id: int, command_id: str) -> bool:
        """Returns True if now favorited, False if removed."""
        with self._lock:
            u = self._user(user_id)
            if command_id in u["favorites"]:
                u["favorites"].remove(command_id)
                self._save()
                return False
            u["favorites"].append(command_id)
            self._save()
            return True

    def get_favorites(self, user_id: int) -> list[str]:
        return list(self._user(user_id)["favorites"])
