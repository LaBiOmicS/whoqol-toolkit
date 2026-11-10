import numpy as np
import pandas as pd
import pytest

from whoqol.anchors import AMBIGUOUS_ANCHORS
from whoqol.i18n import FLAGS, LANGS, T, fmt, fmt_p, fmt_r, p_expr, report_language
from whoqol.instruments import get_instrument
from whoqol.io import detect_mapping, detect_version_language, recode_value

BREF = get_instrument("whoqol-bref")


@pytest.mark.parametrize("v,exp", [
    ("Muito ruim", 1), ("nem ruim nem boa", 3), ("Muito satisfeito(a)", 5), ("Médio", 3), ("Completamente", 5),
    ("Bastante", 4), ("Muito", 4), ("Muito pouco", 2), ("Nunca", 1), ("Muito frequentemente", 4),
    ("3 - Mais ou menos", 3), ("5", 5), (2.0, 2), (7, None), ("", None), ("99", None),
    ("Very satisfied", 5), ("An extreme amount", 5), ("Mostly", 4), ("Seldom", 2),
    ("Muy insatisfecho", 1), ("Lo normal", 3), ("Bastante satisfecho", 4), ("Extremadamente", 5),
    ("Un poco", 2), ("Totalmente", 5), ("Raramente", 2), ("Frecuentemente", 4), ("Ni buena ni mala", 3),
    ("No sabe", None),
])
def test_recode(v, exp):
    r = recode_value(v)
    assert np.isnan(r) if exp is None else r == exp


def test_anchors_unambiguous():
    assert AMBIGUOUS_ANCHORS == frozenset()


@pytest.mark.parametrize("lang", LANGS)
def test_detect_by_question_text(lang):
    df = pd.DataFrame({BREF.item_text[lang][it]: [3, 4] for it in BREF.items})
    df["Sex"] = ["F", "M"]
    d = detect_mapping(df, BREF)
    assert d["missing_items"] == []
    assert d["mapping"] == {it: BREF.item_text[lang][it] for it in BREF.items}
    assert detect_version_language(df, d["mapping"], BREF)["language"] == lang


def test_numeric_has_no_language():
    df = pd.DataFrame({f"Q{i}": [3, 4] for i in range(1, 27)})
    d = detect_mapping(df, BREF)
    assert len(d["mapping"]) == 26
    assert detect_version_language(df, d["mapping"], BREF)["language"] is None


def test_every_string_has_three_languages():
    for table in (T, FLAGS):
        for key, by_lang in table.items():
            assert set(by_lang) >= set(LANGS), key
    for v in BREF.versions:
        assert set(v.description) >= set(LANGS)
    for d in BREF.domains.values():
        assert set(d.labels) >= set(LANGS)
    for lang in LANGS:
        assert set(BREF.item_text[lang]) == set(BREF.items) == set(BREF.item_short[lang])


def test_number_formats():
    assert fmt(0.5, 2, "pt") == "0,50" and fmt(0.5, 2, "en") == "0.50"
    assert fmt_r(0.853, "en") == ".85" and fmt_r(-0.2, "en") == "-.20" and fmt_r(0.853, "es") == "0,85"
    assert fmt_p(0.0004, "pt") == "< 0,001" and fmt_p(0.0004, "en") == "< .001"
    assert p_expr(0.0004, "en") == "< .001" and p_expr(0.02, "en") == "= .020"


def test_report_language():
    assert report_language("auto", "es") == "es"
    assert report_language("auto", None) == "en"
    assert report_language("auto", "fr") == "en"
    assert report_language("pt", "es") == "pt"
