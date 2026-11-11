"""Reference tests for the WHOQOL instruments beyond the WHOQOL-BREF.

The constants below are transcribed from the scoring sources (cited per block), NOT from the toolkit code, and the
expected scores of each respondent were calculated by hand. If one of these tests fails, the code drifted from the
manual - fix the code, not the constant.
"""

import math

import numpy as np
import pandas as pd
import pytest

from whoqol.instruments import REGISTRY, get_instrument
from whoqol.io import build_item_frame, detect_mapping, parse_mapping, recode_value
from whoqol.psychometrics import facet_indicators
from whoqol.scoring import reversed_items_frame, score

BREF_RESPONDENT = [4, 3, 2, 1, 3, 4, 2, 5, 3, 4, 2, 3, 4, 5, 3, 2, 4, 3, 5, 1, 4, 2, 3, 4, 5, 3]  # Q1..Q26
BREF_RAW = {"physical": 100 / 7, "psychological": 38 / 3, "social": 28 / 3, "environment": 16.0}


def frame(inst, values: dict) -> pd.DataFrame:
    return pd.DataFrame([{it: values.get(it, np.nan) for it in inst.items}], dtype=float)


def check(sc: pd.DataFrame, key: str, raw: float, lo: float, hi: float) -> None:
    got = sc.loc[0, f"{key}_raw"]
    assert got == pytest.approx(raw), (key, got, raw)
    assert sc.loc[0, f"{key}_0_100"] == pytest.approx((raw - lo) * 100 / (hi - lo)), key


# ------------------------------------------------------------------------------------------- registry
def test_registry_lists_all_forms():
    assert set(REGISTRY) == {"whoqol-bref", "whoqol-old", "eurohis-qol-8", "whoqol-hiv-bref", "whoqol-srpb-bref",
                             "whoqol-srpb", "whoqol-dis", "whoqol-dis-id", "whoqol-dis-br", "whoqol-dis-id-br",
                             "whoqol-dis-id-proxy", "whoqol-100", "whoqol-hiv", "whoqol-100-srpb", "whoqol-100-bref"}
    for alias, key in {"old": "whoqol-old", "eurohis": "eurohis-qol-8", "whoqol_hiv_bref": "whoqol-hiv-bref",
                       "hiv": "whoqol-hiv", "dis-id": "whoqol-dis-id"}.items():
        assert get_instrument(alias).key == key


@pytest.mark.parametrize("key", sorted(REGISTRY))
def test_every_instrument_documents_its_scoring(key):
    inst = REGISTRY[key]
    md = inst.scoring_markdown()
    assert inst.name in md and "0-100" in md
    assert inst.primary_reference
    for lang in ("pt", "en", "es"):
        assert inst.description[lang]
    for d in inst.domains.values():  # every score has its minimum, between 1 and its number of parts
        assert 1 <= d.min_valid <= len(d.facets or d.items)


# ------------------------------------------------------------------------------------------- WHOQOL-OLD
# WHOQOL-OLD manual (2005), Table 5 scoring list and SPSS syntax.
OLD_FACETS = {"sensory_abilities": (1, 2, 10, 20), "autonomy": (3, 4, 5, 11), "past_present_future": (12, 13, 15, 19),
              "social_participation": (14, 16, 17, 18), "death_dying": (6, 7, 8, 9), "intimacy": (21, 22, 23, 24)}
OLD_REVERSED = {1, 2, 6, 7, 8, 9, 10}
OLD_ANSWERS = [2, 1, 4, 3, 5, 1, 2, 3, 4, 2, 3, 4, 5, 2, 3, 4, 5, 1, 2, 3, 4, 5, 3, 2]  # old_01..old_24
# hand: reversed 01=4 02=5 06=5 07=4 08=3 09=2 10=4
OLD_RAW = {"sensory_abilities": 16, "autonomy": 15, "past_present_future": 14, "social_participation": 12,
           "death_dying": 14, "intimacy": 14}


def old_values():
    return {f"old_{n:02d}": v for n, v in enumerate(OLD_ANSWERS, 1)}


