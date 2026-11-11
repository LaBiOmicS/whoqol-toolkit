"""Psychometric properties: reliability, construct validity, confirmatory factor analysis."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from scipy import optimize, stats

from .instruments import Instrument


# ----------------------------------------------------------- reliability
def cronbach_alpha(df: pd.DataFrame) -> float:
    d = df.dropna()
    k = d.shape[1]
    if k < 2 or len(d) < 3:
        return float("nan")
    item_var = d.var(axis=0, ddof=1).sum()
    total_var = d.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return float("nan")
    return float(k / (k - 1) * (1 - item_var / total_var))


def alpha_ci_feldt(alpha: float, n: int, k: int, level: float = 0.95) -> tuple[float, float]:
    if np.isnan(alpha) or n < 3:
        return (float("nan"), float("nan"))
    df1, df2 = n - 1, (n - 1) * (k - 1)
    g = 1 - level
    lo = 1 - (1 - alpha) * stats.f.ppf(1 - g / 2, df1, df2)
    hi = 1 - (1 - alpha) * stats.f.ppf(g / 2, df1, df2)
    return float(lo), float(hi)


def one_factor_loadings(df: pd.DataFrame) -> np.ndarray:
    """One-factor loadings (minres) on the Pearson correlation matrix."""
    r = df.dropna().corr().values
    k = r.shape[0]
    iu = np.triu_indices(k, 1)
    w, v = np.linalg.eigh(r)
    start = v[:, -1] * np.sqrt(max(w[-1], 1e-6))
    start = np.clip(np.abs(start) * np.sign(start.sum() or 1), -0.95, 0.95)

    def resid(lam):
        return (r - np.outer(lam, lam))[iu]

    res = optimize.least_squares(resid, start, bounds=(-0.999, 0.999))
    lam = res.x
    if lam.sum() < 0:
        lam = -lam
    return lam


def mcdonald_omega(df: pd.DataFrame) -> float:
    d = df.dropna()
    if d.shape[1] < 3 or len(d) < 10:
        return float("nan")
    lam = one_factor_loadings(d)
    s = lam.sum() ** 2
    return float(s / (s + (1 - lam ** 2).sum()))


def item_analysis(df: pd.DataFrame) -> pd.DataFrame:
    d = df.dropna()
    rows = []
    total = d.sum(axis=1)
    for c in d.columns:
        rest = total - d[c]
        r_it = d[c].corr(rest) if d[c].std() > 0 else np.nan
        rows.append({"item": c, "corrected_item_total_r": r_it,
                     "alpha_if_deleted": cronbach_alpha(d.drop(columns=c)) if d.shape[1] > 2 else np.nan})
    return pd.DataFrame(rows)


def reliability_table(rev_items: pd.DataFrame, domain_scores: pd.DataFrame,
                      inst: Instrument) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-domain table + item analysis."""
    rows, item_rows = [], []
    for key in inst.model_domains:
        d = inst.domains[key]
        sub = rev_items[list(d.items)].dropna()
        k, n = sub.shape[1], len(sub)
        a = cronbach_alpha(sub)
        lo, hi = alpha_ci_feldt(a, n, k)
        corr = sub.corr().values
        mean_r = corr[np.triu_indices(k, 1)].mean() if n > 2 else np.nan
        om = mcdonald_omega(sub)
        sd = domain_scores[f"{key}_0_100"].std(ddof=1)
        sem = sd * np.sqrt(1 - a) if not np.isnan(a) and a < 1 else np.nan
        rows.append({"domain": key, "n_items": k, "n_complete": n, "alpha": a,
                     "alpha_ci_low": lo, "alpha_ci_high": hi, "omega": om,
                     "mean_inter_item_r": mean_r, "sd_0_100": sd,
                     "sem_0_100": sem, "mdc95_0_100": 1.96 * np.sqrt(2) * sem if not np.isnan(sem) else np.nan,
                     "half_sd_0_100": sd / 2})
        ia = item_analysis(sub)
        ia.insert(0, "domain", key)
        item_rows.append(ia)
    # whole scale (all items of the measurement model)
    all_items = _model_items(inst)
    sub = rev_items[all_items].dropna()
    a = cronbach_alpha(sub)
    lo, hi = alpha_ci_feldt(a, len(sub), sub.shape[1])
    rows.append({"domain": "total", "n_items": len(all_items), "n_complete": len(sub), "alpha": a,
                 "alpha_ci_low": lo, "alpha_ci_high": hi, "omega": mcdonald_omega(sub),
                 "mean_inter_item_r": sub.corr().values[np.triu_indices(len(all_items), 1)].mean() if len(sub) > 2 else np.nan,
                 "sd_0_100": np.nan, "sem_0_100": np.nan, "mdc95_0_100": np.nan, "half_sd_0_100": np.nan})
    return pd.DataFrame(rows), pd.concat(item_rows, ignore_index=True)


