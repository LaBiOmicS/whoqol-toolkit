"""WHOQOL scoring (WHO manual rules), generic over instruments."""

from __future__ import annotations

import pandas as pd

from .instruments import Instrument, get_instrument


def _flip(items: pd.DataFrame, inst: Instrument, which) -> pd.DataFrame:
    out = items.copy()
    for it in which:
        out[it] = inst.item_max(it) + 1 - out[it]
    return out


def reverse_items(items: pd.DataFrame, inst: Instrument) -> pd.DataFrame:
    """Reverse-codes the instrument's negatively worded items (value = scale maximum + 1 - answer)."""
    return _flip(items, inst, inst.reversed_items)


def score(items: pd.DataFrame, instrument: str | Instrument | None = None, include_total: bool = False) -> pd.DataFrame:
    """Items already recoded to their 1-k scale (NOT reversed). Returns per respondent:
    n_valid_items, excluded (fewer than the minimum valid items), and <score>_raw / <score>_0_100 for every
    domain, facet, overall score and official total; optionally total_* (mean of all items x 4; NOT an official
    score, only for single-scale instruments without an official total)."""
    inst = get_instrument(instrument)
    rev = reverse_items(items[list(inst.items)], inst)
    n_valid = rev.notna().sum(axis=1)
    excluded = n_valid < inst.min_valid_total
    out = pd.DataFrame(index=items.index)
    out["n_valid_items"] = n_valid
    out["excluded"] = excluded
    for key, d in inst.domains.items():
        lo, hi = inst.domain_range(key)
        if d.composite:
            parts = []
            for f in d.facets:
                s = out[f"{f}_raw"]
                flo, fhi = inst.domain_range(f)
                parts.append(flo + fhi - s if f in d.reversed_facets else s)
            sub = pd.concat(parts, axis=1)
            raw = sub.mean(axis=1).where(sub.notna().sum(axis=1) >= d.min_valid)
        else:
            sub = rev[list(d.items)]
            raw = (sub.mean(axis=1) * d.multiplier).where(sub.notna().sum(axis=1) >= d.min_valid)
        raw = raw.where(~excluded)
        out[f"{key}_raw"] = raw
        out[f"{key}_0_100"] = (raw - lo) * 100 / (hi - lo)
    if include_total and total_allowed(inst):
        lo, hi = 4, 4 * inst.scale_max
        raw = (_flip(items[list(inst.items)], inst, inst.psychometric_reversed).mean(axis=1) * 4).where(~excluded)
        out["total_raw"] = raw
        out["total_0_100"] = (raw - lo) * 100 / (hi - lo)
    return out


def total_allowed(inst: Instrument) -> bool:
    """The unofficial item-mean total only makes sense on one response scale and without an official total."""
    return not inst.item_scale and not any(d.role == "total" for d in inst.domains.values())


def reversed_items_frame(items: pd.DataFrame, instrument: str | Instrument | None = None) -> pd.DataFrame:
    """Items oriented so that higher = better QoL (items of facets reversed at domain level are flipped too),
    for the respondents kept by the minimum-valid-items rule (psychometrics, lavaan export)."""
    inst = get_instrument(instrument)
    rev = _flip(items[list(inst.items)], inst, inst.psychometric_reversed)
    return rev.loc[rev.notna().sum(axis=1) >= inst.min_valid_total]


def score_columns(inst: Instrument, include_total: bool = False) -> list[str]:
    return [f"{k}_0_100" for k in inst.reported_domains] + (
        ["total_0_100"] if include_total and total_allowed(inst) else [])


def model_columns(inst: Instrument) -> list[str]:
    return [f"{k}_0_100" for k in inst.primary_domains]


def score_key(col: str) -> str:
    return col.replace("_0_100", "").replace("_raw", "")