def test_old_structure_matches_manual():
    inst = get_instrument("whoqol-old")
    assert {int(i[-2:]) for i in inst.reversed_items} == OLD_REVERSED
    for key, nums in OLD_FACETS.items():
        assert {int(i[-2:]) for i in inst.domains[key].items} == set(nums)
        assert inst.domains[key].min_valid == 4                     # SUM.4
    assert len(inst.domains["old_total"].items) == 24 and inst.domains["old_total"].min_valid == 24   # SUM.24


def test_old_hand_calculated_respondent():
    inst = get_instrument("whoqol-old")
    sc = score(frame(inst, old_values()), inst)
    for key, raw in OLD_RAW.items():
        check(sc, key, raw, 4, 20)
    check(sc, "old_total", 85, 24, 120)
    # manual transformation: 100 x (mean - 1)/4
    assert sc.loc[0, "old_total_0_100"] == pytest.approx(100 * (85 / 24 - 1) / 4)


def test_old_requires_every_item_of_a_facet():
    inst = get_instrument("whoqol-old")
    sc = score(frame(inst, {**old_values(), "old_03": np.nan}), inst)
    assert math.isnan(sc.loc[0, "autonomy_raw"]) and math.isnan(sc.loc[0, "old_total_raw"])
    assert sc.loc[0, "sensory_abilities_raw"] == pytest.approx(16)
    five_missing = {**old_values(), **{f"old_{n:02d}": np.nan for n in (1, 3, 6, 12, 14)}}
    assert bool(score(frame(inst, five_missing), inst).loc[0, "excluded"])   # > 20% missing


def test_old_accepts_brazilian_codes_as_headers():
    inst = get_instrument("whoqol-old")
    df = pd.DataFrame({"F25.1": [1], "F26.1": [2], "old_24": [3], "F30_7": [4]})
    m = detect_mapping(df, inst)["mapping"]
    assert m["old_01"] == "F25.1" and m["old_03"] == "F26.1" and m["old_24"] == "old_24"


# ------------------------------------------------------------------------------------------- EUROHIS
# Schmidt, Mühlan & Power (2006): sum of the eight items; UFRGS syntax: E1=Q1 E2=Q2 E3=Q17 E4=Q19 E5=Q20 E6=Q23
# E7=Q10 E8=Q12.
EUROHIS_FROM_BREF = {"E1": "Q1", "E2": "Q2", "E3": "Q17", "E4": "Q19", "E5": "Q20", "E6": "Q23", "E7": "Q10",
                     "E8": "Q12"}


def test_eurohis_sum_score():
    inst = get_instrument("eurohis-qol-8")
    assert dict(inst.derived_from[1]) == EUROHIS_FROM_BREF
    vals = dict(zip(inst.items, [4, 3, 5, 2, 4, 3, 2, 5], strict=True))
    sc = score(frame(inst, vals), inst)
    check(sc, "eurohis_index", 28, 8, 40)
    sc = score(frame(inst, {**vals, "E3": np.nan}), inst)
    assert math.isnan(sc.loc[0, "eurohis_index_raw"])


def test_eurohis_from_a_whoqol_bref_spreadsheet():
    inst = get_instrument("eurohis-qol-8")
    df = pd.DataFrame([BREF_RESPONDENT], columns=[f"Q{n}" for n in range(1, 27)])
    det = detect_mapping(df, inst)
    assert det["mapping"] == EUROHIS_FROM_BREF        # BREF Q10 -> E7, not E10
    items, _ = build_item_frame(df, det["mapping"], inst)
    expected = sum(BREF_RESPONDENT[int(q[1:]) - 1] for q in EUROHIS_FROM_BREF.values())
    assert score(items, inst).loc[0, "eurohis_index_raw"] == pytest.approx(expected)


# ------------------------------------------------------------------------------------------- WHOQOL-HIV-BREF
# UFRGS WHOQOL-HIV syntax: reverse Q3 Q4 Q5 Q8 Q9 Q10 Q31; domains = mean x 4.
HIVBREF_DOMAINS = {"physical": (3, 4, 14, 21), "psychological": (6, 11, 15, 24, 31), "independence": (5, 20, 22, 23),
                   "social": (17, 25, 26, 27), "environment": (12, 13, 16, 18, 19, 28, 29, 30),
                   "spirituality": (7, 8, 9, 10)}
