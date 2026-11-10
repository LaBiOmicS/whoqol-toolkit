import numpy as np
import pandas as pd
import pytest

from whoqol import psychometrics as psy
from whoqol import stats
from whoqol.instruments import get_instrument
from whoqol.scoring import score

BREF = get_instrument("whoqol-bref")
ITEMS = list(BREF.items)


def frame(rows):
    return pd.DataFrame(rows, columns=ITEMS, dtype=float)


def test_all_threes_gives_50():
    s = score(frame([[3] * 26]), BREF)
    for k in BREF.domains:
        assert s[f"{k}_raw"].iloc[0] == pytest.approx(12)
        assert s[f"{k}_0_100"].iloc[0] == pytest.approx(50)


def test_best_possible_with_reversed_items():
    row = [5] * 26
    for it in BREF.reversed_items:
        row[ITEMS.index(it)] = 1
    s = score(frame([row]), BREF)
    assert (s[[c for c in s if c.endswith("_0_100")]] == 100).all(axis=None)


def test_hand_calculation_physical():
    row = [3] * 26
    for k, v in {"Q3": 2, "Q4": 1, "Q10": 4, "Q15": 5, "Q16": 3, "Q17": 4, "Q18": 2}.items():
        row[ITEMS.index(k)] = v
    s = score(frame([row]), BREF)
    raw = 27 / 7 * 4  # Q3 -> 4, Q4 -> 5; mean = (4+5+4+5+3+4+2)/7
    assert s["physical_raw"].iloc[0] == pytest.approx(raw)
    assert s["physical_0_100"].iloc[0] == pytest.approx((raw - 4) * 100 / 16)


def test_missing_rules():
    row = [4] * 26
    row[ITEMS.index("Q20")] = np.nan
    row[ITEMS.index("Q3")] = row[ITEMS.index("Q4")] = np.nan
    s = score(frame([row]), BREF)
    assert not np.isnan(s["social_0_100"].iloc[0])      # 1 of 3 missing -> computed
    assert np.isnan(s["physical_0_100"].iloc[0])        # 2 of 7 missing -> not computed
    row2 = [4] * 26
    row2[ITEMS.index("Q20")] = row2[ITEMS.index("Q21")] = np.nan
    assert np.isnan(score(frame([row2]), BREF)["social_0_100"].iloc[0])
    row3 = [4] * 26
    row3[ITEMS.index("Q8")] = row3[ITEMS.index("Q9")] = np.nan
    assert not np.isnan(score(frame([row3]), BREF)["environment_0_100"].iloc[0])


def test_exclusion_rule():
    row = [4] * 26
    for it in ITEMS[:6]:
        row[ITEMS.index(it)] = np.nan
    s = score(frame([row]), BREF)
    assert bool(s["excluded"].iloc[0]) and np.isnan(s["environment_0_100"].iloc[0])
    row = [4] * 26
    for it in ITEMS[:5]:
        row[ITEMS.index(it)] = np.nan
    assert not bool(score(frame([row]), BREF)["excluded"].iloc[0])


def test_alpha_known_values():
    rng = np.random.default_rng(0)
    x = rng.normal(size=500)
    assert psy.cronbach_alpha(pd.DataFrame({"a": x, "b": x, "c": x})) == pytest.approx(1)
    assert abs(psy.cronbach_alpha(pd.DataFrame(rng.normal(size=(2000, 4))))) < 0.1


def test_holm():
    assert stats.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])


def test_registry():
    assert get_instrument("bref") is BREF
    with pytest.raises(ValueError):
        get_instrument("whoqol-xyz")
    md = BREF.scoring_markdown()
    assert "Q3*" in md and "6 of 7" in md and "21 of the 26" in md
