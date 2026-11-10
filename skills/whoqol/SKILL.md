---
name: whoqol
description: >-
  Use this skill when the user provides a spreadsheet, CSV or Google Forms export of WHOQOL questionnaire answers
  (WHOQOL-BREF; more WHOQOL instruments later) or asks to score, analyse, interpret or report WHOQOL quality-of-life
  results, in Portuguese, English or Spanish (qualidade de vida, calidad de vida). Scores domains with the official
  WHO rules (physical, psychological, social relationships, environment), checks data quality, estimates reliability
  (Cronbach's alpha with CI, McDonald's omega, SEM/MDC) and validity (CFA, HTMT, multitrait scaling), compares groups
  with effect sizes and Holm correction, and writes APA tables (DOCX), figures, an XLSX workbook and a methods/results
  draft in PT, EN and ES for publication.
---

# WHOQOL analysis for publication (`whoqol-toolkit`)

Every number comes from the `whoqol` MCP tools (deterministic, tested Python). **Never compute scores yourself and
never invent normative values.** Answer in the user's language (Portuguese, English or Spanish); tool outputs are
in English and must be translated when you report them.

**Tools:** `whoqol_instruments`, `whoqol_inspect`, `whoqol_template`, `whoqol_score`, `whoqol_analyze`,
`whoqol_guide`.

**Without MCP** (or when the server failed to start), run the equivalent CLI. `{plugin_root}` is the plugin
directory (`${CLAUDE_PLUGIN_ROOT}` in Claude Code; the installed plugin folder in Antigravity;
`~/.gemini/extensions/whoqol-toolkit` in Gemini CLI):

```bash
uv run --quiet --directory "{plugin_root}" whoqol {instruments|inspect|template|score|analyze|guide} ...
uv run --quiet --directory "{plugin_root}" whoqol analyze --help
```

## Steps

1. **Inspect** with `whoqol_inspect(path)` (default instrument `whoqol-bref`).
   - All items detected? If not, show `missing_items`/`conflicts` and get the right `mapping` ({"Q1": "column"}).
   - Unrecognized answers (`unrecognized`)? Ask how to handle them before going on.
   - A positional mapping (warning in `conflicts`) must be confirmed.
   - `version_language` null (numeric data)? Ask which validated version was administered → `instrument_version`.
2. **Data dictionary (optional).** When there are coded variables (1/2), ordinal categories (education, age band,
   income), missing codes (99, -9) or the user wants to record the study context, offer
   `whoqol_template(path, lang=<user's language>)`: a pre-filled .xlsx with a variables sheet and a study sheet.
   The user reviews it; pass `metadata=<file>` afterwards. Do not require it for a self-explanatory spreadsheet.
3. **Agree on the plan** in one concise question: aim (descriptive, group comparison, psychometric validation,
   associated factors), grouping / continuous / adjustment variables, population (norms, cut-offs), published
   reference values, report language. Use `other_columns[].role_guess` to propose options.
4. **Run** `whoqol_analyze(...)`. `lang="auto"` follows the questionnaire's language; pass the user's language when
   they want the report in another one. With n < 100 and a non-psychometric aim, `run_cfa=false` is fine.
5. **Interpret.** Read `whoqol_guide("interpretation")` (and `psychometrics` / `reporting` as needed). Structure:
   - **Sample and data quality**: analysed/excluded, missingness (Q21), straight-lining.
   - **QoL profile**: domains in order, mean (SD) and 95% CI on 0-100; global items (Q1-Q2); items that explain
     low domains.
   - **Psychometric properties**: α/ω (3-item social domain), CFA, HTMT, multitrait scaling.
   - **Comparisons/associations**: effect size + CI, Holm p, practical relevance (½ SD, MDC).
   - **Alerts and limitations**: from `flags`.
   - **Files**: the paths in `files` (report.md, tables.docx, results.xlsx, figures, methods_results_{pt,en,es}.md,
     cfa_wlsmv_lavaan.R).
6. **Offer next steps**: WLSMV CFA in R for a psychometric paper, sensitivity analysis without straight-liners,
   adjusted regression, comparison with cited norms.

## Rules

- 0-100 scores are not percentages. Higher = better QoL (reverse-coded items already handled).
- No official WHO cut-offs; the cut-off of 60 (Silva et al., 2014) applies to older adults only.
- Normative values only from a verifiable source given by the user or checked in the original paper.
- Cross-sectional designs show association, not causation.
- Follow `rules/AGENTS.md` (data protection and research integrity).