HIVBREF_ANSWERS = [3, 4, 2, 1, 2, 4, 5, 2, 3, 1, 3, 4, 2, 5, 3, 4, 2, 3, 4, 5, 3, 2, 4, 3, 5, 2, 4, 3, 2, 1, 2]
# hand: reversed Q3=4 Q4=5 Q5=4 Q8=4 Q9=3 Q10=5 Q31=4
HIVBREF_RAW = {"physical": 17, "psychological": 13.6, "independence": 15, "social": 13, "environment": 11.5,
               "spirituality": 17, "overall": 14}


def test_hiv_bref_structure_and_respondent():
    inst = get_instrument("whoqol-hiv-bref")
    assert set(inst.reversed_items) == {"Q3", "Q4", "Q5", "Q8", "Q9", "Q10", "Q31"}
    for key, nums in HIVBREF_DOMAINS.items():
        assert inst.domains[key].items == tuple(f"Q{n}" for n in nums)
    sc = score(frame(inst, {f"Q{n}": v for n, v in enumerate(HIVBREF_ANSWERS, 1)}), inst)
    for key, raw in HIVBREF_RAW.items():
        check(sc, key, raw, 4, 20)


def test_hiv_bref_official_variable_names():
    inst = get_instrument("whoqol-hiv-bref")
    df = pd.DataFrame({f"HBREF_{n}": [3] for n in range(1, 32)})
    assert detect_mapping(df, inst)["mapping"]["Q31"] == "HBREF_31"
    assert parse_mapping({"HBREF_5": "x", "31": "y"}, inst) == {"Q5": "x", "Q31": "y"}


# ------------------------------------------------------------------------------------------- SRPB
# WHOQOL-SRPB BREF manual (UFRGS): SRPB9 = MEAN.8(wq6, sp1.1, sp2.3, sp8.2, sp7.2, sp3.1, sp5.3, sp6.2, sp4.2) x 4.
SRPB9 = ("Q6", "SP1.1", "SP2.3", "SP8.2", "SP7.2", "SP3.1", "SP5.3", "SP6.2", "SP4.2")


def test_srpb_bref_keeps_bref_domains_and_adds_srpb():
    inst = get_instrument("whoqol-srpb-bref")
    assert set(inst.domains["srpb"].items) == set(SRPB9) and inst.domains["srpb"].min_valid == 8
    extra = dict(zip(SRPB9[1:], [5, 4, 3, 2, 4, 3, 5, 4], strict=True))
    vals = {**{f"Q{n}": v for n, v in enumerate(BREF_RESPONDENT, 1)}, **extra}
    sc = score(frame(inst, vals), inst)
    for key, raw in BREF_RAW.items():
        check(sc, key, raw, 4, 20)
    check(sc, "srpb", 34 / 9 * 4, 4, 20)                          # Q6 = 4; 4+5+4+3+2+4+3+5+4 = 34
    sc = score(frame(inst, {**vals, "SP1.1": np.nan}), inst)      # one missing: mean of the other eight
    check(sc, "srpb", 29 / 8 * 4, 4, 20)
    sc = score(frame(inst, {**vals, "SP1.1": np.nan, "SP2.3": np.nan}), inst)
    assert math.isnan(sc.loc[0, "srpb_raw"])


def test_srpb_module_facets():
    inst = get_instrument("whoqol-srpb")
    assert inst.reversed_items == ()                               # "None of the SRPB items are negatively phrased"
    vals = {f"SP{f}.{i}": ((f + i) % 5) + 1 for f in range(1, 9) for i in range(1, 5)}
    sc = score(frame(inst, vals), inst)
    check(sc, "srpb_connection", 13, 4, 20)                        # 3+4+5+1
    check(sc, "srpb_wholeness", 10, 4, 20)                         # 1+2+3+4
    sc = score(frame(inst, {**vals, "SP4.1": np.nan}), inst)
    check(sc, "srpb_wholeness", 9 / 3 * 4, 4, 20)
    sc = score(frame(inst, {**vals, "SP4.1": np.nan, "SP4.2": np.nan}), inst)
    assert math.isnan(sc.loc[0, "srpb_wholeness_raw"])


