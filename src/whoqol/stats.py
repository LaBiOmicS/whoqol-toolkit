"""Descriptive and inferential statistics of WHOQOL scores.

Results carry English codes (test names, effect magnitudes, method reasons); reports localize them."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

from .instruments import Instrument


# ------------------------------------------------------------ descriptives
def describe(scores: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        s = scores[c].dropna()
        n = len(s)
        if n == 0:
            continue
        m, sd = s.mean(), s.std(ddof=1)
        se = sd / np.sqrt(n) if n > 1 else np.nan
        tcrit = stats.t.ppf(0.975, n - 1) if n > 1 else np.nan
        sw = stats.shapiro(s) if 3 <= n <= 5000 and s.nunique() > 2 else None
        rows.append({
            "score": c, "n": n, "mean": m, "sd": sd,
            "ci95_low": m - tcrit * se, "ci95_high": m + tcrit * se,
            "median": s.median(), "q1": s.quantile(.25), "q3": s.quantile(.75),
            "min": s.min(), "max": s.max(),
            "skewness": stats.skew(s, bias=False) if n > 2 else np.nan,
            "kurtosis": stats.kurtosis(s, bias=False) if n > 3 else np.nan,
            "shapiro_W": sw.statistic if sw else np.nan,
            "shapiro_p": sw.pvalue if sw else np.nan,
        })
    return pd.DataFrame(rows)


def item_descriptives(items: pd.DataFrame, inst: Instrument) -> pd.DataFrame:
    """Original answers (not reversed), 1-5."""
    rows = []
    for it in inst.items:
        s = items[it]
        v = s.dropna()
        row = {"item": it, "n": len(v), "missing_pct": s.isna().mean() * 100,
               "mean": v.mean(), "sd": v.std(ddof=1), "median": v.median()}
        for k in range(1, 6):
            row[f"pct_{k}"] = (v == k).mean() * 100 if len(v) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------- effect sizes
def magnitude(es_type: str, v: float) -> str:
    a = abs(v)
    if np.isnan(a):
        return ""
    cuts = {  # Cohen (1988)
        "hedges_g": (0.2, 0.5, 0.8), "cohen_d": (0.2, 0.5, 0.8),
        "rank_biserial_r": (0.1, 0.3, 0.5), "spearman_rho": (0.1, 0.3, 0.5),
        "eta2": (0.01, 0.06, 0.14), "omega2": (0.01, 0.06, 0.14), "epsilon2": (0.01, 0.06, 0.14),
    }[es_type]
    labels = ["trivial", "small", "medium", "large"]
    return labels[sum(a >= c for c in cuts)]


def hedges_g(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    n1, n2 = len(x), len(y)
    sp = np.sqrt(((n1 - 1) * x.var(ddof=1) + (n2 - 1) * y.var(ddof=1)) / (n1 + n2 - 2))
    if sp == 0:
        return (np.nan,) * 3
    d = (x.mean() - y.mean()) / sp
    j = 1 - 3 / (4 * (n1 + n2) - 9)
    g = j * d
    se = np.sqrt((n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2)))
    return g, g - 1.96 * se, g + 1.96 * se


def welch_anova(groups: list[np.ndarray]) -> tuple[float, float, float, float]:
    k = len(groups)
    n = np.array([len(g) for g in groups], float)
    m = np.array([g.mean() for g in groups])
    v = np.array([g.var(ddof=1) for g in groups])
    if np.any(v == 0):
        v = np.where(v == 0, 1e-12, v)
    w = n / v
    mw = (w * m).sum() / w.sum()
    a = (w * (m - mw) ** 2).sum() / (k - 1)
    tmp = (((1 - w / w.sum()) ** 2) / (n - 1)).sum()
    b = 1 + 2 * (k - 2) / (k ** 2 - 1) * tmp
    f = a / b
    df1, df2 = k - 1, (k ** 2 - 1) / (3 * tmp)
    return f, df1, df2, stats.f.sf(f, df1, df2)


def eta_omega_sq(groups: list[np.ndarray]) -> tuple[float, float]:
    allv = np.concatenate(groups)
    gm = allv.mean()
    ssb = sum(len(g) * (g.mean() - gm) ** 2 for g in groups)
    sst = ((allv - gm) ** 2).sum()
    k, n = len(groups), len(allv)
    msw = (sst - ssb) / (n - k)
    eta2 = ssb / sst if sst > 0 else np.nan
    om2 = (ssb - (k - 1) * msw) / (sst + msw) if sst > 0 else np.nan
    return eta2, max(om2, 0.0) if not np.isnan(om2) else om2


def games_howell(groups: dict[str, np.ndarray]) -> list[dict]:
    keys = list(groups)
    k = len(keys)
    out = []
    for a, b in combinations(keys, 2):
        x, y = groups[a], groups[b]
        va, vb = x.var(ddof=1) / len(x), y.var(ddof=1) / len(y)
        se = np.sqrt(va + vb)
        diff = x.mean() - y.mean()
        df = (va + vb) ** 2 / (va ** 2 / (len(x) - 1) + vb ** 2 / (len(y) - 1))
        q = abs(diff) / se * np.sqrt(2)
        p = stats.studentized_range.sf(q, k, df)
        g = hedges_g(x, y)[0]
        out.append({"g1": a, "g2": b, "diff": diff, "p_adj": float(p), "test": "games_howell",
                    "effect": g, "effect_type": "hedges_g"})
    return out


def dunn(groups: dict[str, np.ndarray]) -> list[dict]:
    keys = list(groups)
    allv = np.concatenate([groups[k] for k in keys])
    ranks = stats.rankdata(allv)
    n = len(allv)
    _, counts = np.unique(allv, return_counts=True)
    ties = (counts ** 3 - counts).sum()
    idx, mr, ns = 0, {}, {}
    for k in keys:
        m = len(groups[k])
        mr[k] = ranks[idx:idx + m].mean()
        ns[k] = m
        idx += m
    res = []
    for a, b in combinations(keys, 2):
        se = np.sqrt((n * (n + 1) / 12 - ties / (12 * (n - 1))) * (1 / ns[a] + 1 / ns[b]))
        z = (mr[a] - mr[b]) / se
        p = 2 * stats.norm.sf(abs(z))
        u = stats.mannwhitneyu(groups[a], groups[b]).statistic
        rrb = 2 * u / (ns[a] * ns[b]) - 1
        res.append({"g1": a, "g2": b, "z": z, "p_raw": p, "test": "dunn",
                    "effect": rrb, "effect_type": "rank_biserial_r"})
    padj = holm([r["p_raw"] for r in res])
    for r, p in zip(res, padj, strict=True):
        r["p_adj"] = p
    return res


def holm(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, float)
    out = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    pv = p[ok]
    m = len(pv)
    if m == 0:
        return out.tolist()
    order = np.argsort(pv)
    adj = np.empty(m)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, (m - i) * pv[j])
        adj[j] = min(run, 1.0)
    out[ok] = adj
    return out.tolist()


# ------------------------------------------------------ group comparisons
def _choose_parametric(groups: dict[str, np.ndarray], method: str) -> tuple[bool, str]:
    if method == "parametric":
        return True, "user"
    if method == "nonparametric":
        return False, "user"
    if all(len(g) >= 30 for g in groups.values()):
        return True, "clt"
    rej = [stats.shapiro(g).pvalue < 0.05 for g in groups.values() if len(g) >= 3 and np.ptp(g) > 0]
    if any(rej):
        return False, "shapiro_reject"
    return True, "shapiro_ok"


def compare_groups(data: pd.DataFrame, group_var: str, score_cols: list[str],
                   method: str = "auto", min_group_n: int = 3, level_order: list[str] | None = None) -> dict:
    g = data[group_var]
    levels = [lv for lv in g.dropna().unique()]
    try:
        levels = sorted(levels)
    except TypeError:
        pass
    if level_order:
        pos = {str(v): i for i, v in enumerate(level_order)}
        levels = sorted(levels, key=lambda lv: pos.get(str(lv), len(pos)))
    sizes = {lv: int((g == lv).sum()) for lv in levels}
    dropped = [str(lv) for lv, n in sizes.items() if n < min_group_n]
    levels = [lv for lv in levels if sizes[lv] >= min_group_n]
    if len(levels) < 2:
        return {"group_var": group_var, "error": f"fewer than 2 groups with n >= {min_group_n}",
                "group_sizes": {str(k): v for k, v in sizes.items()}}

    # one method decision per variable (consistency across domains)
    par_flags = []
    for c in score_cols:
        gr = {str(lv): data.loc[g == lv, c].dropna().values for lv in levels}
        par_flags.append(_choose_parametric(gr, method))
    parametric = all(f[0] for f in par_flags)
    reason = par_flags[0][1] if parametric else next(f[1] for f in par_flags if not f[0])

    rows, posthoc = [], {}
    for c in score_cols:
        gr = {str(lv): data.loc[g == lv, c].dropna().values for lv in levels}
        gr = {k: v for k, v in gr.items() if len(v) >= 2}
        if len(gr) < 2:
            continue
        row = {"score": c}
        for k, v in gr.items():
            row[f"{k}__n"] = len(v)
            row[f"{k}__mean"] = v.mean()
            row[f"{k}__sd"] = v.std(ddof=1)
            row[f"{k}__median"] = np.median(v)
            row[f"{k}__q1"] = np.percentile(v, 25)
            row[f"{k}__q3"] = np.percentile(v, 75)
        vals = list(gr.values())
        if len(gr) == 2:
            x, y = vals
            t = stats.ttest_ind(x, y, equal_var=False)
            u = stats.mannwhitneyu(x, y, alternative="two-sided")
            gg, lo, hi = hedges_g(x, y)
            rrb = 2 * u.statistic / (len(x) * len(y)) - 1
            welch_df = getattr(t, "df", np.nan)
            par = {"test": "welch_t", "statistic": t.statistic, "df": welch_df, "p": t.pvalue,
                   "effect_type": "hedges_g", "effect": gg, "effect_ci_low": lo, "effect_ci_high": hi}
            npar = {"test": "mann_whitney", "statistic": u.statistic, "df": np.nan, "p": u.pvalue,
                    "effect_type": "rank_biserial_r", "effect": rrb, "effect_ci_low": np.nan,
                    "effect_ci_high": np.nan}
        else:
            f, d1, d2, p = welch_anova(vals)
            eta2, om2 = eta_omega_sq(vals)
            h = stats.kruskal(*vals)
            n = sum(len(v) for v in vals)
            eps2 = h.statistic / (n - 1)
            par = {"test": "welch_anova", "statistic": f, "df": f"{d1:.0f}; {d2:.1f}", "p": p,
                   "effect_type": "omega2", "effect": om2, "eta2": eta2,
                   "effect_ci_low": np.nan, "effect_ci_high": np.nan}
            npar = {"test": "kruskal", "statistic": h.statistic, "df": len(vals) - 1,
                    "p": h.pvalue, "effect_type": "epsilon2", "effect": eps2,
                    "effect_ci_low": np.nan, "effect_ci_high": np.nan}
        prim, sec = (par, npar) if parametric else (npar, par)
        row.update({f"primary_{k}": v for k, v in prim.items()})
        row["primary_magnitude"] = magnitude(prim["effect_type"], prim["effect"])
        row["secondary_test"] = sec["test"]
        row["secondary_p"] = sec["p"]
        rows.append(row)
        if len(gr) > 2:
            posthoc[c] = games_howell(gr) if parametric else dunn(gr)

    tbl = pd.DataFrame(rows)
    if not tbl.empty:
        tbl["primary_p_holm"] = holm(tbl["primary_p"].tolist())
    return {"group_var": group_var, "levels": [str(lv) for lv in levels],
            "group_sizes": {str(k): v for k, v in sizes.items()}, "dropped_small_groups": dropped,
            "parametric": parametric, "method_reason": reason,
            "table": tbl, "posthoc": posthoc}


# --------------------------------------------------------------- correlations
def spearman_ci(r: float, n: int) -> tuple[float, float]:
    """Fisher 95% CI with the Bonett & Wright (2000) standard error."""
    if n <= 3 or abs(r) >= 1:
        return (np.nan, np.nan)
    z = np.arctanh(r)
    se = np.sqrt((1 + r ** 2 / 2) / (n - 3))
    return float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))


def correlate(data: pd.DataFrame, xs: list[str], ys: list[str]) -> pd.DataFrame:
    rows = []
    for x in xs:
        for y in ys:
            if x == y:
                continue
            d = data[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
            if len(d) < 5:
                continue
            r, p = stats.spearmanr(d[x], d[y])
            lo, hi = spearman_ci(r, len(d))
            rows.append({"x": x, "y": y, "n": len(d), "rho": r, "ci95_low": lo,
                         "ci95_high": hi, "p": p, "magnitude": magnitude("spearman_rho", r)})
    t = pd.DataFrame(rows)
    if not t.empty:
        t["p_holm"] = holm(t["p"].tolist())
    return t


def correlation_matrix(data: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = data[cols].dropna()
    rho, p = stats.spearmanr(d.values)
    if np.isscalar(rho):
        rho = np.array([[1, rho], [rho, 1]])
        p = np.array([[0, p], [p, 0]])
    return (pd.DataFrame(rho, index=cols, columns=cols),
            pd.DataFrame(p, index=cols, columns=cols))


# ------------------------------------------------ comparison with reference values
def compare_reference(scores: pd.DataFrame, reference: dict) -> pd.DataFrame:
    """reference: {"physical": {"mean": 70.1, "sd": 16.0, "n": 500, "source": "..."}, ...}
    One-sample t-test against the reference mean, Cohen's d (sample SD). When the reference gives n and
    sd, also Welch's t from summary statistics."""
    rows = []
    for key, ref in reference.items():
        col = f"{key}_0_100"
        if col not in scores:
            continue
        s = scores[col].dropna()
        if len(s) < 3:
            continue
        mu = float(ref["mean"])
        t = stats.ttest_1samp(s, mu)
        d = (s.mean() - mu) / s.std(ddof=1)
        row = {"domain": key, "n": len(s), "sample_mean": s.mean(), "sample_sd": s.std(ddof=1),
               "ref_mean": mu, "ref_sd": ref.get("sd"), "ref_n": ref.get("n"),
               "diff": s.mean() - mu, "t_one_sample": t.statistic, "p_one_sample": t.pvalue,
               "cohen_d": d, "magnitude": magnitude("cohen_d", d), "source": ref.get("source", "")}
        if ref.get("sd") and ref.get("n"):
            tw = stats.ttest_ind_from_stats(s.mean(), s.std(ddof=1), len(s),
                                            mu, float(ref["sd"]), int(ref["n"]), equal_var=False)
            row["t_welch"] = tw.statistic
            row["p_welch"] = tw.pvalue
        rows.append(row)
    t = pd.DataFrame(rows)
    if not t.empty:
        t["p_holm"] = holm(t["p_welch" if "p_welch" in t else "p_one_sample"].tolist())
    return t


