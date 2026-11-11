"""Reference cases for the WHO scoring rules, written from the WHOQOL-BREF manual and NOT from the instrument
definition in the package: domain membership, reversed items and minimum valid items are spelled out here, so a
wrong edit to `instruments/whoqol_bref.py` fails these tests instead of silently changing the expected values."""

import numpy as np
import pandas as pd
import pytest

from whoqol.instruments import get_instrument
from whoqol.scoring import score

ITEMS = [f"Q{i}" for i in range(1, 27)]

# WHOQOL-BREF manual (WHO, 1996), Table 3 / scoring syntax.
DOMAINS = {
    "physical": ["Q3", "Q4", "Q10", "Q15", "Q16", "Q17", "Q18"],
    "psychological": ["Q5", "Q6", "Q7", "Q11", "Q19", "Q26"],
    "social": ["Q20", "Q21", "Q22"],
    "environment": ["Q8", "Q9", "Q12", "Q13", "Q14", "Q23", "Q24", "Q25"],
}
REVERSED = {"Q3", "Q4", "Q26"}
MIN_VALID = {"physical": 6, "psychological": 5, "social": 2, "environment": 6}
MIN_VALID_TOTAL = 21

BREF = get_instrument("whoqol-bref")

# One respondent, every answer written out (Q1..Q26).
RESPONDENT = [4, 3, 2, 1, 3, 4, 2, 5, 3, 4, 2, 3, 4, 5, 3, 2, 4, 3, 5, 1, 4, 2, 3, 4, 5, 3]
# Computed by hand: reverse Q3 (2 -> 4), Q4 (1 -> 5), Q26 (3 -> 3); raw = mean x 4; 0-100 = (raw - 4) x 100 / 16.
#   physical      (4+5+4+3+2+4+3)/7 x 4 = 25/7 x 4 = 14.2857   -> 64.2857
#   psychological (3+4+2+2+5+3)/6 x 4   = 19/6 x 4 = 12.6667   -> 54.1667
#   social        (1+4+2)/3 x 4         =  7/3 x 4 =  9.3333   -> 33.3333
#   environment   (5+3+3+4+5+3+4+5)/8 x 4 = 32/8 x 4 = 16.0000 -> 75.0000
EXPECTED_RAW = {"physical": 100 / 7, "psychological": 38 / 3, "social": 28 / 3, "environment": 16.0}
EXPECTED_0_100 = {"physical": 450 / 7, "psychological": 325 / 6, "social": 100 / 3, "environment": 75.0}


def frame(*rows):
    return pd.DataFrame(list(rows), columns=ITEMS, dtype=float)


def test_instrument_definition_matches_the_manual():
    assert list(BREF.items) == ITEMS
    assert set(BREF.reversed_items) == REVERSED
    assert BREF.min_valid_total == MIN_VALID_TOTAL
    for key, items in DOMAINS.items():
        assert list(BREF.domains[key].items) == items
        assert BREF.domains[key].min_valid == MIN_VALID[key]


def test_hand_calculated_respondent_all_domains():
    s = score(frame(RESPONDENT), BREF)
    assert int(s["n_valid_items"].iloc[0]) == 26 and not bool(s["excluded"].iloc[0])
    for key in DOMAINS:
        assert s[f"{key}_raw"].iloc[0] == pytest.approx(EXPECTED_RAW[key])
        assert s[f"{key}_0_100"].iloc[0] == pytest.approx(EXPECTED_0_100[key])


def test_only_q3_q4_q26_are_reversed():
    for item in ITEMS:
        lo, hi = [3] * 26, [3] * 26
        lo[ITEMS.index(item)], hi[ITEMS.index(item)] = 1, 5
        s = score(frame(lo, hi), BREF)
        for key, items in DOMAINS.items():
            if item not in items:
                continue
            went_up = s[f"{key}_raw"].iloc[1] > s[f"{key}_raw"].iloc[0]
            assert went_up == (item not in REVERSED), f"{item} in {key}"


@pytest.mark.parametrize("key", list(DOMAINS))
def test_minimum_valid_items_per_domain(key):
    items = DOMAINS[key]
    missing_ok = len(items) - MIN_VALID[key]
    for n_missing, computed in [(missing_ok, True), (missing_ok + 1, False)]:
        row = [4.0] * 26
        for it in items[:n_missing]:
            row[ITEMS.index(it)] = np.nan
        s = score(frame(row), BREF)
        if 26 - n_missing < MIN_VALID_TOTAL:  # the questionnaire-level rule takes over
            continue
        assert (not np.isnan(s[f"{key}_0_100"].iloc[0])) == computed, (key, n_missing)


def test_missing_items_use_the_mean_of_the_answered_ones():
    row = list(map(float, RESPONDENT))
    row[ITEMS.index("Q10")] = np.nan  # physical keeps 6 of 7: (4+5+3+2+4+3)/6 x 4 = 14.0
    s = score(frame(row), BREF)
    assert s["physical_raw"].iloc[0] == pytest.approx(14.0)
    assert s["physical_0_100"].iloc[0] == pytest.approx(62.5)


@pytest.mark.parametrize("n_missing,excluded", [(5, False), (6, True)])
def test_questionnaire_with_fewer_than_21_items_is_excluded(n_missing, excluded):
    row = [4.0] * 26
    for it in ["Q1", "Q2", "Q5", "Q8", "Q20", "Q26"][:n_missing]:
        row[ITEMS.index(it)] = np.nan
    s = score(frame(row), BREF)
    assert bool(s["excluded"].iloc[0]) == excluded
    assert np.isnan(s["environment_0_100"].iloc[0]) == excluded


@pytest.mark.parametrize("value,raw,scaled", [(1, 4, 0), (2, 8, 25), (3, 12, 50), (4, 16, 75), (5, 20, 100)])
def test_scale_endpoints(value, raw, scaled):
    row = [value] * 26
    for it in REVERSED:
        row[ITEMS.index(it)] = 6 - value
    s = score(frame(row), BREF)
    for key in DOMAINS:
        assert s[f"{key}_raw"].iloc[0] == pytest.approx(raw)
        assert s[f"{key}_0_100"].iloc[0] == pytest.approx(scaled)