# ------------------------------------------------------------------------------------------- WHOQOL-DIS
# WHOQOL-DISABILITIES manual (2011): Q27 reversed, scored alone; Q28-Q30 reversed; facets = sums (all items);
# total = MEAN.10 x 12; PD: DIS100 = (sum - 12) x 100/48; ID: (sum - 12) x 100/24, items 1-3 except Q1, Q2, Q27.
DIS_MODULE = [2, 3, 1, 4, 5, 3, 2, 4, 5, 3, 4, 1]                  # Q28..Q39


def dis_values(module=DIS_MODULE, q27=2, bref=BREF_RESPONDENT):
    return {**{f"Q{n}": v for n, v in enumerate(bref, 1)}, "Q27": q27,
            **{f"Q{n}": v for n, v in zip(range(28, 40), module, strict=True)}}


def test_dis_pd_hand_calculated():
    inst = get_instrument("whoqol-dis")
    assert set(inst.reversed_items) == {"Q3", "Q4", "Q26", "Q27", "Q28", "Q29", "Q30"}
    sc = score(frame(inst, dis_values()), inst)
    for key, raw in BREF_RAW.items():
        check(sc, key, raw, 4, 20)
    check(sc, "disability_impact", 16, 4, 20)                      # 6 - 2 = 4, x 4
    check(sc, "dis_discrimination", 12, 3, 15)                     # 4 + 3 + 5
    check(sc, "dis_autonomy", 12, 3, 15)
    check(sc, "dis_inclusion", 19, 6, 30)
    check(sc, "dis_total", 43, 12, 60)
    assert sc.loc[0, "dis_total_0_100"] == pytest.approx((43 - 12) * 100 / 48)


def test_dis_total_allows_two_missing_items():
    inst = get_instrument("whoqol-dis")
    vals = {**dis_values(), "Q31": np.nan, "Q34": np.nan}
    sc = score(frame(inst, vals), inst)
    assert math.isnan(sc.loc[0, "dis_autonomy_raw"]) and math.isnan(sc.loc[0, "dis_inclusion_raw"])
    check(sc, "dis_total", (43 - 4 - 2) / 10 * 12, 12, 60)         # Q31 = 4, Q34 = 2 removed
    sc = score(frame(inst, {**vals, "Q35": np.nan}), inst)
    assert math.isnan(sc.loc[0, "dis_total_raw"])


ID_BREF = [4, 3, 1, 2, 3, 2, 1, 3, 2, 3, 1, 2, 3, 1, 2, 3, 2, 1, 3, 2, 1, 3, 2, 1, 3, 1]   # Q1, Q2 on 1-5


def test_dis_id_three_point_scales():
    inst = get_instrument("whoqol-dis-id")
    assert inst.item_max("Q5") == 3 and inst.item_max("Q1") == inst.item_max("Q27") == 5
    vals = dis_values(module=[1, 2, 3, 3, 3, 2, 1, 2, 3, 2, 1, 3], q27=5, bref=ID_BREF)
    sc = score(frame(inst, vals), inst)
    check(sc, "physical", 16 / 7 * 4, 4, 12)                       # Q3 3, Q4 2 (reversed 4 - x), 3, 2, 3, 2, 1
    check(sc, "disability_impact", 4, 4, 20)
    check(sc, "dis_discrimination", 6, 3, 9)                       # manual: 16.7 x (RFS - 3) = 50
    check(sc, "dis_autonomy", 8, 3, 9)
    check(sc, "dis_inclusion", 12, 6, 18)
    check(sc, "dis_total", 26, 12, 36)
    assert sc.loc[0, "dis_total_0_100"] == pytest.approx((26 - 12) * 100 / 24)


def test_dis_id_recoding_keeps_three_point_items_in_range():
    inst = get_instrument("whoqol-dis-id")
    df = pd.DataFrame({f"Q{n}": [4] for n in range(1, 40)})
    items, report = build_item_frame(df, {f"Q{n}": f"Q{n}" for n in range(1, 40)}, inst)
    assert items.loc[0, "Q1"] == 4 and items.loc[0, "Q27"] == 4
    assert math.isnan(items.loc[0, "Q5"]) and "Q5" in report
    assert math.isnan(recode_value("Muito", 3))                     # text anchors only on five-point scales


