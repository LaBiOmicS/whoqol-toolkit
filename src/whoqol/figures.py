"""Publication figures (PNG 300 dpi + vector PDF), labels in the report language."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from scipy import stats as st  # noqa: E402

from .i18n import fmt, t  # noqa: E402
from .instruments import Instrument  # noqa: E402

# Validated categorical palette (fixed order) and blue<->red diverging scale with a neutral grey midpoint.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DIVERGING_5 = ["#d03b3b", "#ec9a8f", "#d9d8d3", "#86b6ef", "#1c5cab"]  # response 1 (worst) ... 5 (best)
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 9, "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.dpi": 300,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": INK,
})


def _save(fig, out: Path, name: str) -> str:
    out.mkdir(parents=True, exist_ok=True)
    png = out / f"{name}.png"
    fig.savefig(png, bbox_inches="tight")
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    return str(png)


def domain_distribution(scores: pd.DataFrame, inst: Instrument, out: Path, lang: str) -> str:
    keys = inst.model_domains
    fig, ax = plt.subplots(figsize=(1.6 * len(keys) + 0.5, 3.6))
    rng = np.random.default_rng(1)
    for i, k in enumerate(keys):
        v = scores[f"{k}_0_100"].dropna().values
        if len(v) == 0:
            continue
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=9, color=SERIES[i % 8], alpha=0.35,
                   linewidths=0, zorder=2)
        ax.boxplot(v, positions=[i], widths=0.5, patch_artist=True, showfliers=False,
                   medianprops={"color": INK, "linewidth": 1.6},
                   boxprops={"facecolor": "none", "edgecolor": INK2, "linewidth": 1},
                   whiskerprops={"color": INK2}, capprops={"color": INK2})
        ax.scatter([i], [v.mean()], marker="D", s=30, color="white", edgecolor=INK, zorder=4, linewidths=1.2)
    ax.set_xticks(range(len(keys)), [inst.domain_label(k, lang) for k in keys])
    ax.set_ylim(-3, 103)
    ax.set_ylabel(t("fig_score_axis", lang))
    ax.set_title(t("fig_dist_title", lang), loc="left")
    ax.text(1.0, -0.17, t("fig_dist_note", lang), transform=ax.transAxes, ha="right", fontsize=7, color=MUTED)
    ax.grid(axis="x", visible=False)
    return _save(fig, out, "fig1_domain_distribution")


def item_responses(items: pd.DataFrame, inst: Instrument, out: Path, lang: str) -> str:
    """Diverging stacked bars of the original 1-5 answers (reverse-coded items flagged in the label)."""
    cols = list(inst.items)
    pct = pd.DataFrame({k: items[cols].apply(lambda s, k=k: (s.dropna() == k).mean() * 100) for k in range(1, 6)})
    pct = pct.iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 0.27 * len(cols) + 0.6))
    y = np.arange(len(pct))
    left = -(pct[1] + pct[2] + pct[3] / 2)
    for k in range(1, 6):
        ax.barh(y, pct[k], left=left, color=DIVERGING_5[k - 1], height=0.72, edgecolor="white", linewidth=1,
                label=str(k))
        left = left + pct[k]
    ax.axvline(0, color=AXIS, linewidth=0.8)
    ax.set_yticks(y, [f"{it}  {inst.item_label(it, lang)}" for it in pct.index], fontsize=7.5)
    lim = max(abs(v) for v in ax.get_xlim())
    ax.set_xlim(-lim, lim)
    ticks = ax.get_xticks()
    ax.set_xticks(ticks, [f"{abs(v):.0f}%" for v in ticks])
    ax.grid(axis="y", visible=False)
    ax.set_title(t("fig_items_title", lang), loc="left")
    ax.legend(title=t("fig_response", lang), ncol=5, frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, -0.05), fontsize=8, title_fontsize=8)
    return _save(fig, out, "fig2_item_responses")


def correlation_heatmap(rho: pd.DataFrame, labels: list[str], out: Path, lang: str) -> str:
    cmap = LinearSegmentedColormap.from_list("div", ["#d03b3b", "#f0efec", "#1c5cab"])
    k = len(labels)
    fig, ax = plt.subplots(figsize=(1.0 * k + 1.4, 0.9 * k + 1.2))
    ax.imshow(rho.values, cmap=cmap, vmin=-1, vmax=1)
    for i in range(k):
        for j in range(k):
            v = rho.values[i, j]
            ax.text(j, i, fmt(v, 2, lang), ha="center", va="center", fontsize=8,
                    color="white" if abs(v) > 0.6 else INK)
    ax.set_xticks(range(k), labels, rotation=35, ha="right")
    ax.set_yticks(range(k), labels)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(t("fig_corr_title", lang), loc="left")
    return _save(fig, out, "fig3_correlations")


def group_means(data: pd.DataFrame, group_var: str, levels: list[str], inst: Instrument, out: Path,
                lang: str, idx: int = 4, label: str | None = None) -> str:
    """Mean and 95% CI per domain and group (dots with error bars; single axis)."""
    keys = inst.model_domains
    fig, ax = plt.subplots(figsize=(1.6 * len(keys) + 0.5, 3.6))
    k = len(levels)
    g = data[group_var].astype("string")
    for j, lv in enumerate(levels):
        color = SERIES[j] if j < len(SERIES) else MUTED
        xs, ms, es = [], [], []
        for i, dom in enumerate(keys):
            v = data.loc[g == lv, f"{dom}_0_100"].dropna()
            if len(v) < 2:
                continue
            xs.append(i - 0.35 + 0.7 * (j + 0.5) / k)
            ms.append(v.mean())
            es.append(st.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)))
        ax.errorbar(xs, ms, yerr=es, fmt="o", color=color, ecolor=color, elinewidth=1.4, capsize=3,
                    markersize=6, markeredgecolor="white", label=f"{lv}")
    ax.set_xticks(range(len(keys)), [inst.domain_label(d, lang) for d in keys])
    ax.set_ylim(0, 100)
    ax.set_ylabel(t("fig_mean_ci", lang))
    ax.set_title(t("fig_group_title", lang, name=label or group_var), loc="left")
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, ncol=min(k, 4), loc="lower center", bbox_to_anchor=(0.5, -0.28), fontsize=8)
    safe = "".join(ch if ch.isalnum() else "_" for ch in group_var)
    return _save(fig, out, f"fig{idx}_groups_{safe}")
