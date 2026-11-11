"""Scoring-rule sensitivity analysis: alternative rules, comparison table, flags and report text."""

import numpy as np
import pandas as pd
import pytest

from whoqol import sensitivity
from whoqol.instruments import REGISTRY, get_instrument
from whoqol.scoring import score

NO_ALTERNATIVE = {"whoqol-bref", "whoqol-old", "eurohis-qol-8", "whoqol-100-bref"}


def simulate(inst, n=300, pmiss=0.06, seed=1, p=None):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({it: rng.choice(np.arange(1, inst.item_max(it) + 1), n,
                                      p=p if p and inst.item_max(it) == 5 else None).astype(float)
                       for it in inst.items})
    return df.mask(rng.random(df.shape) < pmiss)


def test_every_instrument_with_a_convention_has_alternatives():
    for key in REGISTRY:
        alts = sensitivity.alternatives(get_instrument(key))
        assert bool(alts) == (key not in NO_ALTERNATIVE), key
        for alt in alts:
            assert set(alt.label) == set(alt.rule) == {"pt", "en", "es"}
            alt.build(get_instrument(key))           # the alternative instrument is valid


def test_codes_are_unique_and_labelled():
    codes = {}
    for alts in sensitivity.ALTERNATIVES.values():
        for alt in alts:
            assert codes.setdefault(alt.code, alt) is alt, alt.code
            assert sensitivity.label_of(alt.code, "pt") == alt.label["pt"]


def test_alternative_rules_do_not_touch_the_adopted_scoring():
    """Building an alternative never mutates the registered instrument."""
    inst = get_instrument("whoqol-hiv")
    before = score(simulate(inst), inst)
    for alt in sensitivity.alternatives(inst):
        alt.build(inst)
    pd.testing.assert_frame_equal(before, score(simulate(inst), inst))


@pytest.mark.parametrize("key", ["whoqol-dis", "whoqol-dis-id", "whoqol-dis-br", "whoqol-dis-id-proxy"])
def test_dis_ufrgs_gives_the_same_0_100_when_both_rules_score(key):
    """Mean x 4 and the sum have the same 0-100 transformation: the UFRGS rule only changes who gets a score."""
    inst = get_instrument(key)
    res = {r["code"]: r["table"] for r in sensitivity.run(simulate(inst, pmiss=0.08), inst)}
    tab = res["dis_ufrgs"].set_index("score")
    for k in ("dis_discrimination", "dis_autonomy", "dis_inclusion", "dis_total"):
        assert tab.loc[k, "n_values_changed"] == 0, k
    assert (tab.loc[["dis_discrimination", "dis_autonomy", "dis_inclusion"], "n_alternative"]
            >= tab.loc[["dis_discrimination", "dis_autonomy", "dis_inclusion"], "n_adopted"]).all()


def test_f21_reversal_effect_matches_hand_calculation():
    """Energy facet = sum of its 4 items; reversing F2.1 changes it by (6 - 2 x F2.1) raw points = x 100/16 on 0-100."""
    inst = get_instrument("whoqol-hiv")
    alt = sensitivity.F21_UFRGS.build(inst)
    df = simulate(inst, n=1, pmiss=0, seed=3)
    for x in (1, 2, 3, 4, 5):
        df.loc[0, "F2.1"] = x
        d = score(df, alt).loc[0, "energy_0_100"] - score(df, inst).loc[0, "energy_0_100"]
        assert d == pytest.approx((6 - 2 * x) * 100 / 16), x


def test_no_missing_rule_scores_everyone_with_any_answer():
    inst = get_instrument("whoqol-hiv-bref")
    df = simulate(inst, n=50, pmiss=0.0)
    df.iloc[0, :20] = np.nan                       # 11 of 31 items left: excluded by the adopted rule
    alt = sensitivity.NO_MISSING_RULE.build(inst)
    assert bool(score(df, inst).loc[0, "excluded"]) and not bool(score(df, alt).loc[0, "excluded"])


def test_flags_follow_the_thresholds():
    inst = get_instrument("whoqol-hiv")
    skewed = simulate(inst, n=400, pmiss=0.0, p=[.05, .1, .25, .35, .25])
    res = sensitivity.run(skewed, inst)
    fl = sensitivity.flags(res)
    assert {(f["alt"], f["score"]) for f in fl} >= {("f21_reversed", "energy")}
    for f in fl:
        row = next(r for r in res if r["code"] == f["alt"])["table"].set_index("score").loc[f["score"]]
        assert abs(row["delta_sd"]) >= sensitivity.FLAG_SD or \
            abs(row["n_alternative"] - row["n_adopted"]) / row["n_adopted"] >= sensitivity.FLAG_N


def test_report_section_and_methods_text(tmp_path):
    from whoqol import service
    inst = get_instrument("whoqol-hiv")
    path = tmp_path / "hiv.csv"
    simulate(inst, n=120, p=[.05, .1, .25, .35, .25]).to_csv(path, index=False)
    out = tmp_path / "out"
    summary = service.analyze(str(path), instrument="whoqol-hiv", output_dir=str(out), lang="pt")
    assert [s["alternative"] for s in summary["scoring_sensitivity"]] == ["f21_reversed", "no_missing_rule"]
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "## Análise de sensibilidade das regras de pontuação" in report
    section = report.split("## Análise de sensibilidade")[1].split("## ")[0]
    table = [ln for ln in section.splitlines() if ln.startswith("|")]
    assert len({ln.count("|") for ln in table}) == 1          # well-formed Markdown table
    methods = (out / "methods_results_pt.md").read_text(encoding="utf-8")
    assert "Como análise de sensibilidade" in methods and "F2.1" in methods


def test_instrument_without_alternatives_says_so(tmp_path, examples):
    from whoqol import service
    out = tmp_path / "out"
    summary = service.analyze(str(examples / "sample_numeric.csv"), instrument="whoqol-bref", output_dir=str(out),
                              lang="en")
    assert summary["scoring_sensitivity"] == []
    assert "## Sensitivity of the results to the scoring rules" not in (out / "report.md").read_text(encoding="utf-8")
    assert "sensitivity analysis" not in (out / "methods_results_en.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("key, phrase", [
    ("eurohis-qol-8", "soma dos oito itens"),
    ("whoqol-hiv", "F2.1"),
    ("whoqol-100-srpb", "F2.1"),
    ("whoqol-dis", "manual da OMS (2011)"),
    ("whoqol-dis-br", "manual da OMS (2011)"),
])
def test_methods_notes_state_the_divergences(key, phrase):
    inst = get_instrument(key)
    assert phrase in inst.methods_note["pt"]
    assert set(inst.methods_note) == {"pt", "en", "es"}