# ------------------------------------------------------------------------------------------- WHOQOL-100 family
# WHOQOL User Manual (WHO/MNH/MHP/98.4.Rev.1), Appendix 9.
REVERSED_100 = {"F2.2", "F2.4", "F3.2", "F3.4", "F7.2", "F7.3", "F9.3", "F9.4", "F10.2", "F10.4", "F13.1", "F15.4",
                "F16.3", "F18.2", "F18.4", "F22.2", "F23.2", "F23.4"}


def pattern(inst, overall=(4, 4, 3, 5)):
    """Item F{n}.{i} answers ((n + i) mod 5) + 1; SP{f}.{i} likewise; G1-G4 given."""
    vals = {}
    for it in inst.items:
        if it.startswith(("F", "SP")):
            n, i = it.lstrip("FSP").split(".")
            vals[it] = (int(n) + int(i)) % 5 + 1
    vals.update(dict(zip(("G1", "G2", "G3", "G4"), overall, strict=True)))
    return vals


def test_whoqol_100_structure_matches_manual():
    inst = get_instrument("whoqol-100")
    assert set(inst.reversed_items) == REVERSED_100
    d = inst.domains
    assert d["physical"].facets == ("pain", "energy", "sleep") and d["physical"].reversed_facets == ("pain",)
    assert d["psychological"].reversed_facets == ("negative_feelings",)
    assert d["independence"].reversed_facets == ("medication",)
    assert [d[k].min_valid for k in ("physical", "psychological", "independence", "social", "environment")] == \
        [2, 4, 3, 2, 6]
    assert all(d[f].min_valid == 3 for f in d if d[f].role == "facet")       # MEAN.3
    assert inst.min_valid_total == 80


def test_whoqol_100_hand_calculated_respondent():
    inst = get_instrument("whoqol-100")
    sc = score(frame(inst, pattern(inst)), inst)
    check(sc, "pain", 13, 4, 20)                                   # 3+4+5+1, facet direction (more pain)
    check(sc, "energy", 10, 4, 20)                                 # 4 + (6-5) + 1 + (6-2)
    check(sc, "sleep", 15, 4, 20)                                  # 5 + (6-1) + 2 + (6-3)
    check(sc, "physical", 12, 4, 20)                               # mean(24-13, 10, 15)
    check(sc, "psychological", 12.4, 4, 20)                        # mean(10, 14, 13, 12, 24-11)
    check(sc, "social", 9, 4, 20)                                  # mean(7, 10, 10)
    check(sc, "spirituality", 10, 4, 20)                           # F24 alone
    check(sc, "overall_facet", 16, 4, 20)


def test_whoqol_100_missing_rules():
    inst = get_instrument("whoqol-100")
    vals = pattern(inst)
    sc = score(frame(inst, {**vals, "F1.1": np.nan}), inst)
    check(sc, "pain", 10 / 3 * 4, 4, 20)                           # MEAN.3
    sc = score(frame(inst, {**vals, "F1.1": np.nan, "F1.2": np.nan}), inst)
    assert math.isnan(sc.loc[0, "pain_raw"])
    check(sc, "physical", 12.5, 4, 20)                             # MEAN.2(energy, sleep)
    drop = {it: np.nan for it in list(inst.items)[20:41]}          # 21 missing -> 79 valid
    assert bool(score(frame(inst, {**vals, **drop}), inst).loc[0, "excluded"])


def test_whoqol_100_psychometric_orientation():
    inst = get_instrument("whoqol-100")
    rev = reversed_items_frame(frame(inst, pattern(inst)), inst)
    assert rev.loc[0, "F1.1"] == 6 - 3                              # pain items point to better QoL
    assert rev.loc[0, "F2.2"] == 6 - 5 and rev.loc[0, "F2.1"] == 4


def test_whoqol_100_spss_style_headers():
    inst = get_instrument("whoqol-100")
    df = pd.DataFrame({"F11": [1], "F1_2": [2], "f244": [3], "G1": [4], "F111": [5]})
    m = detect_mapping(df, inst)["mapping"]
    assert m["F1.1"] == "F11" and m["F1.2"] == "F1_2" and m["F24.4"] == "f244" and m["G1"] == "G1"
    assert m["F11.1"] == "F111"