# ----------------------------------------------- validity (multitrait scaling)
def multitrait_scaling(rev_items: pd.DataFrame, inst: Instrument) -> tuple[pd.DataFrame, dict]:
    """Correlation of each item with its own domain (corrected: item removed) and with the other
    domains. Scaling success when r(own) > r(others). Adequate convergence: corrected r >= .40
    (Ware & Gandek, 1998)."""
    order = inst.model_domains
    doms = inst.domains
    d = rev_items.dropna(subset=_model_items(inst))
    dom_means = {k: d[list(doms[k].items)].mean(axis=1) for k in order}
    rows = []
    for k in order:
        for it in doms[k].items:
            own_items = [x for x in doms[k].items if x != it]
            own = d[own_items].mean(axis=1)
            row = {"item": it, "domain": k, "r_own_corrected": d[it].corr(own)}
            others = {}
            for k2 in order:
                if k2 != k:
                    others[k2] = d[it].corr(dom_means[k2])
                    row[f"r_{k2}"] = others[k2]
            row["max_r_other"] = max(others.values())
            row["scaling_success"] = row["r_own_corrected"] > row["max_r_other"]
            rows.append(row)
    t = pd.DataFrame(rows)
    summary = {
        "n_complete": len(d),
        "scaling_success_rate_pct": float(t["scaling_success"].mean() * 100) if len(t) else float("nan"),
        "items_r_own_lt_0_40": t.loc[t["r_own_corrected"] < 0.40, "item"].tolist(),
        "items_failing_scaling": t.loc[~t["scaling_success"], "item"].tolist(),
    }
    return t, summary


def htmt(rev_items: pd.DataFrame, inst: Instrument) -> pd.DataFrame:
    """Heterotrait-monotrait ratio (Henseler et al., 2015). HTMT < .85 (or < .90) supports
    discriminant validity."""
    order, doms = inst.model_domains, inst.domains
    d = rev_items[_model_items(inst)].dropna()
    r = d.corr().abs()
    out = pd.DataFrame(index=order, columns=order, dtype=float)

    def mono(k):
        it = list(doms[k].items)
        m = r.loc[it, it].values
        return m[np.triu_indices(len(it), 1)].mean()

    for a in order:
        for b in order:
            if a == b:
                out.loc[a, b] = 1.0
                continue
            hetero = r.loc[list(doms[a].items), list(doms[b].items)].values.mean()
            out.loc[a, b] = hetero / np.sqrt(mono(a) * mono(b))
    return out


# ------------------------------------------------------------------ AFC
def _model_items(inst: Instrument) -> list[str]:
    return [it for k in inst.model_domains for it in inst.domains[k].items]


def factor_name(key: str) -> str:
    return "F_" + "".join(ch for ch in key.upper() if ch.isalnum())


def cfa_model(inst: Instrument) -> str:
    return "\n".join(f"{factor_name(k)} =~ " + " + ".join(inst.domains[k].items) for k in inst.model_domains)


