"""Full pipeline: spreadsheet -> scoring -> data quality -> psychometrics -> inference."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from . import figures, quality, scoring, stats
from . import psychometrics as psy
from .i18n import report_language
from .instruments import Instrument, get_instrument
from .io import build_item_frame, detect_mapping, detect_version_language, load_table, parse_mapping
from .metadata import apply_to_raw, find_embedded, load_metadata
from .security import column_ref


@dataclass
class AnalysisConfig:
    path: str
    instrument: str = "whoqol-bref"
    sheet: str | int | None = None
    mapping: dict[str, str] | None = None
    id_column: str | None = None
    group_vars: list[str] = field(default_factory=list)
    continuous_vars: list[str] = field(default_factory=list)
    covariates: list[str] = field(default_factory=list)
    reference: dict | None = None
    method: str = "auto"                 # auto | parametric | nonparametric
    cutoff: float | None = None
    include_total: bool = False
    run_cfa: bool = True
    lang: str = "auto"                   # auto | pt | en | es (report language)
    instrument_version: str = "auto"     # auto | pt | en | es | other (language version administered)
    output_dir: str | None = None
    metadata: str | None = None


@dataclass
class AnalysisResult:
    config: AnalysisConfig
    inst: Instrument
    lang: str
    version_lang: str | None
    raw: pd.DataFrame
    items: pd.DataFrame
    scores: pd.DataFrame
    data: pd.DataFrame
    quality: dict
    descriptives: pd.DataFrame
    descriptives_raw: pd.DataFrame
    item_desc: pd.DataFrame
    floor_ceiling: pd.DataFrame
    reliability: pd.DataFrame
    item_analysis: pd.DataFrame
    multitrait: pd.DataFrame
    multitrait_summary: dict
    htmt: pd.DataFrame
    cfa: dict | None
    corr_rho: pd.DataFrame
    corr_p: pd.DataFrame
    convergent: pd.DataFrame
    group_results: list[dict]
    continuous: pd.DataFrame | None
    regression: dict | None
    reference: pd.DataFrame | None
    cutoff_table: pd.DataFrame | None
    figures: list[str] = field(default_factory=list)
    flags: list[dict] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


def resolve_mapping(df: pd.DataFrame, mapping, inst: Instrument) -> dict[str, str]:
    m = parse_mapping(mapping, inst)
    if m is not None:
        return m
    det = detect_mapping(df, inst)
    if det["missing_items"]:
        raise ValueError(f"Could not detect the columns of items {det['missing_items']}. "
                         "Run inspect and pass an explicit 'mapping'.")
    return det["mapping"]


def run(cfg: AnalysisConfig) -> AnalysisResult:
    inst = get_instrument(cfg.instrument)
    raw = load_table(cfg.path, cfg.sheet)
    meta = load_metadata(cfg.metadata, inst) if cfg.metadata else find_embedded(cfg.path, inst)
    if meta:
        raw = apply_to_raw(raw, meta)
        if cfg.mapping is None and meta["mapping"]:
            m = detect_mapping(raw, inst)["mapping"] if len(meta["mapping"]) < len(inst.items) else {}
            m.update(meta["mapping"])
            cfg.mapping = m
        cfg.id_column = cfg.id_column or meta["id_column"]
        cfg.group_vars = cfg.group_vars or meta["group_vars"]
        cfg.continuous_vars = cfg.continuous_vars or meta["continuous_vars"]
        cfg.covariates = cfg.covariates or meta["covariates"]
    meta = meta or {}
    labels = meta.get("labels", {})
    # '#n' (column position printed by `inspect`) stands for a column whose header is long or unsafe to echo.
    cols = list(raw.columns)
    cfg.id_column = column_ref(cols, cfg.id_column) if cfg.id_column else cfg.id_column
    cfg.group_vars = [column_ref(cols, c) for c in cfg.group_vars]
    cfg.continuous_vars = [column_ref(cols, c) for c in cfg.continuous_vars]
    cfg.covariates = [column_ref(cols, c) for c in cfg.covariates]
    mapping = {it: column_ref(cols, c) for it, c in resolve_mapping(raw, cfg.mapping, inst).items()}

    detected = detect_version_language(raw, mapping, inst)
    version_lang = cfg.instrument_version if cfg.instrument_version != "auto" else detected["language"]
    lang = report_language(cfg.lang, version_lang)

    items, recode_report = build_item_frame(raw, mapping, inst)
    scores = scoring.score(items, inst, include_total=cfg.include_total)
    q = quality.data_quality(raw, items, mapping, recode_report, inst, cfg.id_column)
    q["warnings"].extend(meta.get("warnings", []))

    keep = ~scores["excluded"]
    data = pd.concat([raw.loc[keep], scores.loc[keep]], axis=1)
    sc_cols = scoring.score_columns(inst, cfg.include_total)
    dom_cols = scoring.model_columns(inst)

    desc = stats.describe(data, sc_cols)
    desc_raw = stats.describe(data, [c.replace("_0_100", "_raw") for c in sc_cols])
    item_desc = stats.item_descriptives(items.loc[keep], inst)
    fc = quality.floor_ceiling(data, sc_cols)

    rev = scoring.reversed_items_frame(items, inst)
    rel, ia = psy.reliability_table(rev, data, inst)
    mt, mts = psy.multitrait_scaling(rev, inst)
    ht = psy.htmt(rev, inst)
    cfa_res = psy.cfa(rev, inst) if cfg.run_cfa else None

    corr_cols = [f"{k}_0_100" for k in inst.domains]
    rho, pmat = stats.correlation_matrix(data, corr_cols)
    # convergent validity: domains x global items (when the instrument has a global facet)
    global_items = [it for d in inst.domains.values() if not d.in_measurement_model for it in d.items]
    conv = pd.DataFrame()
    if global_items:
        conv = stats.correlate(pd.concat([data, items.loc[keep][global_items].add_suffix("_item")], axis=1),
                               [f"{g}_item" for g in global_items], dom_cols)

    groups = []
    for gv in cfg.group_vars:
        if gv not in data.columns:
            groups.append({"group_var": gv, "label": labels.get(gv, gv), "error": "column not found"})
            continue
        gr = stats.compare_groups(data, gv, sc_cols, cfg.method, level_order=meta.get("level_order", {}).get(gv))
        gr["label"] = labels.get(gv, gv)
        groups.append(gr)

    cont = None
    if cfg.continuous_vars:
        present = [c for c in cfg.continuous_vars if c in data.columns]
        if missing := [c for c in cfg.continuous_vars if c not in data.columns]:
            q["warnings"].append(f"Continuous variables not found: {missing}")
        cont = stats.correlate(data, present, sc_cols) if present else None

    reg = None
    if covs := [c for c in cfg.covariates if c in data.columns]:
        reg = stats.adjusted_regression(data, dom_cols, covs)

    ref = stats.compare_reference(data, cfg.reference) if cfg.reference else None

    cut = None
    if cfg.cutoff is not None:
        rows = []
        for c in sc_cols:
            s = data[c].dropna()
            if len(s):
                k = int((s >= cfg.cutoff).sum())
                rows.append({"score": c, "n": len(s), "n_ge_cutoff": k, "pct_ge_cutoff": 100 * k / len(s)})
        cut = pd.DataFrame(rows)

    default_out = Path(cfg.path).expanduser().with_suffix("").as_posix() + "_whoqol"
    out = Path(cfg.output_dir or default_out)

    res = AnalysisResult(cfg, inst, lang, version_lang, raw, items, scores, data, q, desc, desc_raw, item_desc,
                         fc, rel, ia, mt, mts, ht, cfa_res, rho, pmat, conv, groups, cont, reg, ref, cut)
    res.extra.update(output_dir=str(out), labels=labels, study=meta.get("study", {}),
                     metadata_source=cfg.metadata or ("embedded sheet" if meta else None),
                     version_detection=detected)

    fig_dir = out / "figures"
    corr_labels = [inst.domain_label(k, lang) for k in inst.domains]
    res.figures = [figures.domain_distribution(data, inst, fig_dir, lang),
                   figures.item_responses(items.loc[keep], inst, fig_dir, lang),
                   figures.correlation_heatmap(rho, corr_labels, fig_dir, lang)]
    for i, gr in enumerate(g for g in groups if "error" not in g):
        res.figures.append(figures.group_means(data, gr["group_var"], gr["levels"], inst, fig_dir, lang,
                                               idx=4 + i, label=gr.get("label")))
    res.flags = interpretive_flags(res)
    return res


def interpretive_flags(r: AnalysisResult) -> list[dict]:
    """Automatic alerts based on published criteria, as {code, **params}; rendered by i18n.render_flag."""
    f: list[dict] = []
    q, inst = r.quality, r.inst
    if q["n_excluded"]:
        f.append({"code": "excluded", "n": q["n_excluded"], "m": inst.min_valid_total})
    if q["items_with_gt5pct_missing"]:
        f.append({"code": "items_missing", "items": q["items_with_gt5pct_missing"]})
    if q["unrecognized_values"]:
        f.append({"code": "unrecognized"})
    if q["straightlining_rows"]:
        f.append({"code": "straightlining", "n": len(q["straightlining_rows"])})
    if q["duplicate_response_patterns"]:
        f.append({"code": "duplicates", "n": q["duplicate_response_patterns"]})
    if q["n_analyzed"] < 30:
        f.append({"code": "small_n", "n": q["n_analyzed"]})
    if r.version_lang is None and r.config.instrument_version == "auto":
        f.append({"code": "version_unknown"})
    for _, row in r.reliability.iterrows():
        a = row["alpha"]
        if np.isnan(a) or row["domain"] == "total":
            continue
        if a < 0.70:
            code = "alpha_low_few_items" if row["n_items"] <= 3 else "alpha_low"
            f.append({"code": code, "domain": row["domain"], "a": a, "k": int(row["n_items"])})
        elif a > 0.95:
            f.append({"code": "alpha_high", "domain": row["domain"], "a": a})
    for _, row in r.floor_ceiling.iterrows():
        if row["floor_effect"]:
            f.append({"code": "floor", "score": row["score"]})
        if row["ceiling_effect"]:
            f.append({"code": "ceiling", "score": row["score"]})
    ms = r.multitrait_summary
    if ms.get("items_r_own_lt_0_40"):
        f.append({"code": "item_r_low", "items": ms["items_r_own_lt_0_40"]})
    if ms.get("items_failing_scaling"):
        f.append({"code": "scaling_fail", "items": ms["items_failing_scaling"]})
    k = len(r.htmt)
    hv = r.htmt.where(~np.eye(k, dtype=bool)).stack()
    if len(hi := hv[hv > 0.85]):
        f.append({"code": "htmt", "pairs": sorted({tuple(sorted(p)) for p in hi.index})})
    if r.cfa and "fit" in r.cfa:
        fit = r.cfa["fit"]
        f.append({"code": "cfa_fit", "cfi": fit["CFI"], "tli": fit["TLI"], "rmsea": fit["RMSEA"], "srmr": fit["SRMR"]})
    if r.cfa and r.cfa.get("warning") == "small_n":
        f.append({"code": "cfa_small_n", "n": r.cfa["n"]})
    for gr in r.group_results:
        name = gr.get("label", gr["group_var"])
        if "error" in gr:
            f.append({"code": "group_error", "name": name, "error": gr["error"]})
            continue
        for _, row in gr["table"][gr["table"]["primary_p_holm"] < 0.05].iterrows():
            f.append({"code": "group_sig", "score": row["score"], "name": name, "test": row["primary_test"],
                      "p": row["primary_p_holm"], "es": row["primary_effect_type"], "v": row["primary_effect"],
                      "mag": row["primary_magnitude"]})
        if gr["dropped_small_groups"]:
            f.append({"code": "group_dropped", "name": name, "groups": gr["dropped_small_groups"]})
    return f


def summary_dict(r: AnalysisResult, files: dict | None = None) -> dict:
    """Compact JSON summary (English keys and codes) for the LLM to interpret."""
    from .i18n import render_flag

    def rec(df, cols=None, nd=3):
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return []
        d = df[[c for c in cols if c in df.columns]] if cols else df
        return d.round(nd).replace({np.nan: None}).to_dict(orient="records")

    groups = []
    for gr in r.group_results:
        if "error" in gr:
            groups.append({k: gr.get(k) for k in ("group_var", "label", "error")})
            continue
        t = gr["table"]
        cols = ["score"] + [c for c in t.columns if c.endswith(("__n", "__mean", "__sd", "__median"))] + \
               ["primary_test", "primary_statistic", "primary_df", "primary_p", "primary_p_holm",
                "primary_effect_type", "primary_effect", "primary_effect_ci_low", "primary_effect_ci_high",
                "primary_magnitude", "secondary_test", "secondary_p"]
        groups.append({"group_var": gr["group_var"], "label": gr.get("label"), "group_sizes": gr["group_sizes"],
                       "parametric": gr["parametric"], "method_reason": gr["method_reason"],
                       "results": rec(t, cols), "posthoc": gr["posthoc"]})
    out = {
        "instrument": {"key": r.inst.key, "name": r.inst.name},
        "report_language": r.lang,
        "version_language": r.version_lang,
        "version_detection": r.extra.get("version_detection"),
        "n": {k: r.quality[k] for k in ("n_rows", "n_complete", "n_excluded", "n_analyzed")},
        "data_quality": {k: v for k, v in r.quality.items() if k not in ("pct_missing_by_item", "mapping_used")},
        "descriptives_0_100": rec(r.descriptives, ["score", "n", "mean", "sd", "ci95_low", "ci95_high", "median",
                                                   "q1", "q3", "skewness", "shapiro_p"], 2),
        "descriptives_raw_4_20": rec(r.descriptives_raw, ["score", "mean", "sd"], 2),
        "floor_ceiling": rec(r.floor_ceiling),
        "reliability": rec(r.reliability),
        "multitrait_summary": r.multitrait_summary,
        "htmt": r.htmt.round(3).to_dict(),
        "cfa": ({k: v for k, v in r.cfa.items() if k not in ("loadings", "model")} if r.cfa else None),
        "spearman_between_scores": r.corr_rho.round(3).to_dict(),
        "convergent_with_global_items": rec(r.convergent),
        "group_comparisons": groups,
        "continuous_correlations": rec(r.continuous),
        "regression": r.regression,
        "reference_comparison": rec(r.reference),
        "cutoff": ({"value": r.config.cutoff, "table": rec(r.cutoff_table)} if r.cutoff_table is not None else None),
        "flags": [{"code": fl["code"], "message": render_flag(fl, "en", r.inst)} for fl in r.flags],
        "study_context": r.extra.get("study", {}),
        "variable_labels": r.extra.get("labels", {}),
        "metadata_source": r.extra.get("metadata_source"),
        "files": files or {},
    }
    return jsonable(out)


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else round(float(o), 4)
    if isinstance(o, pd.DataFrame):
        return jsonable(o.to_dict(orient="records"))
    return o
