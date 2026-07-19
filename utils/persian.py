"""
utils/persian.py
-----------------
Small, dependency-free helpers for normalizing Persian (Farsi) text so it
can be compared/matched against the database aliases regardless of the
particular Unicode forms the user typed (Arabic vs Persian ی/ك, zero-width
non-joiner usage, diacritics, etc.), and a lightweight keyword translation
table for common Persian networking phrases -> English search terms.
"""

from __future__ import annotations

import re

# Arabic -> Persian canonicalization
_CHAR_MAP = {
    "\u064a": "\u06cc",  # Arabic Yeh -> Persian Yeh (ي -> ی)
    "\u0643": "\u06a9",  # Arabic Kaf -> Persian Kaf (ك -> ک)
    "\u0629": "\u0647",  # Teh Marbuta -> Heh (ة -> ه)
    "\u06c0": "\u0647",  # Heh Goal -> Heh
    "\u0621": "",         # Hamza, strip
}

_DIACRITICS = re.compile(
    "[\u064b-\u065f\u0670\u06d6-\u06dc\u06df-\u06e8\u06ea-\u06ed]"
)
_ZWNJ = "\u200c"
_TATWEEL = "\u0640"

# Common Persian networking phrases -> English keywords that appear in our
# alias index. This is intentionally small and hand-curated; the fuzzy
# matcher handles anything not covered here.
PERSIAN_KEYWORDS = {
    "نمایش": "show",
    "چطور": "how",
    "چگونه": "how",
    "میخوام": "want",
    "می‌خوام": "want",
    "بگیرم": "get",
    "ببینم": "see",
    "جدول": "table",
    "مک": "mac",
    "آدرس": "address",
    "پینگ": "ping",
    "ترافیک": "traffic",
    "همسایه": "neighbor",
    "همسایه‌ها": "neighbors",
    "وضعیت": "status",
    "کانفیگ": "config",
    "پیکربندی": "config",
    "فعال": "enable",
    "غیرفعال": "disable",
    "مسیریابی": "routing",
    "مسیر": "route",
    "خلاصه": "summary",
    "جزئیات": "detail",
    "دیتابیس": "database",
    "لاگ": "logging",
    "دیباگ": "debug",
    "امنیت": "security",
    "پورت": "port",
    "اینترفیس": "interface",
    "لیست": "list",
    "پاک": "clear",
    "ریست": "reset",
    "ذخیره": "save",
    "دستگاه": "device",
    "روتر": "router",
    "سوییچ": "switch",
    "سویچ": "switch",
    "حافظه": "memory",
    "مصرف": "usage",
    "دما": "temperature",
}


def normalize(text: str) -> str:
    """Canonicalize Persian/Arabic text for comparison purposes."""
    if not text:
        return ""
    out = text.strip().lower()
    for src, dst in _CHAR_MAP.items():
        out = out.replace(src, dst)
    out = out.replace(_ZWNJ, " ").replace(_TATWEEL, "")
    out = _DIACRITICS.sub("", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def translate_keywords(text: str) -> str:
    """
    Append English equivalents for recognized Persian keywords found in
    `text`, so the fuzzy/substring matcher has English tokens to compare
    against the (mostly English) command database fields.
    """
    normalized = normalize(text)
    extra_terms = []
    for fa_word, en_word in PERSIAN_KEYWORDS.items():
        if normalize(fa_word) in normalized:
            extra_terms.append(en_word)
    if extra_terms:
        return f"{normalized} {' '.join(extra_terms)}"
    return normalized


def contains_persian(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text or ""))
