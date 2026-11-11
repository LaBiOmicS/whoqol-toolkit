"""Spreadsheet reading, item column detection, response recoding and language-version detection."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .anchors import AMBIGUOUS_ANCHORS, ANCHOR_LANGS, MISSING_TOKENS, RESPONSE_ANCHORS, normalize_text
from .instruments import Instrument, get_instrument
from .instruments.base import code_key
from .security import column_ref

SPREADSHEET_SUFFIXES = {".xlsx", ".xlsm", ".xls", ".ods"}


# ---------------------------------------------------------------- reading
def load_table(path: str | Path, sheet: str | int | None = None) -> pd.DataFrame:
    path = Path(path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suf = path.suffix.lower()
    if suf in SPREADSHEET_SUFFIXES:
        df = pd.read_excel(path, sheet_name=0 if sheet is None else sheet)
    elif suf in {".csv", ".txt"}:
        df = _read_csv_sniff(path)
    elif suf == ".tsv":
        df = pd.read_csv(path, sep="\t")
    elif suf == ".sav":
        df = pd.read_spss(path)
    else:
        raise ValueError(f"Unsupported format: {suf} (use .xlsx, .xls, .ods, .csv, .tsv or .sav)")
    df.columns = [str(c).strip() for c in df.columns]
    return df.dropna(how="all").reset_index(drop=True)


def _read_csv_sniff(path: Path) -> pd.DataFrame:
    for enc in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(path, sep=None, engine="python", encoding=enc)
            if df.shape[1] == 1 and ";" in str(df.columns[0]):
                df = pd.read_csv(path, sep=";", encoding=enc)
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode the CSV file (save it as UTF-8).")


def list_sheets(path: str | Path) -> list[str]:
    path = Path(path).expanduser()
    if path.suffix.lower() in SPREADSHEET_SUFFIXES:
        return [str(s) for s in pd.ExcelFile(path).sheet_names]
    return []


# -------------------------------------------------------- column detection
_NUM_PREFIX = r"(?:q|item|whoqol(?:\s?bref)?|wq|wb|p|questao|quest|pergunta|pregunta)"
_NUM_HEADER = [
    # Q1, q01, Q_1, item1, item_01, whoqol1, wq1, wb1, P1, questao 1, pregunta 1
    re.compile(rf"^{_NUM_PREFIX}\s?0*(\d{{1,3}})$"),
    # "1. Como você avaliaria..." / "1 - ..." / "1) ..." / "Q1. ..."
    re.compile(r"^(?:q|questao|pergunta|pregunta|item)?\s?0*(\d{1,3})\s?(?:\.|\)|:|\s)\s?\D"),
]
# first token of a header that starts with an item code: "F1.2 Você se preocupa...", "SP3.1) ...", "old_05 - ..."
_CODE_TOKEN = re.compile(r"^\s*([A-Za-z]{1,6}[\s_.-]?\d{1,3}(?:[._]\d{1,2})?)(?=$|[\s).:=-])")
_PRIORITY = {"code": 0, "number": 1, "text": 2}


def _text_key(s: str) -> str:
    return normalize_text(s).replace("(", "").replace(")", "").replace("/", " ").strip()


def _text_match(norm_header: str, inst: Instrument) -> list[str]:
    """Items whose full question (any language) is contained in the header, or vice versa (header >= 25 chars)."""
    h = _text_key(norm_header)
    hits: dict[str, int] = {}
    for texts in inst.item_text.values():
        for it, txt in texts.items():
            k = _text_key(txt)
            if len(k) >= 15 and (k in h or (len(h) >= 25 and h in k)):
                hits[it] = max(hits.get(it, 0), len(k))
    if not hits:
        return []
    best = max(hits.values())
    return [it for it, n in hits.items() if n == best]


def _match_column(col: str, inst: Instrument) -> tuple[str | None, str]:
    raw = str(col).strip()
    codes = inst.header_codes()
    if (it := codes.get(code_key(raw))) is not None:
        return it, "code"
    if (m := _CODE_TOKEN.match(raw)) and (it := codes.get(code_key(m.group(1)))) is not None:
        return it, "code"
    norm = normalize_text(col)
    numbering = inst.numbering()
    for rx in _NUM_HEADER:
        m = rx.match(norm) or rx.match(raw.lower())
        if m and int(m.group(1)) in numbering:
            return numbering[int(m.group(1))], "number"
    hits = []
    for item, pats in inst.item_patterns.items():
        for rank, p in enumerate(pats):
            if re.search(p, norm):
                hits.append((item, rank, len(p)))
                break
    if not hits:
        found = _text_match(norm, inst)
        if len(found) == 1:
            return found[0], "text"
        return (found[0], "text-ambiguous:" + ",".join(found)) if found else (None, "")
    if len(hits) == 1:
        return hits[0][0], "text"
    hits.sort(key=lambda h: (-h[2], h[1]))  # most specific (longest) pattern wins
    return hits[0][0], "text-ambiguous:" + ",".join(h[0] for h in hits)


def detect_mapping(df: pd.DataFrame, instrument: str | Instrument | None = None) -> dict[str, Any]:
    """Proposes {item: column}. Also returns unmapped items, conflicts and the remaining columns."""
    inst = get_instrument(instrument)
    if inst.derived_from:
        derived = _derived_mapping(df, inst)
        if derived:
            return derived
    candidates: dict[str, list[tuple[str, str]]] = {it: [] for it in inst.items}
    for col in df.columns:
        item, how = _match_column(col, inst)
        if item:
            candidates[item].append((col, how))

    mapping: dict[str, str] = {}
    conflicts: dict[str, list[str]] = {}
    by_number = False
    for item, cands in candidates.items():
        if not cands:
            continue
        ranked = sorted(cands, key=lambda c: (-_likert_score(df[c[0]], inst.item_max(item)),
                                              _PRIORITY.get(c[1].split("-")[0], 2)))
        mapping[item] = ranked[0][0]
        by_number |= ranked[0][1] == "number"
        if len(cands) > 1:
            conflicts[item] = [c[0] for c in cands]

    numbering = inst.numbering()
    order = [numbering[n] for n in sorted(numbering)]
    if len(mapping) < int(0.75 * len(inst.items)) and sorted(order) == sorted(inst.items):
        block = _find_likert_block(df, len(inst.items), inst.scale_max)
        if block:
            mapping = dict(zip(order, block, strict=True))
            conflicts = {"_warning": [f"POSITIONAL mapping ({len(inst.items)} consecutive Likert columns). "
                                      "Confirm the order with the user before analysing."]}
    elif by_number and inst.number_note:
        conflicts["_note"] = [f"Some items were matched by question number: {inst.number_note}"]
    used = set(mapping.values())
    return {"mapping": mapping, "missing_items": [it for it in inst.items if it not in mapping],
            "conflicts": conflicts, "other_columns": [c for c in df.columns if c not in used]}


def _derived_mapping(df: pd.DataFrame, inst: Instrument) -> dict[str, Any] | None:
    """Instruments made of items of another one (EUROHIS-QOL 8 from the WHOQOL-BREF): when the sheet holds the
    parent questionnaire, map through it (its numbering differs, so Q10 of the BREF is item 7 of the EUROHIS)."""
    base_key, translation = inst.derived_from
    base = get_instrument(base_key)
    det = detect_mapping(df, base)
    if len(det["mapping"]) < base.min_valid_total:
        return None
    mapping = {it: det["mapping"][b] for it, b in translation.items() if b in det["mapping"]}
    used = set(mapping.values())
    conflicts = {k: v for k, v in det["conflicts"].items() if k.startswith("_") or k in translation.values()}
    conflicts["_note"] = [f"The spreadsheet holds the {base.name}; {inst.name} items were taken from its columns ("
                          + ", ".join(f"{a} = {b}" for a, b in translation.items()) + ")."]
    return {"mapping": mapping, "missing_items": [it for it in inst.items if it not in mapping],
            "conflicts": conflicts, "other_columns": [c for c in df.columns if c not in used]}


def _likert_score(s: pd.Series, max_value: int = 5) -> float:
    nonmiss = s.notna().sum()
    return 0.0 if nonmiss == 0 else float(recode_series(s, max_value).notna().sum() / nonmiss)


def _find_likert_block(df: pd.DataFrame, k: int, max_value: int = 5) -> list[str] | None:
    cols = list(df.columns)
    ok = [(_likert_score(df[c], max(max_value, 5)) >= 0.9 and df[c].notna().sum() > 0) for c in cols]
    for start in range(len(cols) - k + 1):
        if all(ok[start:start + k]):
            return cols[start:start + k]
    return None


# ------------------------------------------------------------- recoding
_LEADING_NUM = re.compile(r"^\s*([1-9])(?:[.,]0+)?\s*(?:$|[-–—=:.)\s])")


def recode_value(v: Any, max_value: int = 5) -> float:
    """Answer (number, or anchor text in PT/EN/ES on five-point scales) -> 1..max_value; NaN when invalid or
    missing. Anchor texts are only read on five-point scales: on 3-point scales the same words mean other values."""
    valid = {float(k) for k in range(1, max_value + 1)}
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan
    if isinstance(v, (int, np.integer, float, np.floating)) and not isinstance(v, bool):
        f = float(v)
        return f if f in valid else np.nan
    s = str(v).strip()
    norm = normalize_text(s)
    if norm in MISSING_TOKENS:
        return np.nan
    m = _LEADING_NUM.match(s)
    if m:
        f = float(m.group(1))
        return f if f in valid else np.nan
    if max_value == 5 and norm in RESPONSE_ANCHORS and norm not in AMBIGUOUS_ANCHORS:
        return float(RESPONSE_ANCHORS[norm])
    try:
        f = float(s.replace(",", "."))
        return f if f in valid else np.nan
    except ValueError:
        return np.nan


def recode_series(s: pd.Series, max_value: int = 5) -> pd.Series:
    return s.map(lambda v: recode_value(v, max_value)).astype(float)


def unrecognized_values(s: pd.Series, max_value: int = 5) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in s.dropna():
        if np.isnan(recode_value(v, max_value)) and normalize_text(v) not in MISSING_TOKENS:
            out[str(v)] = out.get(str(v), 0) + 1
    return out


def resolve_item_key(key: Any, instrument: str | Instrument | None = None) -> str | None:
    """Item id from an item id or code ('Q1', 'F1.1', 'old_05', 'SP3.1', 'HBREF_2') or a question number
    ('1', 'q01'); None when it does not name an item of the instrument."""
    inst = get_instrument(instrument)
    item = inst.header_codes().get(code_key(key))
    if item is None:
        m = re.fullmatch(r"\s*[A-Za-z]{0,9}[\s_.-]?0*(\d{1,3})\s*", str(key))
        item = inst.numbering().get(int(m.group(1))) if m else None
    return item


def parse_mapping(mapping: str | dict | None, instrument: str | Instrument | None = None) -> dict[str, str] | None:
    """dict, JSON string or .json path. Keys are item ids or codes ('Q1', 'F1.1', 'old_05', 'SP3.1') or question
    numbers ('1', 'q01'), normalized to the instrument's item ids."""
    if mapping in (None, "", {}):
        return None
    inst = get_instrument(instrument)
    if isinstance(mapping, str):
        p = Path(mapping).expanduser()
        mapping = json.loads(p.read_text(encoding="utf-8")) if p.suffix == ".json" and p.exists() else json.loads(mapping)
    out = {}
    for k, v in mapping.items():
        item = resolve_item_key(k, inst)
        if item is None:
            raise ValueError(f"Invalid mapping key for {inst.name}: {k!r}")
        out[item] = str(v)
    return out