# --------------------------------------------------------- adjusted regression
def adjusted_regression(data: pd.DataFrame, score_cols: list[str], covariates: list[str]) -> dict:
    """OLS with HC3 robust standard errors, one model per domain. Categorical variables (text or <= 6
    distinct values) become dummies (first category = reference)."""
    import statsmodels.api as sm

    X = []
    for c in covariates:
        col = data[c]
        num = pd.to_numeric(col, errors="coerce")
        if num.notna().mean() > 0.9 and num.nunique() > 6:
            X.append(num.rename(c))
        else:
            X.append(pd.get_dummies(col.astype("string"), prefix=c, drop_first=True, dtype=float))
    Xdf = pd.concat(X, axis=1)
    out = {}
    for sc in score_cols:
        d = pd.concat([data[sc], Xdf], axis=1).dropna()
        if len(d) < Xdf.shape[1] + 10:
            out[sc] = {"error": "n too small for the number of predictors"}
            continue
        y = d[sc]
        Xm = sm.add_constant(d.drop(columns=sc))
        fit = sm.OLS(y, Xm).fit(cov_type="HC3")
        ci = fit.conf_int()
        sd_y = y.std(ddof=1)
        coefs = []
        for name in fit.params.index:
            if name == "const":
                continue
            sd_x = Xm[name].std(ddof=1)
            coefs.append({"term": name, "B": fit.params[name], "ci95_low": ci.loc[name, 0],
                          "ci95_high": ci.loc[name, 1], "se_HC3": fit.bse[name],
                          "p": fit.pvalues[name], "beta_std": fit.params[name] * sd_x / sd_y})
        vif = {}
        if Xm.shape[1] > 2:
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            for i, name in enumerate(Xm.columns):
                if name != "const":
                    vif[name] = float(variance_inflation_factor(Xm.values, i))
        out[sc] = {"n": int(fit.nobs), "r2": fit.rsquared, "r2_adj": fit.rsquared_adj,
                   "F_p": float(fit.f_pvalue), "coefficients": coefs, "vif": vif}
    return out
