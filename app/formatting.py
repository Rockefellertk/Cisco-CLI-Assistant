"""
app/formatting.py
------------------
Pure functions that turn a CiscoCommand (or list of them) into the
Markdown-formatted strings sent to Telegram. Kept separate from
handlers.py so message layout can be changed without touching routing
logic, and so it's independently testable.
"""

from __future__ import annotations

from app.commands import PLATFORM_LABELS, PLATFORMS, CiscoCommand


def _escape(text: str) -> str:
    """Escape characters that are special in Telegram legacy Markdown."""
    if not text:
        return text
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text


def format_command_summary(cmd: CiscoCommand) -> str:
    """Short card shown in search results / lists."""
    lines = [f"*{_escape(cmd.title)}*  _(#{cmd.category})_", ""]
    for p in PLATFORMS:
        val = cmd.platform_command(p)
        if cmd.is_supported(p):
            lines.append(f"*{PLATFORM_LABELS[p]}:* `{val}`")
        else:
            lines.append(f"*{PLATFORM_LABELS[p]}:* _not supported_")
    return "\n".join(lines)


def format_command_full(cmd: CiscoCommand) -> str:
    """Full explanation view: purpose, syntax, args, example, output, notes..."""
    lines = [f"*{_escape(cmd.title)}*", f"_Category: {_escape(cmd.category)}_", ""]

    lines.append("*Purpose*")
    lines.append(_escape(cmd.description) or "_No description available._")
    lines.append("")

    lines.append("*Commands by platform*")
    for p in PLATFORMS:
        val = cmd.platform_command(p)
        if cmd.is_supported(p):
            lines.append(f"• *{PLATFORM_LABELS[p]}:* `{val}`")
        else:
            lines.append(f"• *{PLATFORM_LABELS[p]}:* _not supported on this platform_")
    lines.append("")

    if cmd.syntax:
        lines.append("*Syntax*")
        lines.append(f"`{cmd.syntax}`")
        lines.append("")

    if cmd.example:
        lines.append("*Example*")
        lines.append(f"`{cmd.example}`")
        lines.append("")

    if cmd.sample_output:
        lines.append("*Sample Output*")
        lines.append(f"```\n{cmd.sample_output}\n```")
        lines.append("")

    meta_bits = []
    if cmd.privilege_level:
        meta_bits.append(f"*Privilege Level:* {_escape(cmd.privilege_level)}")
    if cmd.configuration_mode:
        meta_bits.append(f"*Configuration Mode:* {_escape(cmd.configuration_mode)}")
    if meta_bits:
        lines.append("\n".join(meta_bits))
        lines.append("")

    if cmd.notes:
        lines.append("*Notes*")
        lines.append(_escape(cmd.notes))
        lines.append("")

    if cmd.related_commands:
        lines.append("*Related Commands*")
        lines.append(", ".join(f"`{r}`" for r in cmd.related_commands))
        lines.append("")

    if cmd.references:
        lines.append("*References*")
        lines.append("\n".join(cmd.references))

    return "\n".join(lines).strip()


def format_platform_single(cmd: CiscoCommand, platform: str) -> str:
    label = PLATFORM_LABELS.get(platform, platform)
    val = cmd.platform_command(platform)
    if not cmd.is_supported(platform):
        return f"*{_escape(cmd.title)}* — *{label}*\n\n_Not supported on this platform._"
    return (
        f"*{_escape(cmd.title)}* — *{label}*\n\n"
        f"`{val}`\n\n"
        f"{_escape(cmd.description)}"
    )


def format_convert_table(cmd: CiscoCommand) -> str:
    lines = [f"*Cross-platform equivalents:* {_escape(cmd.title)}", ""]
    for p in PLATFORMS:
        val = cmd.platform_command(p)
        label = PLATFORM_LABELS[p]
        if cmd.is_supported(p):
            lines.append(f"*{label}*\n`{val}`\n")
        else:
            lines.append(f"*{label}*\n_not supported_\n")
    return "\n".join(lines).strip()


def format_search_no_results(query: str) -> str:
    return (
        f"No matching command found for: `{_escape(query)}`\n\n"
        "I won't guess a Cisco command that isn't in the database.\n"
        "Try rephrasing, use /category to browse, or check spelling."
    )


def format_history_list(commands: list[CiscoCommand]) -> str:
    if not commands:
        return "Your search history is empty."
    lines = ["*Recent lookups:*", ""]
    for c in commands:
        lines.append(f"• {c.title} _(#{c.category})_")
    return "\n".join(lines)


def format_favorites_list(commands: list[CiscoCommand]) -> str:
    if not commands:
        return "You have no favorites yet. Open a command and tap \u2606 Add Favorite."
    lines = ["*Your favorites:*", ""]
    for c in commands:
        lines.append(f"• {c.title} _(#{c.category})_")
    return "\n".join(lines)