# WHOQOL-HIV (UFRGS manual and syntax): facets F50 (domain I), F51 (IV), F52-F54 (VI); negative facets F1, F8,
# F11, F50, F52, F53, F54; F51.2 and F51.4 reversed; F2.1 NOT reversed (erratum of the UFRGS list).
def test_whoqol_hiv_domains():
    inst = get_instrument("whoqol-hiv")
    assert "F2.1" not in inst.reversed_items and {"F51.2", "F51.4"} <= set(inst.reversed_items)
    assert len(inst.items) == 120
    sc = score(frame(inst, pattern(inst)), inst)
    check(sc, "hiv_symptoms", 14, 4, 20)                           # 2+3+4+5
    check(sc, "physical", 11.5, 4, 20)                             # mean(24-13, 10, 15, 24-14)
    check(sc, "social_inclusion", 15, 4, 20)                       # 3 + (6-4) + 5 + (6-1)
    check(sc, "social", 10.5, 4, 20)                               # mean(7, 10, 10, 15)
    check(sc, "spirituality", 12.25, 4, 20)                        # mean(10, 24-12, 24-11, 24-10)


def test_whoqol_hiv_equals_item_level_reversal_of_the_syntax():
    """The UFRGS syntax reverses 48 items (49 listed, minus F2.1) and averages plainly: same domains."""
    inst = get_instrument("whoqol-hiv")
    vals = pattern(inst)
    syntax_reversed = (REVERSED_100 | {"F51.2", "F51.4"}
                       | {f"F{n}.{i}" for n in (1, 8, 11, 50, 52, 53, 54) for i in range(1, 5)})
    assert len(syntax_reversed) == 48
    rv = {k: (6 - v if k in syntax_reversed else v) for k, v in vals.items()}

    def facet(n):
        return sum(rv[f"F{n}.{i}"] for i in range(1, 5))            # mean x 4 = sum with complete data

    sc = score(frame(inst, vals), inst)
    assert sc.loc[0, "physical_raw"] == pytest.approx(np.mean([facet(n) for n in (1, 2, 3, 50)]))
    assert sc.loc[0, "spirituality_raw"] == pytest.approx(np.mean([facet(n) for n in (24, 52, 53, 54)]))


# WHOQOL-SRPB scoring: Domain6 = (srpb + eight SRPB facets) / 9 x 4.
def test_whoqol_100_srpb_domain_vi():
    inst = get_instrument("whoqol-100-srpb")
    sc = score(frame(inst, pattern(inst)), inst)
    check(sc, "spirituality", 106 / 9, 4, 20)                      # F24 10 + 13+12+11+10+14+13+12+11
    check(sc, "physical", 12, 4, 20)                               # same as the WHOQOL-100


# UFRGS WHOQOL-DIS syntax: domDIS_nac = MEAN.3(q40 q41 q42 q43) x 4 (Brazilian national items, not in the total).
def test_dis_brazilian_national_items():
    inst = get_instrument("whoqol-dis-br")
    assert inst.items[-4:] == ("Q40", "Q41", "Q42", "Q43") and inst.min_valid_total == 35
    assert "Q40" not in inst.domains["dis_total"].items
    vals = {**dis_values(), "Q40": 2, "Q41": 3, "Q42": 5, "Q43": 4}
    sc = score(frame(inst, vals), inst)
    check(sc, "dis_national", 14, 4, 20)
    check(sc, "dis_total", 43, 12, 60)                             # unchanged by the national items
    sc = score(frame(inst, {**vals, "Q42": np.nan}), inst)
    check(sc, "dis_national", 9 / 3 * 4, 4, 20)
    sc = score(frame(inst, {**vals, "Q42": np.nan, "Q43": np.nan}), inst)
    assert math.isnan(sc.loc[0, "dis_national_raw"])
    df = pd.DataFrame({"Você está satisfeito(a) com a sua alimentação?": [4]})
    assert detect_mapping(df, inst)["mapping"] == {"Q43": df.columns[0]}


