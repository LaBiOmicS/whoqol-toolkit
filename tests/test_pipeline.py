import json
from pathlib import Path

import pandas as pd
import pytest

from whoqol import service
from whoqol.metadata import apply_to_raw, guess_role, parse_variables


def test_parse_variables_multilingual():
    v = pd.DataFrame([
        {"coluna": "sx", "papel": "grupo", "rotulo": "Sexo", "rotulos_valores": "1=F; 2=M"},
        {"coluna": "esc", "papel": "Grupo", "ordem_niveis": "Fund; Med; Sup"},
        {"coluna": "idade", "papel": "covariável", "codigos_ausentes": "99; -9"},
        {"coluna": "p1", "papel": "item", "item": "Q1"},
        {"coluna": "xx", "papel": "banana"},
    ])
    m = parse_variables(v, {"population": "older adults"})
    assert m["group_vars"] == ["sx", "esc"] and m["covariates"] == ["idade"]
    assert m["mapping"] == {"Q1": "p1"} and m["level_order"]["esc"] == ["Fund", "Med", "Sup"]
    assert m["warnings"]
    out = apply_to_raw(pd.DataFrame({"sx": [1, 2.0, None], "idade": [30, 99, -9], "p1": [1, 2, 3]}), m)
    assert out["sx"].tolist()[:2] == ["F", "M"]
    assert out["idade"].isna().tolist() == [False, True, True]
    es = parse_variables(pd.DataFrame([{"columna": "edad", "rol": "covariable"},
                                       {"columna": "sexo", "rol": "grupo", "etiquetas_valores": "1=Mujer"}]))
    assert es["covariates"] == ["edad"] and es["value_labels"]["sexo"] == {"1": "Mujer"}
    en = parse_variables(pd.DataFrame([{"column": "age", "role": "continuous", "label": "Age"}]))
    assert en["continuous_vars"] == ["age"] and en["labels"]["age"] == "Age"


def test_guess_role():
    assert guess_role("ID", pd.Series(range(50))) == "id"
    assert guess_role("Idade", pd.Series(list(range(20, 70)))) == "continuous"
    assert guess_role("Sexo", pd.Series(["F", "M"] * 10)) == "group"
    assert guess_role("Marca temporal", pd.Series(pd.date_range("2026-01-01", periods=5))) == "ignore"


@pytest.mark.parametrize("fname,groups,lang", [
    ("sample_google_forms_pt.xlsx", ["Sexo", "Escolaridade"], "pt"),
    ("sample_forms_es.xlsx", ["Sexo", "Nivel educativo"], "es"),
    ("sample_numeric.csv", ["Sexo"], "en"),
])
def test_same_scores_any_format_and_language(examples, tmp_path, fname, groups, lang):
    r = service.analyze(str(examples / fname), output_dir=str(tmp_path), group_vars=groups, run_cfa=False)
    assert r["report_language"] == lang
    assert r["n"]["n_analyzed"] == 297 and r["n"]["n_excluded"] == 3
    assert 42 in r["data_quality"]["straightlining_rows"]
    phys = next(d for d in r["descriptives_0_100"] if d["score"] == "physical_0_100")
    assert phys["mean"] == pytest.approx(59.52, abs=0.01)
    for key in ("docx", "xlsx", "markdown", "json", "methods_pt", "methods_en", "methods_es"):
        assert Path(r["files"][key]).exists()
    assert json.loads(Path(r["files"]["json"]).read_text())["instrument"]["key"] == "whoqol-bref"


def test_forced_report_language(examples, tmp_path):
    r = service.analyze(str(examples / "sample_google_forms_pt.xlsx"), output_dir=str(tmp_path), lang="es",
                        run_cfa=False)
    assert r["report_language"] == "es" and r["version_language"] == "pt"
    md = Path(r["files"]["markdown"]).read_text()
    assert "Informe de análisis" in md and "Fleck et al., 2000" in md


@pytest.mark.parametrize("lang,sheet", [("pt", "variaveis"), ("en", "variables"), ("es", "variables")])
def test_template_roundtrip(examples, tmp_path, lang, sheet):
    out = service.template(str(examples / "sample_numeric.csv"), str(tmp_path / "m.xlsx"), lang=lang)["metadata_file"]
    v = pd.read_excel(out, sheet)
    assert (v.iloc[:, 1] == "item").sum() == 26
    insp = service.inspect(str(examples / "sample_numeric.csv"), metadata=out)
    assert len(insp["metadata"]["mapping"]) == 26
    assert insp["metadata"]["study"] == {}  # example placeholders never become values


def test_guides():
    for topic in service.GUIDE_TOPICS:
        assert len(service.guide(topic)) > 200


def test_report_is_readable_for_non_specialists(examples, tmp_path):
    """Plain-language summary, reading aids, figure captions and the construct-validity section in report.md;
    acronyms kept and near-equal domain means not ranked in the results draft."""
    service.analyze(str(examples / "sample_google_forms_pt.xlsx"), output_dir=str(tmp_path), lang="pt", run_cfa=False)
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert report.index("## Em resumo") < report.index("## Amostra")
    assert report.count("*Como ler.*") == 3
    assert "## Validade de constructo" in report and "HTMT máximo" in report
    assert "**Figura 1.** Distribuição dos escores" in report and "![](" not in report
    assert "## Análise de sensibilidade" not in report  # WHOQOL-BREF has no alternative scoring rule
    assert "(s)" not in report
    results = (tmp_path / "methods_results_pt.md").read_text(encoding="utf-8").split("## Resultados")[1]
    assert "QV geral e saúde (Q1–Q2)" in results and "qv geral" not in results
    assert "perfil semelhante entre os domínios" in results and "A média mais alta" not in results


def test_lower_label_keeps_acronyms():
    from whoqol.i18n import lower_label
    assert lower_label("QV geral e saúde (Q1–Q2)", "pt") == "QV geral e saúde (Q1–Q2)"
    assert lower_label("Relações sociais", "pt") == "relações sociais"
    assert lower_label("Social relationships", "en") == "Social relationships"
