"""WHOQOL scoring (WHO manual rules), generic over instruments."""

from __future__ import annotations

import pandas as pd

from .instruments import Instrument, get_instrument


def reverse_items(items: pd.DataFrame, inst: Instrument) -> pd.DataFrame:
    out = items.copy()
    for it in inst.reversed_items:
        out[it] = 6 - out[it]
    return out


def score(items: pd.DataFrame, instrument: str | Instrument | None = None, include_total: bool = False) -> pd.DataFrame:
    """Items already recoded to 1-5 (NOT reversed). Returns per respondent:
    n_valid_items, excluded (fewer than the minimum valid items), <domain>_raw (4-20) and
    <domain>_0_100 for every domain, and optionally total_* (mean of all items; NOT an official score)."""
    inst = get_instrument(instrument)
    rev = reverse_items(items[list(inst.items)], inst)
    n_valid = rev.notna().sum(axis=1)
    excluded = n_valid < inst.min_valid_total
    lo, hi = inst.raw_range()
    out = pd.DataFrame(index=items.index)
    out["n_valid_items"] = n_valid
    out["excluded"] = excluded
    for key, d in inst.domains.items():
        sub = rev[list(d.items)]
        raw = (sub.mean(axis=1) * inst.raw_multiplier).where(sub.notna().sum(axis=1) >= d.min_valid)
        raw = raw.where(~excluded)
        out[f"{key}_raw"] = raw
        out[f"{key}_0_100"] = (raw - lo) * 100 / (hi - lo)
    if include_total:
        raw = (rev.mean(axis=1) * inst.raw_multiplier).where(~excluded)
        out["total_raw"] = raw
        out["total_0_100"] = (raw - lo) * 100 / (hi - lo)
    return out


def reversed_items_frame(items: pd.DataFrame, instrument: str | Instrument | None = None) -> pd.DataFrame:
    """Reversed items of the respondents kept by the minimum-valid-items rule (for psychometrics)."""
    inst = get_instrument(instrument)
    rev = reverse_items(items[list(inst.items)], inst)
    return rev.loc[rev.notna().sum(axis=1) >= inst.min_valid_total]


def score_columns(inst: Instrument, include_total: bool = False) -> list[str]:
    return [f"{k}_0_100" for k in inst.domains] + (["total_0_100"] if include_total else [])


def model_columns(inst: Instrument) -> list[str]:
    return [f"{k}_0_100" for k in inst.model_domains]


def score_key(col: str) -> str:
    return col.replace("_0_100", "").replace("_raw", "")