def test_dis_id_brazilian_national_items_three_point():
    inst = get_instrument("whoqol-dis-id-br")
    assert inst.item_max("Q40") == 3
    vals = {**dis_values(module=[1, 2, 3, 3, 3, 2, 1, 2, 3, 2, 1, 3], q27=5, bref=ID_BREF),
            "Q40": 1, "Q41": 2, "Q42": 3, "Q43": 3}
    check(score(frame(inst, vals), inst), "dis_national", 9 / 4 * 4, 4, 12)


def test_dis_id_proxy_is_five_point_with_third_person_texts():
    inst = get_instrument("whoqol-dis-id-proxy")
    assert all(inst.item_max(it) == 5 for it in inst.items) and len(inst.items) == 43
    vals = {**dis_values(), "Q40": 2, "Q41": 3, "Q42": 5, "Q43": 4}
    sc = score(frame(inst, vals), inst)
    check(sc, "dis_inclusion", 19, 6, 30)
    check(sc, "physical", BREF_RAW["physical"], 4, 20)
    df = pd.DataFrame({"Ele/ela aproveita a vida?": [3], "31. Ele/ela se sente no controle da própria vida?": [2]})
    m = detect_mapping(df, inst)["mapping"]
    assert m["Q5"] == "Ele/ela aproveita a vida?" and m["Q31"].endswith("vida?")
    assert any("Schmidt" in v.citation for v in inst.versions)


# WHOQOL User Manual, Appendix 8: WHOQOL-100 code of each WHOQOL-BREF question.
BREF_FROM_100 = {"Q1": "G1", "Q2": "G4", "Q3": "F1.4", "Q4": "F11.3", "Q5": "F4.1", "Q6": "F24.2", "Q7": "F5.3",
                 "Q8": "F16.1", "Q9": "F22.1", "Q10": "F2.1", "Q11": "F7.1", "Q12": "F18.1", "Q13": "F20.1",
                 "Q14": "F21.1", "Q15": "F9.1", "Q16": "F3.3", "Q17": "F10.3", "Q18": "F12.4", "Q19": "F6.3",
                 "Q20": "F13.3", "Q21": "F15.3", "Q22": "F14.4", "Q23": "F17.3", "Q24": "F19.3", "Q25": "F23.3",
                 "Q26": "F8.1"}


def test_bref_four_domains_from_whoqol_100_sheet():
    inst = get_instrument("whoqol-100-bref")
    assert dict(inst.derived_from[1]) == BREF_FROM_100
    vals = pattern(get_instrument("whoqol-100"))
    df = pd.DataFrame([vals])
    det = detect_mapping(df, inst)
    assert det["mapping"] == BREF_FROM_100
    items, _ = build_item_frame(df, det["mapping"], inst)
    sc = score(items, inst)
    check(sc, "physical", 19 / 7 * 4, 4, 20)       # F1.4 1->5, F11.3 5->1, 4, 1, 2, 4, 2
    check(sc, "psychological", 17 / 6 * 4, 4, 20)  # 1, 2, 4, 4, 5, F8.1 5->1
    check(sc, "social", 10 / 3 * 4, 4, 20)
    check(sc, "environment", 11.5, 4, 20)
    check(sc, "overall", 18, 4, 20)                # G1 = 4, G4 = 5


def test_whoqol_100_english_headers():
    inst = get_instrument("whoqol-100")
    df = pd.DataFrame({"How would you rate your memory?": [3], "How easily do you get tired?": [2],
                       "To what extent do you have difficulty in performing your routine activities?": [1]})
    m = detect_mapping(df, inst)["mapping"]
    assert m == {"F5.1": df.columns[0], "F2.2": df.columns[1], "F10.2": df.columns[2]}


def test_facet_level_cfa_model():
    inst = get_instrument("whoqol-100")
    sc = score(frame(inst, pattern(inst)), inst)
    model, data = facet_indicators(sc, inst)
    assert "F_PHYSICAL =~ pain + energy + sleep" in model and "SPIRITUALITY" not in model   # one-facet domain
    assert data.loc[0, "pain"] == 24 - 13 and data.loc[0, "energy"] == 10
    assert get_instrument("whoqol-hiv").domains["spirituality"].facets[0] == "srpb_facet"
