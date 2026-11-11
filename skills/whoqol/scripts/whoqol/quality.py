"""Data quality: missingness, invalid answers, suspicious response patterns, floor/ceiling effects."""

from __future__ import annotations

import pandas as pd

from .instruments import Instrument


def data_quality(raw_df: pd.DataFrame, items: pd.DataFrame, mapping: dict[str, str], recode_report: dict,
                 inst: Instrument, id_col: str | None = None) -> dict:
    n = len(items)
    miss_item = items.isna().mean().mul(100).round(2)
    n_valid = items.notna().sum(axis=1)
    excluded = int((n_valid < inst.min_valid_total).sum())

    # identical answers to every item ("straight-lining"): inconsistent with reverse-coded items
    full = items.dropna()
    straight = full.index[full.nunique(axis=1) == 1].tolist()

    dom_missing = {}
    for key, d in inst.domains.items():
        if d.composite:  # computed from facet scores; see the facet entries
            continue
        valid = items[list(d.items)].notna().sum(axis=1)
        dom_missing[key] = int(((valid < d.min_valid) & (n_valid >= inst.min_valid_total)).sum())

    dup_ids = []
    if id_col and id_col in raw_df.columns:
        dup_ids = raw_df[id_col][raw_df[id_col].duplicated(keep=False)].astype(str).unique().tolist()

    return {
        "n_rows": n,
        "n_complete": int((n_valid == len(inst.items)).sum()),
        "n_excluded": excluded,
        "n_analyzed": n - excluded,
        "min_valid_items": inst.min_valid_total,
        "pct_missing_by_item": miss_item.to_dict(),
        "pct_missing_overall": round(float(items.isna().values.mean() * 100), 2),
        "items_with_gt5pct_missing": [k for k, v in miss_item.items() if v > 5],
        "unrecognized_values": recode_report,
        "straightlining_rows": [int(i) for i in straight],
        "domains_not_computable": dom_missing,
        "duplicate_ids": dup_ids,
        "duplicate_response_patterns": int(items.duplicated(keep="first").sum()) if n else 0,
        "mapping_used": mapping,
        "warnings": [],
    }


def floor_ceiling(scores: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """% at 0 and 100. > 15% indicates a floor/ceiling effect (Terwee et al., 2007)."""
    rows = []
    for c in cols:
        s = scores[c].dropna()
        if s.empty:
            continue
        floor = (s <= 1e-9).mean() * 100
        ceil = (s >= 100 - 1e-9).mean() * 100
        rows.append({"score": c, "n": len(s), "floor_pct": round(floor, 1), "ceiling_pct": round(ceil, 1),
                     "floor_effect": bool(floor > 15), "ceiling_effect": bool(ceil > 15)})
    return pd.DataFrame(rows)
