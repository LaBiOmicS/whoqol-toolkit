"""MCP server (stdio) for Claude Code, Antigravity and Gemini CLI."""

from __future__ import annotations

from typing import Literal

try:  # mcp >= 2
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP

from . import service

Lang = Literal["auto", "pt", "en", "es"]

mcp = FastMCP(
    "whoqol",
    instructions=(
        "Scoring and publication-grade analysis of WHOQOL questionnaires (WHO rules). Workflow: "
        "1) whoqol_inspect to see the detected columns and language version; 2) confirm the mapping and the analysis "
        "variables with the user (offer whoqol_template when coded variables or ordinal categories need labels); "
        "3) whoqol_analyze; 4) interpret the returned JSON with whoqol_guide('interpretation') and "
        "whoqol_guide('reporting'), answering in the user's language. Never invent numbers: use only the returned "
        "values. Normative values must come from a cited source."),
)


@mcp.tool()
def whoqol_instruments() -> str:
    """Lists the supported WHOQOL instruments (key, items, domains, recognised language versions)."""
    return service.to_json(service.instruments())


@mcp.tool()
def whoqol_inspect(path: str, instrument: str = "whoqol-bref", sheet: str | None = None,
                   metadata: str | None = None) -> str:
    """Inspects a spreadsheet (xlsx/xls/ods/csv/tsv/sav): detects the item columns (by number 'Q1', '1.' or by the
    question text in Portuguese, English or Spanish), the language version administered, sample answers,
    unrecognised answers and the likely role of the other columns. Also reads a data dictionary (metadata=.xlsx/.json,
    or a 'variables'/'variaveis' sheet in the workbook). ALWAYS run before analysing."""
    return service.to_json(service.inspect(path, instrument, sheet, metadata))


@mcp.tool()
def whoqol_template(path: str, output: str | None = None, instrument: str = "whoqol-bref",
                    sheet: str | None = None, lang: Literal["pt", "en", "es"] = "en") -> str:
    """Creates an OPTIONAL, PRE-FILLED data dictionary (.xlsx) in the user's language (pt/en/es): sheet 'variables'
    (role of each column: item/id/group/continuous/covariate/ignore, item id, label, value labels '1=Female; 2=Male',
    level order, missing codes) and sheet 'study' (population, design, country, administration mode). Useful for
    coded variables, ordinal categories or missing codes. The user reviews it and you pass metadata=<file>."""
    return service.to_json(service.template(path, output, instrument, sheet, lang))


@mcp.tool()
def whoqol_score(path: str, output: str | None = None, instrument: str = "whoqol-bref", sheet: str | None = None,
                 mapping: dict[str, str] | None = None, include_total: bool = False) -> str:
    """Scores only (no statistics) and saves a spreadsheet with raw (4-20) and 0-100 domain scores per participant.
    mapping: {"Q1": "column name", ...} when automatic detection fails."""
    return service.to_json(service.score_only(path, output, instrument, sheet, mapping, include_total))


@mcp.tool()
def whoqol_analyze(
    path: str,
    instrument: str = "whoqol-bref",
    output_dir: str | None = None,
    sheet: str | None = None,
    mapping: dict[str, str] | None = None,
    id_column: str | None = None,
    group_vars: list[str] | None = None,
    continuous_vars: list[str] | None = None,
    covariates: list[str] | None = None,
    reference: dict | None = None,
    method: Literal["auto", "parametric", "nonparametric"] = "auto",
    cutoff: float | None = None,
    include_total: bool = False,
    run_cfa: bool = True,
    lang: Lang = "auto",
    instrument_version: Literal["auto", "pt", "en", "es", "other"] = "auto",
    metadata: str | None = None,
) -> str:
    """Full publication analysis: WHO scoring, data quality, descriptives (0-100 and 4-20), floor/ceiling,
    alpha (Feldt CI), omega, SEM/MDC, multitrait scaling, HTMT, CFA, Spearman correlations, group comparisons
    (Welch/Games-Howell or Mann-Whitney/Kruskal-Wallis/Dunn, effect sizes, Holm correction), correlations with
    continuous variables, adjusted regression (HC3), reference values and cut-off.

    Writes to output_dir: results.xlsx, report.md, tables.docx (APA tables), methods_results_{pt,en,es}.md,
    figures/ (PNG 300 dpi + PDF), cfa_wlsmv_lavaan.R and results.json.

    lang: report language; 'auto' follows the questionnaire's language (pt/en/es), else English. Pass the user's
    language when they ask for it. instrument_version: language version administered (cited in the methods text);
    'auto' detects it from the answers/headers.
    metadata: optional data dictionary (see whoqol_template); explicit arguments take precedence.
    reference: {"physical": {"mean": 70.1, "sd": 16.2, "n": 751, "source": "Author, year"}, ...}
    cutoff: e.g. 60 (Silva et al., 2014, older adults) - only when the user asks for it and it fits the population.
    Returns a JSON summary to interpret (English codes)."""
    return service.to_json(service.analyze(
        path, instrument, output_dir, sheet, mapping, id_column, group_vars, continuous_vars, covariates, reference,
        method, cutoff, include_total, run_cfa, lang, instrument_version, metadata))


@mcp.tool()
def whoqol_guide(topic: Literal["workflow", "scoring", "psychometrics", "interpretation", "reporting",
                                "references"] = "interpretation", instrument: str = "whoqol-bref") -> str:
    """Methodological guide: agent workflow, scoring rules (generated from the instrument definition), psychometric
    criteria, how to interpret scores and effects, reporting checklist for publication, and references."""
    return service.guide(topic, instrument)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