def cfa(rev_items: pd.DataFrame, inst: Instrument) -> dict:
    """CFA of the correlated-domains model, ML estimator (semopy).

    ML treats Likert items as continuous; for publication also run WLSMV with polychoric
    correlations (lavaan) - the R script is generated with the report.
    """
    try:
        import contextlib
        import sys
        with contextlib.redirect_stdout(sys.stderr):  # semopy prints on import (would corrupt the JSON on stdout)
            import semopy
    except ImportError:
        return {"error": "semopy not installed"}
    model = cfa_model(inst)
    items = _model_items(inst)
    d = rev_items[items].dropna()
    n = len(d)
    res: dict = {"n": n, "estimator": "ML (semopy)", "model": model, "n_factors": len(inst.model_domains),
                 "n_items": len(items)}
    if n < 100:
        res["warning"] = "small_n"
    if n < 30:
        res["error"] = "Sample too small for CFA (n < 30)."
        return res
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = semopy.Model(model)
            m.fit(d)
            st = semopy.calc_stats(m).T.iloc[:, 0]
            est = m.inspect(std_est=True)
    except Exception as e:  # pragma: no cover
        res["error"] = f"CFA fit failed: {e}"
        return res

    def g(name):
        v = st.get(name, np.nan)
        return float(v) if v is not None else float("nan")

    srmr = _srmr(m, d)
    res["fit"] = {"chi2": g("chi2"), "df": g("DoF"), "p": g("chi2 p-value"),
                  "chi2_df": g("chi2") / g("DoF") if g("DoF") else np.nan,
                  "CFI": min(g("CFI"), 1.0), "TLI": g("TLI"), "RMSEA": g("RMSEA"), "SRMR": srmr,
                  "AIC": g("AIC"), "BIC": g("BIC")}
    res["rmsea_ci90"] = _rmsea_ci(g("chi2"), g("DoF"), n)
    load = est[est["op"] == "~"].copy()
    fnames = {factor_name(k): k for k in inst.model_domains}
    load = load[load["rval"].isin(fnames)]
    lt = load[["rval", "lval", "Est. Std", "p-value"]].rename(
        columns={"rval": "factor", "lval": "item", "Est. Std": "std_loading", "p-value": "p"})
    lt["std_loading"] = lt["std_loading"].astype(float)
    lt["factor"] = lt["factor"].map(fnames)
    res["loadings"] = lt.to_dict(orient="records")
    # average variance extracted and composite reliability
    fac = {}
    for f, grp in lt.groupby("factor"):
        lam = grp["std_loading"].values
        cr = lam.sum() ** 2 / (lam.sum() ** 2 + (1 - lam ** 2).sum())
        fac[f] = {"AVE": float((lam ** 2).mean()), "CR": float(cr),
                  "low_loadings_lt_0_40": grp.loc[grp["std_loading"] < 0.40, "item"].tolist()}
    res["factors"] = fac
    fc = est[(est["op"] == "~~") & (est["lval"] != est["rval"])
             & est["lval"].isin(fnames) & est["rval"].isin(fnames)]
    res["factor_correlations"] = [{"f1": fnames[r.lval], "f2": fnames[r.rval], "r": float(r["Est. Std"])}
                                  for _, r in fc.iterrows()]
    f = res["fit"]
    res["fit_assessment"] = {
        "CFI>=0.90": f["CFI"] >= 0.90, "CFI>=0.95": f["CFI"] >= 0.95,
        "TLI>=0.90": f["TLI"] >= 0.90, "RMSEA<=0.08": f["RMSEA"] <= 0.08,
        "RMSEA<=0.06": f["RMSEA"] <= 0.06, "SRMR<=0.08": (srmr <= 0.08) if not np.isnan(srmr) else None,
    }
    return res


def _srmr(model, d: pd.DataFrame) -> float:
    try:
        sigma, _ = model.calc_sigma()
        obs = model.vars["observed"]
        s = d[obs].cov().values
        sd = np.sqrt(np.diag(s))
        r_obs = s / np.outer(sd, sd)
        sds = np.sqrt(np.diag(sigma))
        r_imp = sigma / np.outer(sds, sds)
        iu = np.tril_indices(len(obs))
        return float(np.sqrt(((r_obs - r_imp)[iu] ** 2).mean()))
    except Exception:
        return float("nan")


def _rmsea_ci(chi2: float, df: float, n: int, level: float = 0.90) -> tuple[float, float]:
    """90% CI of the RMSEA from the noncentral chi-square distribution."""
    if not (df and n > 1 and np.isfinite(chi2)):
        return (float("nan"), float("nan"))

    def find(p):
        def f(lam):
            return stats.ncx2.cdf(chi2, df, lam) - p if lam > 0 else stats.chi2.cdf(chi2, df) - p
        if f(0) < 0:
            return 0.0
        hi = max(chi2 * 3, 10)
        while f(hi) > 0:
            hi *= 2
        return optimize.brentq(f, 1e-9, hi)

    lam_lo = find(1 - (1 - level) / 2)
    lam_hi = find((1 - level) / 2)
    def conv(lam):
        return float(np.sqrt(max(lam, 0) / (df * (n - 1))))
    return conv(lam_lo), conv(lam_hi)


LAVAAN_SCRIPT = """# CFA of the {name} with the WLSMV estimator (ordinal items) - generated by whoqol-toolkit
# install.packages(c("lavaan", "semTools"))
library(lavaan)
data <- read.csv("items_reversed.csv")   # items already reverse-coded ({reversed})

model <- '
{model}
'
items <- c({items})
fit <- cfa(model, data = data, ordered = items, estimator = "WLSMV", std.lv = TRUE)
summary(fit, fit.measures = TRUE, standardized = TRUE)
fitMeasures(fit, c("chisq.scaled", "df.scaled", "pvalue.scaled", "cfi.scaled", "tli.scaled",
                   "rmsea.scaled", "rmsea.ci.lower.scaled", "rmsea.ci.upper.scaled", "srmr"))
semTools::compRelSEM(fit)            # ordinal omega per domain
modindices(fit, sort. = TRUE, maximum.number = 10)

# Measurement invariance across groups (e.g. sex): see semTools::measEq.syntax (Wu & Estabrook, 2016)
# configural <- cfa(model, data, ordered = items, estimator = "WLSMV", group = "sex")
"""


def lavaan_script(inst: Instrument) -> str:
    items = _model_items(inst)
    return LAVAAN_SCRIPT.format(name=inst.name, model=cfa_model(inst), reversed=", ".join(inst.reversed_items),
                                items=", ".join(f'"{i}"' for i in items))
