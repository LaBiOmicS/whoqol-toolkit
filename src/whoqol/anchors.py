"""Response anchors shared by the WHOQOL family (five-point scales) in Portuguese, English and Spanish.

Every WHOQOL instrument uses the same five response scales (evaluation, satisfaction, intensity,
capacity, frequency). Text answers exported by Google Forms, REDCap, LimeSurvey, etc. are mapped to
1-5 here; the language of the matched anchors also tells which language version was administered.
"""

from __future__ import annotations

import re
import unicodedata

LANGS = ("pt", "en", "es")


def normalize_text(s: object) -> str:
    """Lower case, no accents, hyphens/underscores as spaces, collapsed whitespace."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("-", " ").replace("_", " ")
    s = re.sub(r"[^\w\s()/]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# (language, [anchor 1, ..., anchor 5])
_SCALES: list[tuple[str, list[str]]] = [
    # ---- Portuguese (Brazil; Fleck et al., 2000) ----
    ("pt", ["muito ruim", "ruim", "nem ruim nem boa", "boa", "muito boa"]),
    ("pt", ["muito ruim", "ruim", "nem ruim nem bom", "bom", "muito bom"]),
    ("pt", ["muito insatisfeito", "insatisfeito", "nem satisfeito nem insatisfeito", "satisfeito", "muito satisfeito"]),
    ("pt", ["muito insatisfeita", "insatisfeita", "nem satisfeita nem insatisfeita", "satisfeita", "muito satisfeita"]),
    ("pt", ["muito insatisfeito(a)", "insatisfeito(a)", "nem satisfeito(a) nem insatisfeito(a)", "satisfeito(a)",
            "muito satisfeito(a)"]),
    ("pt", ["nada", "muito pouco", "mais ou menos", "bastante", "extremamente"]),
    ("pt", ["nada", "muito pouco", "medio", "muito", "completamente"]),
    ("pt", ["nunca", "algumas vezes", "frequentemente", "muito frequentemente", "sempre"]),
    # ---- English (WHO generic version) ----
    ("en", ["very poor", "poor", "neither poor nor good", "good", "very good"]),
    ("en", ["very dissatisfied", "dissatisfied", "neither satisfied nor dissatisfied", "satisfied", "very satisfied"]),
    ("en", ["not at all", "a little", "a moderate amount", "very much", "an extreme amount"]),
    ("en", ["not at all", "a little", "a moderate amount", "very much", "extremely"]),
    ("en", ["not at all", "a little", "moderately", "mostly", "completely"]),
    ("en", ["never", "seldom", "quite often", "very often", "always"]),
    # ---- Spanish (Spain, Lucas, 1998; and common Latin American wordings) ----
    ("es", ["muy mal", "poco", "lo normal", "bastante bien", "muy bien"]),
    ("es", ["muy mala", "mala", "ni buena ni mala", "buena", "muy buena"]),
    ("es", ["muy malo", "malo", "ni bueno ni malo", "bueno", "muy bueno"]),
    ("es", ["muy insatisfecho", "poco", "lo normal", "bastante satisfecho", "muy satisfecho"]),
    ("es", ["muy insatisfecho", "insatisfecho", "ni satisfecho ni insatisfecho", "satisfecho", "muy satisfecho"]),
    ("es", ["muy insatisfecha", "insatisfecha", "ni satisfecha ni insatisfecha", "satisfecha", "muy satisfecha"]),
    ("es", ["muy insatisfecho(a)", "insatisfecho(a)", "ni satisfecho(a) ni insatisfecho(a)", "satisfecho(a)",
            "muy satisfecho(a)"]),
    ("es", ["nada", "un poco", "lo normal", "bastante", "extremadamente"]),
    ("es", ["nada", "un poco", "moderadamente", "bastante", "extremadamente"]),
    ("es", ["nada", "un poco", "moderado", "bastante", "totalmente"]),
    ("es", ["nada", "un poco", "moderadamente", "bastante", "totalmente"]),
    ("es", ["nunca", "raramente", "medianamente", "frecuentemente", "siempre"]),
    ("es", ["nunca", "rara vez", "medianamente", "frecuentemente", "siempre"]),
]

RESPONSE_ANCHORS: dict[str, int] = {}
ANCHOR_LANGS: dict[str, set[str]] = {}
_conflicts: list[str] = []
for _lang, _values in _SCALES:
    for _i, _v in enumerate(_values, start=1):
        _k = normalize_text(_v)
        if _k in RESPONSE_ANCHORS and RESPONSE_ANCHORS[_k] != _i:
            _conflicts.append(_k)
        RESPONSE_ANCHORS.setdefault(_k, _i)
        ANCHOR_LANGS.setdefault(_k, set()).add(_lang)
# Anchors whose position differs between scales cannot be decoded without the item's scale:
# recode_value() leaves them missing (reported as unrecognized). Kept empty by test_anchors_unambiguous.
AMBIGUOUS_ANCHORS = frozenset(_conflicts)

MISSING_TOKENS = {
    "", "na", "n/a", "nan", "none", "null", "-", "--", ".", "missing",
    "ns", "nr", "nao respondeu", "sem resposta", "nao sei", "ausente",
    "ns/nc", "no sabe", "no responde", "sin respuesta", "no contesta",
    "no answer", "don t know", "dont know", "refused",
    "999", "99", "9", "-9", "-99", "-999",
}
