"""Outputs: full XLSX, APA-style DOCX tables, Markdown report, methods/results draft (PT, EN, ES),
lavaan script and JSON summary. File names are in English; their content is in the report language."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import psychometrics as psy
from . import scoring, sensitivity
from .analysis import AnalysisResult, summary_dict
from .i18n import ES_SYMBOL, LANGS, fmt, fmt_p, fmt_r, join_list, lower_label, p_expr, render_flag, score_label, t

METHOD_REFERENCES = [
    "Bonett DG, Wright TA. Sample size requirements for estimating Pearson, Kendall and Spearman correlations. "
    "Psychometrika. 2000;65(1):23-28.",
    "Cohen J. Statistical power analysis for the behavioral sciences. 2nd ed. Hillsdale: Lawrence Erlbaum; 1988.",
    "Feldt LS. The approximate sampling distribution of Kuder-Richardson reliability coefficient twenty. "
    "Psychometrika. 1965;30(3):357-370.",
    "Henseler J, Ringle CM, Sarstedt M. A new criterion for assessing discriminant validity in variance-based "
    "structural equation modeling. J Acad Mark Sci. 2015;43(1):115-135.",
    "Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat. 1979;6(2):65-70.",
    "Hu LT, Bentler PM. Cutoff criteria for fit indexes in covariance structure analysis: conventional criteria "
    "versus new alternatives. Struct Equ Modeling. 1999;6(1):1-55.",
    "McDonald RP. Test theory: a unified treatment. Mahwah: Lawrence Erlbaum; 1999.",
    "Norman GR, Sloan JA, Wyrwich KW. Interpretation of changes in health-related quality of life: the remarkable "
    "universality of half a standard deviation. Med Care. 2003;41(5):582-592.",
    "Terwee CB, Bot SDM, de Boer MR, van der Windt DAWM, Knol DL, Dekker J, et al. Quality criteria were proposed "
    "for measurement properties of health status questionnaires. J Clin Epidemiol. 2007;60(1):34-42.",
    "Ware JE Jr, Gandek B. Methods for testing data quality, scaling assumptions, and reliability: the IQOLA "
    "Project approach. J Clin Epidemiol. 1998;51(11):945-952.",
]


def references(r: AnalysisResult) -> list[str]:
    refs = set(METHOD_REFERENCES) | set(r.inst.references) | {r.inst.primary_reference}
    v = r.inst.version_for(r.version_lang)
    if v:
        refs.add(v.reference)
    return sorted(refs)


# ------------------------------------------------------------------ tables
def _range_note(inst, key: str) -> str:
    if key in inst.domains:
        lo, hi = inst.domain_range(key)
    else:  # unofficial total
        lo, hi = 4, 4 * inst.scale_max
    return f" [{lo:g}–{hi:g}]"


def table_descriptives(r: AnalysisResult) -> pd.DataFrame:
    lang, inst = r.lang, r.inst
    rel = r.reliability.set_index("domain")
    fc = r.floor_ceiling.set_index("score")
    draw = r.descriptives_raw.set_index("score")
    single = inst.single_range
    lo, hi = inst.raw_range()
    rows = []
    for _, d in r.descriptives.iterrows():
        key = d["score"].replace("_0_100", "")
        a = rel["alpha"].get(key, np.nan) if key in rel.index else np.nan
        om = rel["omega"].get(key, np.nan) if key in rel.index else np.nan
        dr = draw.loc[d["score"].replace("_0_100", "_raw")]
        rows.append({
            t("score", lang): score_label(d["score"], lang, inst),
            "n": int(d["n"]),
            t("mean_sd", lang): f"{fmt(d['mean'], 1, lang)} ({fmt(d['sd'], 1, lang)})",
            t("ci95", lang): f"{fmt(d['ci95_low'], 1, lang)}–{fmt(d['ci95_high'], 1, lang)}",
            t("median_iqr", lang): f"{fmt(d['median'], 1, lang)} [{fmt(d['q1'], 1, lang)}–{fmt(d['q3'], 1, lang)}]",
            t("raw_mean_sd", lang, range=f"{lo:g}–{hi:g}" if single
                   else {"pt": "bruta", "en": "raw", "es": "bruta"}[lang]):
                f"{fmt(dr['mean'], 2, lang)} ({fmt(dr['sd'], 2, lang)})" + ("" if single else _range_note(inst, key)),
            t("floor", lang): fmt(fc.loc[d["score"], "floor_pct"], 1, lang),
            t("ceiling", lang): fmt(fc.loc[d["score"], "ceiling_pct"], 1, lang),
            "α": fmt_r(a, lang), "ω": fmt_r(om, lang),
        })
    return pd.DataFrame(rows)


def table_reliability(r: AnalysisResult) -> pd.DataFrame:
    lang = r.lang
    rows = []
    for _, d in r.reliability.iterrows():
        name = (t("total_items", lang, n=int(d["n_items"])) if d["domain"] == "total"
                else r.inst.domain_label(d["domain"], lang))
        rows.append({
            t("domain", lang): name, t("items", lang): int(d["n_items"]), "n": int(d["n_complete"]),
            t("alpha_ci", lang): f"{fmt_r(d['alpha'], lang)} ({fmt_r(d['alpha_ci_low'], lang)}–"
                                 f"{fmt_r(d['alpha_ci_high'], lang)})",
            "ω": fmt_r(d["omega"], lang), t("mean_interitem", lang): fmt_r(d["mean_inter_item_r"], lang),
            t("sem", lang): fmt(d["sem_0_100"], 1, lang), t("mdc95", lang): fmt(d["mdc95_0_100"], 1, lang),
            t("half_sd", lang): fmt(d["half_sd_0_100"], 1, lang),
        })
    return pd.DataFrame(rows)


def table_correlations(r: AnalysisResult) -> pd.DataFrame:
    lang = r.lang
    cols = list(r.corr_rho.columns)
    labels = [score_label(c, lang, r.inst) for c in cols]
    out = pd.DataFrame("", index=[f"{i + 1}. {lab}" for i, lab in enumerate(labels)],
                       columns=[str(i + 1) for i in range(len(cols))])
    for i in range(len(cols)):
        for j in range(i + 1):
            if i == j:
                out.iloc[i, j] = "—"
                continue
            p = r.corr_p.iloc[i, j]
            star = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
            out.iloc[i, j] = fmt_r(r.corr_rho.iloc[i, j], lang) + star
    out.index.name = t("score", lang)
    return out.reset_index()


def table_group(gr: dict, r: AnalysisResult) -> pd.DataFrame:
    lang, par = r.lang, gr["parametric"]
    rows = []
    for _, row in gr["table"].iterrows():
        d = {t("score", lang): score_label(row["score"], lang, r.inst)}
        for lv in gr["levels"]:
            if pd.isna(row.get(f"{lv}__n", np.nan)):
                continue
            hdr = f"{lv} (n = {gr['group_sizes'].get(str(lv), int(row[f'{lv}__n']))})"
            d[hdr] = (f"{fmt(row[f'{lv}__mean'], 1, lang)} ({fmt(row[f'{lv}__sd'], 1, lang)})" if par else
                      f"{fmt(row[f'{lv}__median'], 1, lang)} [{fmt(row[f'{lv}__q1'], 1, lang)}–"
                      f"{fmt(row[f'{lv}__q3'], 1, lang)}]")
        d[t("statistic", lang)] = fmt(row["primary_statistic"], 2, lang)
        d["p"] = fmt_p(row["primary_p"], lang)
        d["p (Holm)"] = fmt_p(row["primary_p_holm"], lang)
        ci = ""
        if pd.notna(row.get("primary_effect_ci_low")):
            ci = f" [{fmt(row['primary_effect_ci_low'], 2, lang)}; {fmt(row['primary_effect_ci_high'], 2, lang)}]"
        sym = ES_SYMBOL.get(row["primary_effect_type"], row["primary_effect_type"])
        d[t("effect_size", lang)] = f"{sym} = {fmt(row['primary_effect'], 2, lang)}{ci}"
        rows.append(d)
    return pd.DataFrame(rows)


def table_cfa(r: AnalysisResult) -> pd.DataFrame | None:
    if not r.cfa or "fit" not in r.cfa:
        return None
    lang, f = r.lang, r.cfa["fit"]
    lo, hi = r.cfa.get("rmsea_ci90", (np.nan, np.nan))
    return pd.DataFrame([{
        "n": r.cfa["n"], "χ²": fmt(f["chi2"], 2, lang), t("df", lang): fmt(f["df"], 0, lang), "p": fmt_p(f["p"], lang),
        f"χ²/{t('df', lang)}": fmt(f["chi2_df"], 2, lang), "CFI": fmt_r(f["CFI"], lang, 3), "TLI": fmt_r(f["TLI"], lang, 3),
        f"RMSEA ({t('ci90', lang)})": f"{fmt_r(f['RMSEA'], lang, 3)} ({fmt_r(lo, lang, 3)}–{fmt_r(hi, lang, 3)})",
        "SRMR": fmt_r(f["SRMR"], lang, 3),
    }])


def _howto_rel(r: AnalysisResult) -> str:
    rows = r.reliability[(r.reliability["domain"] != "total") & r.reliability["mdc95_0_100"].notna()]
    if rows.empty:
        return ""
    x = rows.iloc[0]
    return t("howto_rel", r.lang, dom=lower_label(r.inst.domain_label(x["domain"], r.lang), r.lang), mdc=fmt(x["mdc95_0_100"], 1, r.lang),
             hs=fmt(x["half_sd_0_100"], 1, r.lang))


def build_tables(r: AnalysisResult) -> list[tuple[str, pd.DataFrame, str, str]]:
    """(title, table, APA note, plain-language reading aid). The reading aid goes only into report.md."""
    lang, inst = r.lang, r.inst
    desc = table_descriptives(r)
    raw_col = str(desc.columns[5])  # "Média 4–20 (DP)": score, n, mean (SD), CI, median, raw mean
    tabs = [(t("t_desc", lang, n=1, inst=inst.name), desc, t("n_desc", lang), t("howto_desc", lang, raw=raw_col)),
            (t("t_rel", lang, n=2), table_reliability(r), t("n_rel", lang), _howto_rel(r)),
            (t("t_corr", lang, n=3), table_correlations(r), t("n_corr", lang), t("howto_corr", lang))]
    n = 4
    if (cfa_t := table_cfa(r)) is not None:
        key = "t_cfa_facet" if r.cfa.get("level") == "facet" else "t_cfa"
        tabs.append((t(key, lang, n=n, k=r.cfa["n_factors"], i=r.cfa["n_items"]), cfa_t, t("n_cfa", lang),
                     t("howto_cfa", lang)))
        n += 1
    for gr in r.group_results:
        if "error" in gr or gr["table"].empty:
            continue
        desc = t("mean_sd", lang) if gr["parametric"] else t("median_iqr", lang)
        test = t(f"test_{gr['table']['primary_test'].iloc[0]}", lang)
        tabs.append((t("t_group", lang, n=n, inst=inst.name, name=gr.get("label", gr["group_var"])),
                     table_group(gr, r),
                     t("n_group", lang, desc=desc, test=test, reason=t(f"reason_{gr['method_reason']}", lang)),
                     t("howto_group", lang)))
        n += 1
    return tabs


def table_sensitivity(r: AnalysisResult) -> pd.DataFrame | None:
    """Scoring-rule sensitivity, one row per alternative rule x score (report language)."""
    lang, inst = r.lang, r.inst
    rows = []
    for res in r.extra.get("sensitivity", []):
        for _, x in res["table"].iterrows():
            # Report only what changes; facets whose values stay the same (only n differs) are left to results.xlsx.
            moved = x["n_values_changed"] > 0
            if not moved and (x["n_alternative"] == x["n_adopted"] or inst.domains[x["score"]].role == "facet"):
                continue
            rows.append({
                t("sens_rule", lang): res["label"][lang],
                t("sens_score", lang): score_label(x["score"], lang, inst),
                t("sens_n", lang): f"{x['n_adopted']} → {x['n_alternative']}",
                t("sens_means", lang): f"{fmt(x['mean_adopted'], 1, lang)} → {fmt(x['mean_alternative'], 1, lang)}",
                "Δ": fmt(x["delta_mean"], 2, lang),
                f"Δ/{t('sd', lang)}": fmt(x["delta_sd"], 2, lang),
                t("sens_maxdiff", lang): fmt(x["max_abs_diff"], 1, lang),
                t("sens_changed", lang): x["n_values_changed"],
            })
    return pd.DataFrame(rows) if rows else None


def sensitivity_markdown(r: AnalysisResult) -> list[str]:
    lang = r.lang
    if not r.extra.get("sensitivity"):  # scored entirely by the official source: nothing to compare
        return []
    parts = [f"## {t('h_sensitivity', lang)}\n"]
    tab = table_sensitivity(r)
    if tab is None:
        return parts + [t("sens_nochange", lang), ""]
    parts.append(t("sens_intro", lang) + "\n")
    for res in r.extra["sensitivity"]:
        parts.append(f"- **{res['label'][lang]}**: {res['rule'][lang]}.")
    return parts + ["", _md_table(tab), f"\n*{t('note', lang)}* {t('sens_note', lang)}\n"]


# ------------------------------------------------------------------ writers
def _md_table(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    lines += ["| " + " | ".join(str(v) for v in row.values) + " |" for _, row in df.iterrows()]
    return "\n".join(lines)


def domain_profile(r: AnalysisResult) -> dict | None:
    """Domain means on 0–100, ties at the reported precision, and whether the highest and lowest means differ by
    less than half a standard deviation (Norman et al., 2003) — then no domain is singled out."""
    d = r.descriptives.set_index("score")
    doms = [k for k in r.inst.primary_domains if f"{k}_0_100" in d.index]
    if not doms:
        return None
    means = {k: float(d.loc[f"{k}_0_100", "mean"]) for k in doms}
    sds = [float(d.loc[f"{k}_0_100", "sd"]) for k in doms]
    hi, lo = max(means.values()), min(means.values())
    shown = {k: fmt(m, 1) for k, m in means.items()}
    return {"doms": doms, "means": means, "hi": hi, "lo": lo, "gap": hi - lo,
            "hi_doms": [k for k in doms if shown[k] == fmt(hi, 1)],
            "lo_doms": [k for k in doms if shown[k] == fmt(lo, 1)],
            "similar": len(doms) < 2 or hi - lo < 0.5 * float(np.nanmean(sds))}


def summary_markdown(r: AnalysisResult) -> list[str]:
    """Plain-language summary for readers without a psychometrics background; every number comes from the analysis."""
    lang, q, inst = r.lang, r.quality, r.inst
    out = []
    s = t("sum_n", lang, n=q["n_analyzed"], rows=q["n_rows"])
    if q["n_excluded"] == 1:
        s += t("sum_n_exc1", lang, m=inst.min_valid_total)
    elif q["n_excluded"] > 1:
        s += t("sum_n_exc", lang, exc=q["n_excluded"], m=inst.min_valid_total)
    out.append(s + ".")
    if (pf := domain_profile(r)) and len(pf["doms"]) > 1:
        labs = lambda ks: join_list([inst.domain_label(k, lang) for k in ks], lang)  # noqa: E731
        s = t("sum_profile", lang, lo=fmt(pf["lo"], 1, lang), lo_lab=labs(pf["lo_doms"]),
              hi=fmt(pf["hi"], 1, lang), hi_lab=labs(pf["hi_doms"]))
        s += t("sum_similar" if pf["similar"] else "sum_apart", lang, d=fmt(pf["gap"], 1, lang))
        out.append(s)
    elif pf:
        k = pf["doms"][0]
        out.append(t("sum_single", lang, lab=inst.domain_label(k, lang), m=fmt(pf["means"][k], 1, lang)))
    if r.reference is None or r.reference.empty:
        out.append(t("sum_norms", lang))
    rel = r.reliability[r.reliability["domain"].isin(inst.model_domains) & r.reliability["alpha"].notna()]
    if not rel.empty:
        low = [inst.domain_label(k, lang) for k in rel.loc[rel["alpha"] < 0.70, "domain"]]
        out.append(t("sum_alpha_ok", lang) if not low else
                   t("sum_alpha_low", lang, doms=join_list(low, lang)) if len(low) <= 3 else
                   t("sum_alpha_many", lang, k=len(low), n=len(rel)))
    fc = list(dict.fromkeys(score_label(f["score"], lang, inst) for f in r.flags if f["code"] in ("floor", "ceiling")))
    out.append(t("sum_fc", lang, scores=join_list(fc, lang)) if fc else t("sum_fc_none", lang))
    for gr in r.group_results:
        if "error" in gr or gr["table"].empty:
            continue
        name = gr.get("label", gr["group_var"])
        sig = [f for f in r.flags if f["code"] == "group_sig" and f["name"] == name]
        if not sig:
            out.append(t("sum_group_none", lang, name=name))
        else:
            out.append(t("sum_group", lang, name=name,
                         scores=join_list([score_label(f["score"], lang, inst) for f in sig], lang),
                         mags=join_list(list(dict.fromkeys(t(f"mag_{f['mag']}", lang) for f in sig)), lang)))
    if r.flags:
        out.append(t("sum_flags1", lang) if len(r.flags) == 1 else t("sum_flags", lang, k=len(r.flags)))
    return [f"## {t('h_summary', lang)}\n", *[f"- {x}" for x in out], ""]


def validity_markdown(r: AnalysisResult) -> list[str]:
    lang, inst, ms = r.lang, r.inst, r.multitrait_summary
    out = []
    if ms and ms.get("n_complete", 0) > 0 and not pd.isna(ms.get("scaling_success_rate_pct", np.nan)):
        low = ms.get("items_r_own_lt_0_40") or []
        out.append(t("val_mt", lang, n=ms["n_complete"], pct=fmt(ms["scaling_success_rate_pct"], 0, lang),
                     low=", ".join(map(str, low)) if low else t("none", lang)))
    if r.htmt is not None and len(r.htmt) > 1:
        hv = r.htmt.where(~np.eye(len(r.htmt), dtype=bool)).stack().dropna()
        if len(hv):
            a, b = hv.idxmax()
            out.append(t("val_htmt", lang, v=fmt_r(hv.max(), lang), a=inst.domain_label(a, lang),
                         b=inst.domain_label(b, lang)))
    return [f"## {t('h_validity', lang)}\n", *[f"- {x}" for x in out], ""] if out else []


def figure_caption(r: AnalysisResult, path: str) -> str:
    lang, inst, stem = r.lang, r.inst, Path(path).stem
    if stem.startswith("fig1_"):
        note = t("fig_dist_note", lang)
        return f"{t('fig_dist_title', lang)} ({note[0].lower()}{note[1:]})"
    if stem.startswith("fig2_"):
        key = stem.removeprefix("fig2_item_responses").lstrip("_")
        cap = t("fig_items_title", lang)
        return f"{cap}: {inst.domain_label(key, lang)}" if key in inst.domains else cap
    if stem.startswith("fig3_"):
        return t("fig_corr_caption", lang)
    for gr in r.group_results:
        safe = "".join(ch if ch.isalnum() else "_" for ch in gr["group_var"])
        if stem.endswith(f"_groups_{safe}"):
            mci = t("fig_mean_ci", lang)
            return f"{t('fig_group_title', lang, name=gr.get('label', gr['group_var']))}: {mci[0].lower()}{mci[1:]}"
    return ""


def markdown_report(r: AnalysisResult, tables) -> str:
    lang, q, inst = r.lang, r.quality, r.inst
    v = inst.version_for(r.version_lang)
    parts = [f"# {t('report_title', lang, inst=inst.name)}\n", f"{t('file', lang)}: `{r.config.path}`\n",
             *summary_markdown(r),
             f"## {t('h_sample', lang)}\n",
             f"- {t('rows', lang)}: {q['n_rows']}",
             f"- {t('complete', lang, k=len(inst.items))}: {q['n_complete']}",
             f"- {t('excluded', lang, m=inst.min_valid_total)}: {q['n_excluded']}",
             f"- {t('analysed', lang)}: {q['n_analyzed']}",
             f"- {t('missing_overall', lang)}: {fmt(q['pct_missing_overall'], 2, lang)}%",
             f"- {t('detected_version', lang)}: {v.code + ' (' + v.citation + ')' if v else '—'}\n"]
    if r.flags:
        parts += [f"## {t('h_flags', lang)}\n", *[f"- {render_flag(fl, lang, inst)}" for fl in r.flags], ""]
    for i, (title, df, note, howto) in enumerate(tables):
        parts += [f"## {title}\n", _md_table(df), f"\n*{t('note', lang)}* {note}\n"]
        if howto:
            parts.append(f"*{t('howto', lang)}* {howto}\n")
        if i == 2:  # after the correlations: multitrait scaling and HTMT (described in the methods text)
            parts += validity_markdown(r)
    for gr in r.group_results:
        if "error" in gr or not gr["posthoc"]:
            continue
        parts.append(f"### {t('h_posthoc', lang, name=gr.get('label', gr['group_var']))}\n")
        for sc, lst in gr["posthoc"].items():
            parts.append(f"**{score_label(sc, lang, inst)}**: " + "; ".join(
                f"{x['g1']} vs {x['g2']}: p {p_expr(x['p_adj'], lang)} ({t('test_' + x['test'], lang)})" for x in lst))
        parts.append("")
    if r.regression:
        parts.append(f"## {t('h_regression', lang)}\n")
        for sc, m in r.regression.items():
            if "error" in m:
                parts.append(f"- {score_label(sc, lang, inst)}: {m['error']}")
                continue
            parts.append(f"**{score_label(sc, lang, inst)}** (n = {m['n']}, {t('r2adj', lang)} = "
                         f"{fmt(m['r2_adj'], 3, lang)})\n")
            parts.append(_md_table(pd.DataFrame([{
                t("term", lang): c["term"], "B": fmt(c["B"], 2, lang),
                t("ci95", lang): f"{fmt(c['ci95_low'], 2, lang)}; {fmt(c['ci95_high'], 2, lang)}",
                "β": fmt(c["beta_std"], 2, lang), "p": fmt_p(c["p"], lang)} for c in m["coefficients"]])))
            parts.append("")
    if r.reference is not None and not r.reference.empty:
        parts += [f"## {t('h_reference', lang)}\n", _md_table(r.reference.round(3)), ""]
    if r.cutoff_table is not None:
        parts += [f"## {t('h_cutoff', lang, c=fmt(r.config.cutoff, 0, lang))}\n", _md_table(r.cutoff_table.round(1)), ""]
    parts += sensitivity_markdown(r)
    parts.append(f"## {t('h_figures', lang)}\n")
    base = Path(r.extra["output_dir"])
    for i, f in enumerate(r.figures, 1):
        cap = figure_caption(r, f)
        parts += [f"**{t('figure', lang)} {i}.** {cap}\n", f"![{cap}]({Path(f).relative_to(base).as_posix()})\n"]
    return "\n".join(parts) + "\n"


def _apa_borders(table):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    def set_border(cell, **edges):
        tc_pr = cell._tc.get_or_add_tcPr()
        b = tc_pr.find(qn("w:tcBorders"))
        if b is None:
            b = OxmlElement("w:tcBorders")
            tc_pr.append(b)
        for edge, val in edges.items():
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), val)
            el.set(qn("w:sz"), "8")
            el.set(qn("w:color"), "000000")
            b.append(el)

    for c in table.rows[0].cells:
        set_border(c, top="single", bottom="single")
    for c in table.rows[-1].cells:
        set_border(c, bottom="single")


def docx_report(r: AnalysisResult, tables, path: str) -> None:
    from docx import Document
    from docx.shared import Inches, Pt

    lang = r.lang
    doc = Document()
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(10)
    doc.add_heading(t("docx_title", lang, inst=r.inst.name), 1)
    for title, df, note, _howto in tables:
        doc.add_paragraph().add_run(title).bold = True
        tb = doc.add_table(rows=1, cols=len(df.columns))
        for i, c in enumerate(df.columns):
            tb.rows[0].cells[i].text = str(c)
            for run in tb.rows[0].cells[i].paragraphs[0].runs:
                run.bold = True
        for _, row in df.iterrows():
            cells = tb.add_row().cells
            for i, v in enumerate(row.values):
                cells[i].text = str(v)
        for row in tb.rows:
            for c in row.cells:
                for par in c.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(8.5)
        _apa_borders(tb)
        p = doc.add_paragraph()
        p.add_run(t("note", lang) + " ").italic = True
        p.add_run(note).font.size = Pt(8.5)
    doc.add_page_break()
    for i, f in enumerate(r.figures, 1):
        par = doc.add_paragraph()
        par.add_run(f"{t('figure', lang)} {i}. ").bold = True
        par.add_run(figure_caption(r, f)).italic = True
        doc.add_picture(f, width=Inches(6.0))
    doc.add_page_break()
    doc.add_heading(t("references", lang), 2)
    for ref in references(r):
        doc.add_paragraph(ref)
    doc.save(path)


def write_all(r: AnalysisResult) -> dict:
    out = Path(r.extra["output_dir"])
    out.mkdir(parents=True, exist_ok=True)
    files: dict = {}

    scored = pd.concat([r.raw, r.items.add_prefix("item_"), r.scores], axis=1)
    files["xlsx"] = str(out / "results.xlsx")
    with pd.ExcelWriter(files["xlsx"], engine="openpyxl") as xw:
        scored.to_excel(xw, sheet_name="scores_by_participant", index=False)
        sheets = {"descriptives_0_100": r.descriptives, "descriptives_raw": r.descriptives_raw,
                  "items": r.item_desc, "floor_ceiling": r.floor_ceiling, "reliability": r.reliability,
                  "item_analysis": r.item_analysis, "multitrait": r.multitrait, "convergent": r.convergent}
        for name, df in sheets.items():
            if df is not None and not df.empty:
                df.round(4).to_excel(xw, sheet_name=name, index=False)
        r.htmt.round(3).to_excel(xw, sheet_name="htmt")
        r.corr_rho.round(3).to_excel(xw, sheet_name="spearman_rho")
        r.corr_p.round(4).to_excel(xw, sheet_name="spearman_p")
        if r.cfa and "fit" in r.cfa:
            pd.DataFrame([r.cfa["fit"]]).round(4).to_excel(xw, sheet_name="cfa_fit", index=False)
            pd.DataFrame(r.cfa["loadings"]).round(3).to_excel(xw, sheet_name="cfa_loadings", index=False)
            pd.DataFrame(r.cfa["factors"]).T.to_excel(xw, sheet_name="cfa_ave_cr")
        for gr in r.group_results:
            if "error" in gr:
                continue
            gr["table"].round(4).to_excel(xw, sheet_name=f"group_{gr['group_var']}"[:31], index=False)
            if ph := [dict(score=k, **x) for k, v in gr["posthoc"].items() for x in v]:
                pd.DataFrame(ph).round(4).to_excel(xw, sheet_name=f"posthoc_{gr['group_var']}"[:31], index=False)
        if r.continuous is not None and not r.continuous.empty:
            r.continuous.round(4).to_excel(xw, sheet_name="continuous", index=False)
        if r.regression:
            regs = [dict(score=k, n=v.get("n"), r2_adj=v.get("r2_adj"), **c)
                    for k, v in r.regression.items() for c in v.get("coefficients", [])]
            pd.DataFrame(regs).round(4).to_excel(xw, sheet_name="regression", index=False)
        if r.reference is not None and not r.reference.empty:
            r.reference.round(4).to_excel(xw, sheet_name="reference", index=False)
        if r.cutoff_table is not None:
            r.cutoff_table.round(2).to_excel(xw, sheet_name="cutoff", index=False)
        if sens := r.extra.get("sensitivity"):
            pd.concat([s["table"].assign(alternative=s["code"], rule=s["rule"]["en"]) for s in sens]
                      ).round(4).to_excel(xw, sheet_name="scoring_sensitivity", index=False)
        q = r.quality
        pd.DataFrame({"item": list(q["pct_missing_by_item"]), "pct_missing": list(q["pct_missing_by_item"].values()),
                      "source_column": [q["mapping_used"].get(i) for i in q["pct_missing_by_item"]]}
                     ).to_excel(xw, sheet_name="missing_by_item", index=False)

    scoring.reversed_items_frame(r.items.loc[~r.scores["excluded"]], r.inst).to_csv(out / "items_reversed.csv",
                                                                                    index=False)
    (out / "cfa_wlsmv_lavaan.R").write_text(psy.lavaan_script(r.inst), encoding="utf-8")
    files["lavaan_script"] = str(out / "cfa_wlsmv_lavaan.R")

    tables = build_tables(r)
    files["markdown"] = str(out / "report.md")
    Path(files["markdown"]).write_text(markdown_report(r, tables), encoding="utf-8")
    files["docx"] = str(out / "tables.docx")
    docx_report(r, tables, files["docx"])
    for lg in LANGS:
        p = out / f"methods_results_{lg}.md"
        p.write_text(methods_text(r, lg) + "\n\n" + results_text(r, lg), encoding="utf-8")
        files[f"methods_{lg}"] = str(p)
    files["figures"] = r.figures
    files["json"] = str(out / "results.json")
    Path(files["json"]).write_text(json.dumps(summary_dict(r, files), ensure_ascii=False, indent=2), encoding="utf-8")
    return files


# ------------------------------------------------------------------ prose
def _simple_scoring(inst) -> bool:
    """WHOQOL-BREF-like: item means x 4 on one five-point scale, no facets or official totals."""
    return (not inst.hierarchical and not inst.item_scale and inst.scale_max == 5
            and all(d.multiplier == 4 and d.role in ("domain", "global") for d in inst.domains.values()))


SCORING_WORDS = {
    "pt": {"mean": "média dos itens × {m}", "sum": "soma dos itens", "meansum": "média dos itens × {m} (soma)",
           "comp": "média dos escores das facetas", "revf": ", com {f} invertida(s) (mínimo + máximo − escore)",
           "facets": "cada faceta: mínimo de {v} de {n} itens", "dom_items": "mínimo de {v} de {n} itens",
           "dom_facets": "mínimo de {v} de {n} facetas", "all": "todos os itens",
           "all_facets": "todas as facetas", "one_facet": "a faceta válida"},
    "en": {"mean": "mean of the items × {m}", "sum": "sum of the items", "meansum": "mean of the items × {m} (sum)",
           "comp": "mean of the facet scores", "revf": ", with {f} reversed (minimum + maximum − score)",
           "facets": "each facet: at least {v} of {n} items", "dom_items": "at least {v} of {n} items",
           "dom_facets": "at least {v} of {n} facets", "all": "all items",
           "all_facets": "all facets", "one_facet": "a valid facet"},
    "es": {"mean": "media de los ítems × {m}", "sum": "suma de los ítems", "meansum": "media de los ítems × {m} (suma)",
           "comp": "media de las puntuaciones de las facetas", "revf": ", con {f} invertida(s) (mínimo + máximo − puntuación)",
           "facets": "cada faceta: al menos {v} de {n} ítems", "dom_items": "al menos {v} de {n} ítems",
           "dom_facets": "al menos {v} de {n} facetas", "all": "todos los ítems",
           "all_facets": "todas las facetas", "one_facet": "la faceta válida"},
}

GENERIC_SCORING = {
    "pt": ("Os escores foram calculados conforme o manual e a sintaxe oficiais do instrumento: os itens {rev} foram "
           "invertidos (valor = máximo da escala + 1 − resposta). {rules}. Todos os escores foram transformados para "
           "a escala 0–100 [(escore − mínimo) × 100/(máximo − mínimo)], na qual valores mais altos indicam melhor "
           "qualidade de vida. Questionários com menos de {minv} itens válidos foram excluídos. Respostas válidas "
           "exigidas por escore: {rule}; quando permitido calcular com itens ausentes, usou-se a média dos itens "
           "respondidos do próprio escore."),
    "en": ("Scores were computed following the instrument's official manual and syntax: items {rev} were "
           "reverse-coded (value = scale maximum + 1 − answer). {rules}. All scores were transformed to a 0–100 "
           "scale [(score − minimum) × 100/(maximum − minimum)], with higher values indicating better quality of "
           "life. Questionnaires with fewer than {minv} valid items were excluded. Valid answers required per score: "
           "{rule}; where missing items were allowed, the mean of the answered items of that score was used."),
    "es": ("Las puntuaciones se calcularon según el manual y la sintaxis oficiales del instrumento: los ítems {rev} se "
           "invirtieron (valor = máximo de la escala + 1 − respuesta). {rules}. Todas las puntuaciones se "
           "transformaron a una escala de 0–100 [(puntuación − mínimo) × 100/(máximo − mínimo)], en la que los valores "
           "más altos indican mejor calidad de vida. Se excluyeron los cuestionarios con menos de {minv} ítems "
           "válidos. Respuestas válidas exigidas por puntuación: {rule}; cuando se permitieron ítems faltantes, se "
           "usó la media de los ítems respondidos de la propia puntuación."),
}


def _score_rules(inst, lang: str) -> str:
    W = SCORING_WORDS[lang]
    parts = []
    facets = [k for k, d in inst.domains.items() if d.role == "facet"]
    if facets:
        d0 = inst.domains[facets[0]]
        lo, hi = inst.domain_range(facets[0])
        parts.append({"pt": "Facetas", "en": "Facets", "es": "Facetas"}[lang] + ": "
                     + W["mean"].format(m=d0.multiplier) + f" ({lo:g}–{hi:g})")
    for k in inst.reported_domains:
        d = inst.domains[k]
        lo, hi = inst.domain_range(k)
        if d.composite:
            rule = W["comp"] + (W["revf"].format(f=", ".join(inst.domain_label(f, lang) for f in d.reversed_facets))
                                if d.reversed_facets else "")
        elif d.multiplier == len(d.items) > 1 and d.min_valid == len(d.items):
            rule = W["sum"]
        elif d.multiplier == len(d.items) > 4:
            rule = W["meansum"].format(m=d.multiplier)
        else:
            rule = W["mean"].format(m=d.multiplier)
        parts.append(f"{inst.domain_label(k, lang)}: {rule} ({lo:g}–{hi:g})")
    return "; ".join(parts)


def _missing_rule(r: AnalysisResult, lang: str) -> str:
    if not _simple_scoring(r.inst):
        W, inst, out = SCORING_WORDS[lang], r.inst, []
        facets = [d for d in inst.domains.values() if d.role == "facet"]
        if facets and len({(d.min_valid, len(d.items)) for d in facets}) == 1:
            out.append(W["facets"].format(v=facets[0].min_valid, n=len(facets[0].items)))
        groups: dict[str, list[str]] = {}
        for d in inst.domains.values():
            if d.role == "facet" and out:
                continue
            n = len(d.facets or d.items)
            if d.min_valid == n:
                rule = W["one_facet"] if d.composite and n == 1 else W["all_facets"] if d.composite else W["all"]
            else:
                rule = W["dom_facets" if d.composite else "dom_items"].format(v=d.min_valid, n=n)
            groups.setdefault(rule, []).append(d.label(lang))
        out += [f"{', '.join(names)} ({rule})" for rule, names in groups.items()]
        return "; ".join(out)
    allowed = {k: len(d.items) - d.min_valid for k, d in r.inst.domains.items() if d.in_measurement_model}
    parts = "; ".join(f"{lower_label(r.inst.domain_label(k, lang), lang)}: {v}" for k, v in allowed.items())
    return {"pt": f"número máximo de itens ausentes por domínio — {parts}",
            "en": f"maximum number of missing items per domain — {parts}",
            "es": f"número máximo de ítems faltantes por dominio — {parts}"}[lang]


PROSE = {
    "pt": {
        "h_methods": "## Métodos — análise estatística (rascunho)",
        "instrument": "A qualidade de vida foi avaliada pelo {name}, na {version}. {desc}.",
        "no_version": "[indique a versão linguística validada utilizada]",
        "scoring": ("Os escores foram calculados conforme o manual da Organização Mundial da Saúde: os itens {rev} "
                    "foram invertidos; o escore de cada domínio correspondeu à média dos itens multiplicada por "
                    "quatro (amplitude {lo}–{hi}) e foi transformado para a escala 0–100 [(escore − {lo}) × 100/{span}], "
                    "na qual valores mais altos indicam melhor qualidade de vida. Questionários com menos de {minv} "
                    "itens válidos foram excluídos, e os domínios foram calculados com imputação pela média dos itens "
                    "respondidos do próprio domínio ({rule})."),
        "descr": ("As variáveis foram descritas por média, desvio-padrão (DP), intervalo de confiança de 95% (IC 95%), "
                  "mediana e intervalo interquartil (IIQ). Efeitos piso e teto foram considerados presentes quando mais "
                  "de 15% dos participantes obtiveram o escore mínimo ou máximo (Terwee et al., 2007). A consistência "
                  "interna foi estimada pelo alfa de Cronbach, com IC 95% pelo método de Feldt (1965), e pelo ômega de "
                  "McDonald (1999); valores ≥ 0,70 foram considerados adequados. O erro-padrão da medida (EPM) e a "
                  "mudança mínima detectável (MMD95) foram derivados do alfa. A validade de constructo foi examinada "
                  "por análise multitraço (correlação item-domínio corrigida ≥ 0,40 e maior que com os demais domínios; "
                  "Ware & Gandek, 1998) e pela razão heterotraço-monotraço (HTMT < 0,85; Henseler et al., 2015)"),
        "cfa": (", e por análise fatorial confirmatória do modelo de domínios correlacionados, estimada por máxima "
                "verossimilhança, com ajuste avaliado por χ²/gl, CFI, TLI, RMSEA (IC 90%) e SRMR (Hu & Bentler, 1999)"),
        "cfa_facet": (", e por análise fatorial confirmatória do modelo de domínios correlacionados com os escores das "
                      "facetas como indicadores (facetas de conteúdo negativo invertidas), estimada por máxima "
                      "verossimilhança, com ajuste avaliado por χ²/gl, CFI, TLI, RMSEA (IC 90%) e SRMR (Hu & Bentler, "
                      "1999)"),
        "corr": ("As associações entre escores foram avaliadas pelo coeficiente de correlação de Spearman (ρ), com IC 95% "
                 "pela transformação de Fisher (Bonett & Wright, 2000)."),
        "par": ("teste t de Welch (dois grupos) ou ANOVA de Welch com post hoc de Games-Howell (três ou mais grupos), "
                "com g de Hedges ou ω² como tamanho de efeito"),
        "npar": ("teste de Mann-Whitney (dois grupos) ou de Kruskal-Wallis com post hoc de Dunn (três ou mais grupos), "
                 "com correlação rank-bisserial ou ε² como tamanho de efeito"),
        "groups": ("A normalidade foi verificada pelo teste de Shapiro-Wilk. As comparações entre grupos utilizaram {tests}. "
                   "A magnitude dos efeitos foi interpretada segundo Cohen (1988), e os valores de p foram corrigidos "
                   "para comparações múltiplas pelo método de Holm (1979)."),
        "or": " ou ",
        "reg": ("Modelos de regressão linear múltipla, um por domínio, estimaram as associações ajustadas com {covs}, "
                "com erros-padrão robustos HC3; a multicolinearidade foi avaliada pelo fator de inflação da variância."),
        "ref": ("Os escores foram comparados a valores de referência publicados por teste t, com d de Cohen como "
                "tamanho de efeito."),
        "software": ("Adotou-se nível de significância de 5%. As análises foram realizadas em Python (pandas, SciPy, "
                     "statsmodels, semopy) com o whoqol-toolkit."),
        "h_results": "## Resultados (rascunho para edição)",
        "sample": ("Dos {rows} questionários, {exc} foram excluídos por terem menos de {minv} itens válidos, resultando "
                   "em {n} participantes analisados."),
        "sample_all": "Todos os {rows} questionários tinham ao menos {minv} itens válidos e foram analisados.",
        "profile": " As médias dos escores na escala 0–100 foram: {doms} (Tabela 1).",
        "similar": (" A diferença entre a maior e a menor média ({d} pontos) foi inferior a meio desvio-padrão (Norman "
                    "et al., 2003), indicando um perfil semelhante entre os domínios."),
        "hi_lo": " A média mais alta foi observada em {hi} e a mais baixa em {lo}.",
        "validity": ("Na análise multitraço, {pct}% dos itens correlacionaram mais com o próprio domínio do que com os "
                     "demais, e a maior razão HTMT foi {v} ({a} e {b})."),
        "overall": " O escore {name} foi {ms}.",
        "alpha": "A consistência interna (α de Cronbach) foi: {alphas} (Tabela 2).",
        "cfa_res": ("A AFC apresentou χ²/gl = {chi}, CFI = {cfi}, TLI = {tli}, RMSEA = {rmsea} (IC 90%: {lo}–{hi}) "
                    "e SRMR = {srmr}."),
        "no_diff": "Não houve diferenças significativas segundo {name} após a correção de Holm.",
        "diff": "Segundo {name}, houve diferenças significativas em: {items}.",
        "closing": "_Revise e complete a interpretação; os números acima vêm diretamente da análise._",
    },
    "en": {
        "h_methods": "## Methods — statistical analysis (draft)",
        "instrument": "Quality of life was assessed with the {name}, using the {version}. {desc}.",
        "no_version": "[state the validated language version used]",
        "scoring": ("Scores were computed following the World Health Organization manual: items {rev} were "
                    "reverse-coded; each domain score was the mean of its items multiplied by four (range {lo}–{hi}) "
                    "and transformed to a 0–100 scale [(score − {lo}) × 100/{span}], with higher values indicating "
                    "better quality of life. Questionnaires with fewer than {minv} valid items were excluded, and domain "
                    "scores were computed with person-mean imputation within the domain ({rule})."),
        "descr": ("Variables were described as mean, standard deviation (SD), 95% confidence interval (95% CI), median "
                  "and interquartile range (IQR). Floor and ceiling effects were considered present when more than 15% "
                  "of participants scored the minimum or maximum (Terwee et al., 2007). Internal consistency was "
                  "estimated with Cronbach's alpha, with 95% CI by Feldt's (1965) method, and McDonald's (1999) omega; "
                  "values ≥ .70 were considered adequate. The standard error of measurement (SEM) and the minimal "
                  "detectable change (MDC95) were derived from alpha. Construct validity was examined through multitrait "
                  "scaling analysis (corrected item-domain correlation ≥ .40 and higher than with the other domains; "
                  "Ware & Gandek, 1998) and the heterotrait-monotrait ratio (HTMT < .85; Henseler et al., 2015)"),
        "cfa": (", and through confirmatory factor analysis of the correlated-domains model, estimated by maximum "
                "likelihood, with fit assessed by χ²/df, CFI, TLI, RMSEA (90% CI) and SRMR (Hu & Bentler, 1999)"),
        "cfa_facet": (", and through confirmatory factor analysis of the correlated-domains model with the facet scores "
                      "as indicators (negatively framed facets reversed), estimated by maximum likelihood, with fit "
                      "assessed by χ²/df, CFI, TLI, RMSEA (90% CI) and SRMR (Hu & Bentler, 1999)"),
        "corr": ("Associations between scores were assessed with Spearman's correlation coefficient (ρ), with 95% CI "
                 "via Fisher's transformation (Bonett & Wright, 2000)."),
        "par": ("Welch's t-test (two groups) or Welch's ANOVA with Games-Howell post hoc tests (three or more groups), "
                "with Hedges' g or ω² as effect sizes"),
        "npar": ("the Mann-Whitney test (two groups) or the Kruskal-Wallis test with Dunn's post hoc tests (three or more "
                 "groups), with the rank-biserial correlation or ε² as effect sizes"),
        "groups": ("Normality was checked with the Shapiro-Wilk test. Group comparisons used {tests}. Effect magnitudes "
                   "were interpreted following Cohen (1988), and p values were adjusted for multiple comparisons with "
                   "Holm's (1979) method."),
        "or": " or ",
        "reg": ("Multiple linear regression models, one per domain, estimated adjusted associations with {covs}, using "
                "HC3 robust standard errors; multicollinearity was assessed with variance inflation factors."),
        "ref": "Scores were compared with published reference values using t-tests, with Cohen's d as the effect size.",
        "software": ("The significance level was set at 5%. Analyses were performed in Python (pandas, SciPy, "
                     "statsmodels, semopy) with whoqol-toolkit."),
        "h_results": "## Results (draft for editing)",
        "sample": ("Of the {rows} questionnaires, {exc} were excluded for having fewer than {minv} valid items, leaving "
                   "{n} participants for analysis."),
        "sample_all": "All {rows} questionnaires had at least {minv} valid items and were analysed.",
        "profile": " Mean scores on the 0–100 scale were: {doms} (Table 1).",
        "similar": (" The difference between the highest and lowest means ({d} points) was below half a standard "
                    "deviation (Norman et al., 2003), indicating a similar profile across domains."),
        "hi_lo": " The highest mean was observed in {hi} and the lowest in {lo}.",
        "validity": ("In the multitrait scaling analysis, {pct}% of the items correlated more with their own domain than "
                     "with the others, and the highest HTMT ratio was {v} ({a} and {b})."),
        "overall": " The {name} score was {ms}.",
        "alpha": "Internal consistency (Cronbach's α) was: {alphas} (Table 2).",
        "cfa_res": "CFA yielded χ²/df = {chi}, CFI = {cfi}, TLI = {tli}, RMSEA = {rmsea} (90% CI: {lo}–{hi}) and SRMR = {srmr}.",
        "no_diff": "There were no significant differences by {name} after Holm correction.",
        "diff": "By {name}, significant differences were found in: {items}.",
        "closing": "_Review and complete the interpretation; the figures above come directly from the analysis._",
    },
    "es": {
        "h_methods": "## Métodos — análisis estadístico (borrador)",
        "instrument": "La calidad de vida se evaluó con el {name}, en su {version}. {desc}.",
        "no_version": "[indique la versión lingüística validada utilizada]",
        "scoring": ("Las puntuaciones se calcularon según el manual de la Organización Mundial de la Salud: los ítems "
                    "{rev} se invirtieron; la puntuación de cada dominio correspondió a la media de sus ítems "
                    "multiplicada por cuatro (rango {lo}–{hi}) y se transformó a una escala de 0–100 "
                    "[(puntuación − {lo}) × 100/{span}], en la que los valores más altos indican mejor calidad de vida. "
                    "Se excluyeron los cuestionarios con menos de {minv} ítems válidos, y los dominios se calcularon con "
                    "imputación por la media de los ítems respondidos del propio dominio ({rule})."),
        "descr": ("Las variables se describieron mediante media, desviación estándar (DE), intervalo de confianza del "
                  "95% (IC 95%), mediana y rango intercuartílico (RIC). Se consideraron efectos suelo y techo cuando más "
                  "del 15% de los participantes obtuvo la puntuación mínima o máxima (Terwee et al., 2007). La "
                  "consistencia interna se estimó con el alfa de Cronbach, con IC 95% por el método de Feldt (1965), y "
                  "con el omega de McDonald (1999); se consideraron adecuados valores ≥ 0,70. El error estándar de "
                  "medida (EEM) y el cambio mínimo detectable (CMD95) se derivaron del alfa. La validez de constructo se "
                  "examinó mediante análisis multirrasgo (correlación ítem-dominio corregida ≥ 0,40 y mayor que con los "
                  "demás dominios; Ware & Gandek, 1998) y la razón heterorrasgo-monorrasgo (HTMT < 0,85; Henseler et "
                  "al., 2015)"),
        "cfa": (", y mediante análisis factorial confirmatorio del modelo de dominios correlacionados, estimado por "
                "máxima verosimilitud, con el ajuste evaluado por χ²/gl, CFI, TLI, RMSEA (IC 90%) y SRMR (Hu & "
                "Bentler, 1999)"),
        "cfa_facet": (", y mediante análisis factorial confirmatorio del modelo de dominios correlacionados con las "
                      "puntuaciones de las facetas como indicadores (facetas de contenido negativo invertidas), estimado "
                      "por máxima verosimilitud, con el ajuste evaluado por χ²/gl, CFI, TLI, RMSEA (IC 90%) y SRMR (Hu "
                      "& Bentler, 1999)"),
        "corr": ("Las asociaciones entre puntuaciones se evaluaron con el coeficiente de correlación de Spearman (ρ), con "
                 "IC 95% mediante la transformación de Fisher (Bonett & Wright, 2000)."),
        "par": ("la prueba t de Welch (dos grupos) o el ANOVA de Welch con pruebas post hoc de Games-Howell (tres o más "
                "grupos), con g de Hedges u ω² como tamaño del efecto"),
        "npar": ("la prueba de Mann-Whitney (dos grupos) o la de Kruskal-Wallis con pruebas post hoc de Dunn (tres o más "
                 "grupos), con la correlación biserial de rangos o ε² como tamaño del efecto"),
        "groups": ("La normalidad se verificó con la prueba de Shapiro-Wilk. Las comparaciones entre grupos utilizaron "
                   "{tests}. La magnitud de los efectos se interpretó según Cohen (1988), y los valores p se ajustaron "
                   "por comparaciones múltiples con el método de Holm (1979)."),
        "or": " o ",
        "reg": ("Modelos de regresión lineal múltiple, uno por dominio, estimaron las asociaciones ajustadas con {covs}, "
                "con errores estándar robustos HC3; la multicolinealidad se evaluó con el factor de inflación de la "
                "varianza."),
        "ref": ("Las puntuaciones se compararon con valores de referencia publicados mediante pruebas t, con d de Cohen "
                "como tamaño del efecto."),
        "software": ("Se adoptó un nivel de significación del 5%. Los análisis se realizaron en Python (pandas, SciPy, "
                     "statsmodels, semopy) con whoqol-toolkit."),
        "h_results": "## Resultados (borrador para editar)",
        "sample": ("De los {rows} cuestionarios, {exc} se excluyeron por tener menos de {minv} ítems válidos, quedando {n} "
                   "participantes para el análisis."),
        "sample_all": "Los {rows} cuestionarios tenían al menos {minv} ítems válidos y se analizaron todos.",
        "profile": " Las medias de las puntuaciones en la escala 0–100 fueron: {doms} (Tabla 1).",
        "similar": (" La diferencia entre la media más alta y la más baja ({d} puntos) fue inferior a media desviación "
                    "estándar (Norman et al., 2003), lo que indica un perfil similar entre los dominios."),
        "hi_lo": " La media más alta se observó en {hi} y la más baja en {lo}.",
        "validity": ("En el análisis multirrasgo, el {pct}% de los ítems correlacionó más con su propio dominio que con "
                     "los demás, y la mayor razón HTMT fue {v} ({a} y {b})."),
        "overall": " La puntuación de {name} fue {ms}.",
        "alpha": "La consistencia interna (α de Cronbach) fue: {alphas} (Tabla 2).",
        "cfa_res": ("El AFC mostró χ²/gl = {chi}, CFI = {cfi}, TLI = {tli}, RMSEA = {rmsea} (IC 90%: {lo}–{hi}) y "
                    "SRMR = {srmr}."),
        "no_diff": "No hubo diferencias significativas según {name} tras la corrección de Holm.",
        "diff": "Según {name}, hubo diferencias significativas en: {items}.",
        "closing": "_Revise y complete la interpretación; las cifras anteriores provienen directamente del análisis._",
    },
}


SENS_PROSE = {
    "pt": {
        "methods": ("Como análise de sensibilidade, os escores foram recalculados com as regras alternativas "
                    "documentadas nas fontes ({alts}), comparando as médias e o número de participantes pontuados."),
        "results": ("Na análise de sensibilidade das regras de pontuação, a maior diferença entre médias foi de {d} "
                    "pontos, em {score}, com a regra “{alt}”; o número de participantes com escore variou no máximo "
                    "{dn}, em {score_n}, com a regra “{alt_n}”."),
    },
    "en": {
        "methods": ("As a sensitivity analysis, scores were recomputed with the alternative rules documented in the "
                    "sources ({alts}), comparing means and the number of participants scored."),
        "results": ("In the sensitivity analysis of the scoring rules, the largest difference between means was {d} "
                    "points, in {score}, with the rule “{alt}”; the number of participants with a score changed by at "
                    "most {dn}, in {score_n}, with the rule “{alt_n}”."),
    },
    "es": {
        "methods": ("Como análisis de sensibilidad, las puntuaciones se recalcularon con las reglas alternativas "
                    "documentadas en las fuentes ({alts}), comparando las medias y el número de participantes "
                    "puntuados."),
        "results": ("En el análisis de sensibilidad de las reglas de puntuación, la mayor diferencia entre medias fue "
                    "de {d} puntos, en {score}, con la regla “{alt}”; el número de participantes con puntuación varió "
                    "como máximo {dn}, en {score_n}, con la regla “{alt_n}”."),
    },
}


def methods_text(r: AnalysisResult, lang: str) -> str:
    P, inst, cfg = PROSE[lang], r.inst, r.config
    v = inst.version_for(r.version_lang)
    lo, hi = inst.raw_range()
    if _simple_scoring(inst):
        rev = join_list([i.lstrip("Q") for i in inst.reversed_items], lang)
        scoring_text = P["scoring"].format(rev=rev, lo=lo, hi=hi, span=hi - lo, minv=inst.min_valid_total,
                                           rule=_missing_rule(r, lang))
    else:
        scoring_text = GENERIC_SCORING[lang].format(rev=join_list(list(inst.reversed_items), lang),
                                                    rules=_score_rules(inst, lang), minv=inst.min_valid_total,
                                                    rule=_missing_rule(r, lang))
    s = [P["h_methods"],
         P["instrument"].format(name=inst.name, desc=inst.description[lang],
                                version=v.description[lang] if v else P["no_version"]),
         scoring_text + (" " + inst.methods_note[lang] if lang in inst.methods_note else ""),
         P["descr"] + ((P["cfa_facet"] if r.cfa.get("level") == "facet" else P["cfa"]) if r.cfa and "fit" in r.cfa
                       else "") + ".",
         P["corr"]]
    ok = [g for g in r.group_results if "error" not in g]
    if ok:
        tests = [P["par"]] * any(g["parametric"] for g in ok) + [P["npar"]] * any(not g["parametric"] for g in ok)
        s.append(P["groups"].format(tests=P["or"].join(tests)))
    if r.regression:
        s.append(P["reg"].format(covs=", ".join(r.extra["labels"].get(c, c) for c in cfg.covariates)))
    if r.reference is not None and not r.reference.empty:
        s.append(P["ref"])
    if sens := r.extra.get("sensitivity"):
        s.append(SENS_PROSE[lang]["methods"].format(alts=join_list([f"“{x['label'][lang]}”" for x in sens], lang)))
    s.append(P["software"])
    return "\n\n".join(s)


def results_text(r: AnalysisResult, lang: str) -> str:
    P, inst, q = PROSE[lang], r.inst, r.quality
    d = r.descriptives.set_index("score")
    rel = r.reliability.set_index("domain")
    doms = [k for k in inst.primary_domains if f"{k}_0_100" in d.index]
    alpha_doms = [k for k in inst.model_domains if k in rel.index]

    def lab(k):
        return lower_label(inst.domain_label(k, lang), lang)

    def ms(k):
        row = d.loc[f"{k}_0_100"]
        return f"{fmt(row['mean'], 1, lang)} ({t('sd', lang)} = {fmt(row['sd'], 1, lang)})"

    pf = domain_profile(r)
    profile = ""
    if pf:
        profile = P["profile"].format(doms="; ".join(f"{lab(k)}, {ms(k)}" for k in doms))
        if len(doms) > 1:
            profile += (P["similar"].format(d=fmt(pf["gap"], 1, lang)) if pf["similar"] else
                        P["hi_lo"].format(hi=join_list([lab(k) for k in pf["hi_doms"]], lang),
                                          lo=join_list([lab(k) for k in pf["lo_doms"]], lang)))
    s = [P["h_results"],
         P["sample" if q["n_excluded"] else "sample_all"].format(rows=q["n_rows"], exc=q["n_excluded"],
                                                                  minv=inst.min_valid_total, n=q["n_analyzed"])
         + profile
         + "".join(P["overall"].format(name=lab(k), ms=ms(k)) for k, dm in inst.domains.items()
                   if dm.role in ("global", "total") and f"{k}_0_100" in d.index),
         P["alpha"].format(alphas=", ".join(f"{lab(k)} = {fmt_r(rel.loc[k, 'alpha'], lang)}" for k in alpha_doms))]
    mts = r.multitrait_summary or {}
    hv = pd.Series(dtype=float)
    if r.htmt is not None and len(r.htmt) > 1:
        hv = r.htmt.where(~np.eye(len(r.htmt), dtype=bool)).stack().dropna()
    if mts.get("n_complete", 0) > 0 and not pd.isna(mts.get("scaling_success_rate_pct", np.nan)) and len(hv):
        a, b = hv.idxmax()
        s.append(P["validity"].format(pct=fmt(mts["scaling_success_rate_pct"], 0, lang), v=fmt_r(hv.max(), lang),
                                      a=lab(a), b=lab(b)))
    if r.cfa and "fit" in r.cfa:
        f = r.cfa["fit"]
        lo90, hi90 = r.cfa["rmsea_ci90"]
        s.append(P["cfa_res"].format(chi=fmt(f["chi2_df"], 2, lang), cfi=fmt_r(f["CFI"], lang, 3),
                                     tli=fmt_r(f["TLI"], lang, 3), rmsea=fmt_r(f["RMSEA"], lang, 3),
                                     lo=fmt_r(lo90, lang, 3), hi=fmt_r(hi90, lang, 3), srmr=fmt_r(f["SRMR"], lang, 3)))
    for gr in r.group_results:
        if "error" in gr or gr["table"].empty:
            continue
        name = gr.get("label", gr["group_var"])
        sig = gr["table"][gr["table"]["primary_p_holm"] < 0.05]
        if sig.empty:
            s.append(P["no_diff"].format(name=name))
        else:
            items = [f"{score_label(row['score'], lang, inst)} (p {p_expr(row['primary_p_holm'], lang)}; "
                     f"{ES_SYMBOL.get(row['primary_effect_type'])} = {fmt(row['primary_effect'], 2, lang)})"
                     for _, row in sig.iterrows()]
            s.append(P["diff"].format(name=name, items="; ".join(items)))
    if mc := sensitivity.max_change(r.extra.get("sensitivity", [])):
        s.append(SENS_PROSE[lang]["results"].format(
            d=fmt(mc["d"], 1, lang), score=score_label(mc["d_score"], lang, inst),
            alt=sensitivity.label_of(mc["d_alt"], lang), dn=mc["dn"], score_n=score_label(mc["dn_score"], lang, inst),
            alt_n=sensitivity.label_of(mc["dn_alt"], lang)))
    s.append(P["closing"])
    return "\n\n".join(s)