def build_item_frame(df: pd.DataFrame, mapping: dict[str, str],
                     instrument: str | Instrument | None = None) -> tuple[pd.DataFrame, dict]:
    inst = get_instrument(instrument)
    mapping = {it: column_ref(list(df.columns), c) for it, c in mapping.items()}
    missing_cols = [c for c in mapping.values() if c not in df.columns]
    if missing_cols:
        raise KeyError(f"Mapped columns not found in the spreadsheet: {missing_cols}")
    absent = [it for it in inst.items if it not in mapping]
    if absent:
        raise ValueError(f"Items without a column: {absent}. Provide the full mapping.")
    items = pd.DataFrame({it: recode_series(df[mapping[it]], inst.item_max(it)) for it in inst.items}, index=df.index)
    report = {it: bad for it in inst.items if (bad := unrecognized_values(df[mapping[it]], inst.item_max(it)))}
    return items, report


# --------------------------------------------------- language of the version
def detect_version_language(df: pd.DataFrame, mapping: dict[str, str],
                            instrument: str | Instrument | None = None) -> dict:
    """Language of the administered version (pt/en/es), from text answers and item headers."""
    inst = get_instrument(instrument)
    votes: Counter = Counter()
    for col in mapping.values():
        for v in df[col].dropna().astype(str).unique()[:20]:
            langs = ANCHOR_LANGS.get(normalize_text(re.sub(r"^\s*[1-9]\s*[-–—=:.)]?\s*", "", v)), set())
            if len(langs) == 1:
                votes[next(iter(langs))] += 1
        norm = normalize_text(col)
        for lang, texts in inst.item_text.items():
            for txt in texts.values():
                key = normalize_text(txt)[:25]
                if len(key) > 10 and key in norm:
                    votes[lang] += 3
                    break
    if not votes:
        return {"language": None, "evidence": {}}
    lang, n = votes.most_common(1)[0]
    return {"language": lang, "evidence": dict(votes), "confidence": round(n / sum(votes.values()), 2)}
