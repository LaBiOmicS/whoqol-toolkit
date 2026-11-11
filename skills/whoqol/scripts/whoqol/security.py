"""Sanitising spreadsheet text before it reaches the agent.

Column names and cell values come from respondents or third parties. The agent reads them in the JSON printed by the
CLI, so they are cleaned (control, zero-width and bidi characters removed, whitespace collapsed, length capped) and
text that looks like instructions to an AI is flagged for the user instead of being passed on silently.
"""

from __future__ import annotations

import re
import unicodedata

# Zero-width and bidirectional controls can hide or reorder text (Trojan Source style).
_INVISIBLE = re.compile("[​-‏‪-‮⁠-⁤⁦-⁩﻿]")
_SPACES = re.compile(r"\s+")

_INSTRUCTION_PATTERNS = [
    # English
    r"\bignore (all |any )?(the )?(previous|prior|above|earlier)\b",
    r"\b(system|developer) (prompt|message|instructions?)\b",
    r"\byou are (now )?(an?|the) (ai|assistant|model|language model)\b",
    r"\b(disregard|forget|override) (all |your |the )?(instructions|rules)\b",
    r"\b(run|execute) (the )?(following )?(command|code|script)\b",
    r"\bassistant\s*:",
    # Portuguese
    r"\bignor[ea] (todas )?(as )?instru[çc][õo]es\b",
    r"\b(desconsidere|esque[çc]a) (as |todas as )?(instru[çc][õo]es|regras)\b",
    r"\bvoc[êe] [ée] (agora )?(um|uma|o|a) (ia|assistente|modelo)\b",
    r"\bexecute (o |este |o seguinte )?(comando|c[óo]digo|script)\b",
    # Spanish
    r"\bignora (todas )?(las )?instrucciones\b",
    r"\b(olvida|descarta) (las |todas las )?(instrucciones|reglas)\b",
    r"\b(eres|usted es) (ahora )?(un|una|el|la) (ia|asistente|modelo)\b",
    r"\bejecuta (el |este |el siguiente )?(comando|c[óo]digo|script)\b",
]
_INSTRUCTION_RE = re.compile("|".join(_INSTRUCTION_PATTERNS), re.IGNORECASE)

COLUMN_LIMIT = 120
VALUE_LIMIT = 60


def clean(text: object, limit: int = VALUE_LIMIT) -> str:
    """Printable, single-line, length-capped version of a header or cell value."""
    s = unicodedata.normalize("NFKC", str(text))
    s = _INVISIBLE.sub("", s)
    s = "".join(ch if ch.isprintable() else " " for ch in s)
    s = _SPACES.sub(" ", s).strip()
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def risk(text: object) -> str | None:
    """Reason why a header or value deserves the user's attention, or None."""
    raw = str(text)
    if _INVISIBLE.search(raw):
        return "hidden characters (zero-width or bidirectional controls)"
    if _INSTRUCTION_RE.search(unicodedata.normalize("NFKC", raw)):
        return "text that looks like instructions to an AI assistant"
    return None


def column_ref(df_columns, name: str) -> str:
    """Resolve '#n' (1-based column position, as printed by `inspect`) to the real column name."""
    m = re.fullmatch(r"#(\d+)", str(name).strip())
    if m and 1 <= int(m.group(1)) <= len(df_columns):
        return str(df_columns[int(m.group(1)) - 1])
    return name
