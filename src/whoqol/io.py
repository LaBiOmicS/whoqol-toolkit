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
_NUM_HEADER = [
    # Q1, q01, Q_1, item1, item_01, whoqol1, wq1, wb1, P1, questao 1, pregunta 1
    re.compile(r"^(?:q|item|whoqol(?:\s?bref)?|wq|wb|p|questao|quest|pergunta|pregunta)\s?0*(\d{1,3})$"),
    # "1. Como você avaliaria..." / "1 - ..." / "1) ..." / "Q1. ..."
    re.compile(r"^(?:q|questao|pergunta|pregunta|item)?\s?0*(\d{1,3})\s?(?:\.|\)|:|\s)\s?\D"),
]


def _match_column(col: str, inst: Instrument) -> tuple[str | None, str]:
    norm = normalize_text(col)
    raw = str(col).strip().lower()
    n_items = len(inst.items)
    for rx in _NUM_HEADER:
        m = rx.match(norm) or rx.match(raw)
        if m and 1 <= int(m.group(1)) <= n_items:
            return inst.items[int(m.group(1)) - 1], "number"
    hits = []
    for item, pats in inst.item_patterns.items():
        for rank, p in enumerate(pats):
            if re.search(p, norm):
                hits.append((item, rank, len(p)))
                break
    if not hits:
        return None, ""
    if len(hits) == 1:
        return hits[0][0], "text"
    hits.sort(key=lambda h: (-h[2], h[1]))  # most specific (longest) pattern wins
    return hits[0][0], "text-ambiguous:" + ",".join(h[0] for h in hits)


def detect_mapping(df: pd.DataFrame, instrument: str | Instrument | None = None) -> dict[str, Any]:
    """Proposes {item: column}. Also returns unmapped items, conflicts and the remaining columns."""
    inst = get_instrument(instrument)
    candidates: dict[str, list[tuple[str, str]]] = {it: [] for it in inst.items}
    for col in df.columns:
        item, how = _match_column(col, inst)
        if item:
            candidates[item].append((col, how))

    mapping: dict[str, str] = {}
    conflicts: dict[str, list[str]] = {}
    for item, cands in candidates.items():
        if not cands:
            continue
        ranked = sorted(cands, key=lambda c: (-_likert_score(df[c[0]]), c[1] != "number"))
        mapping[item] = ranked[0][0]
        if len(cands) > 1:
            conflicts[item] = [c[0] for c in cands]

    if len(mapping) < int(0.75 * len(inst.items)):
        block = _find_likert_block(df, len(inst.items))
        if block:
            mapping = dict(zip(inst.items, block, strict=True))
            conflicts = {"_warning": [f"POSITIONAL mapping ({len(inst.items)} consecutive Likert columns). "
                                      "Confirm the order with the user before analysing."]}
    used = set(mapping.values())
    return {"mapping": mapping, "missing_items": [it for it in inst.items if it not in mapping],
            "conflicts": conflicts, "other_columns": [c for c in df.columns if c not in used]}


def _likert_score(s: pd.Series) -> float:
    nonmiss = s.notna().sum()
    return 0.0 if nonmiss == 0 else float(recode_series(s).notna().sum() / nonmiss)


def _find_likert_block(df: pd.DataFrame, k: int) -> list[str] | None:
    cols = list(df.columns)
    ok = [(_likert_score(df[c]) >= 0.9 and df[c].notna().sum() > 0) for c in cols]
    for start in range(len(cols) - k + 1):
        if all(ok[start:start + k]):
            return cols[start:start + k]
    return None


# ------------------------------------------------------------- recoding
_LEADING_NUM = re.compile(r"^\s*([1-5])(?:[.,]0+)?\s*(?:$|[-–—=:.)\s])")


def recode_value(v: Any) -> float:
    """Answer (number or anchor text in PT/EN/ES) -> 1-5; NaN when invalid or missing."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan
    if isinstance(v, (int, np.integer, float, np.floating)) and not isinstance(v, bool):
        f = float(v)
        return f if f in (1.0, 2.0, 3.0, 4.0, 5.0) else np.nan
    s = str(v).strip()
    norm = normalize_text(s)
    if norm in MISSING_TOKENS:
        return np.nan
    m = _LEADING_NUM.match(s)
    if m:
        return float(m.group(1))
    if norm in RESPONSE_ANCHORS and norm not in AMBIGUOUS_ANCHORS:
        return float(RESPONSE_ANCHORS[norm])
    try:
        f = float(s.replace(",", "."))
        return f if f in (1.0, 2.0, 3.0, 4.0, 5.0) else np.nan
    except ValueError:
        return np.nan


def recode_series(s: pd.Series) -> pd.Series:
    return s.map(recode_value).astype(float)


def unrecognized_values(s: pd.Series) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in s.dropna():
        if np.isnan(recode_value(v)) and normalize_text(v) not in MISSING_TOKENS:
            out[str(v)] = out.get(str(v), 0) + 1
    return out


def parse_mapping(mapping: str | dict | None, instrument: str | Instrument | None = None) -> dict[str, str] | None:
    """dict, JSON string or .json path. Keys 'Q1' / '1' / 'q01' are normalized to the instrument's item ids."""
    if mapping in (None, "", {}):
        return None
    inst = get_instrument(instrument)
    if isinstance(mapping, str):
        p = Path(mapping).expanduser()
        mapping = json.loads(p.read_text(encoding="utf-8")) if p.suffix == ".json" and p.exists() else json.loads(mapping)
    out = {}
    for k, v in mapping.items():
        m = re.search(r"(\d{1,3})", str(k))
        if not m or not 1 <= int(m.group(1)) <= len(inst.items):
            raise ValueError(f"Invalid mapping key: {k!r}")
        out[inst.items[int(m.group(1)) - 1]] = str(v)
    return out


def build_item_frame(df: pd.DataFrame, mapping: dict[str, str],
                     instrument: str | Instrument | None = None) -> tuple[pd.DataFrame, dict]:
    inst = get_instrument(instrument)
    missing_cols = [c for c in mapping.values() if c not in df.columns]
    if missing_cols:
        raise KeyError(f"Mapped columns not found in the spreadsheet: {missing_cols}")
    absent = [it for it in inst.items if it not in mapping]
    if absent:
        raise ValueError(f"Items without a column: {absent}. Provide the full mapping.")
    items = pd.DataFrame({it: recode_series(df[mapping[it]]) for it in inst.items}, index=df.index)
    report = {it: bad for it in inst.items if (bad := unrecognized_values(df[mapping[it]]))}
    return items, report


# --------------------------------------------------- language of the version
def detect_version_language(df: pd.DataFrame, mapping: dict[str, str],
                            instrument: str | Instrument | None = None) -> dict:
    """Language of the administered version (pt/en/es), from text answers and item headers."""
    inst = get_instrument(instrument)
    votes: Counter = Counter()
    for col in mapping.values():
        for v in df[col].dropna().astype(str).unique()[:20]:
            langs = ANCHOR_LANGS.get(normalize_text(re.sub(r"^\s*[1-5]\s*[-–—=:.)]?\s*", "", v)), set())
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
