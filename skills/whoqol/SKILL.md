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

Scoring and analysis of WHOQOL questionnaires for **Claude Code** and **Antigravity (`agy`)**. Every number comes
from the deterministic, tested Python in `scripts/`. **Never compute scores yourself and never invent normative
values.** Answer in the user's language (Portuguese, English or Spanish); script outputs are in English and must be
translated when you report them.

`{skill_dir}` is this skill's directory (Claude Code: the base directory shown when the skill loads,
`${CLAUDE_PLUGIN_ROOT}/skills/whoqol`; Antigravity: the installed plugin's `skills/whoqol`).

**Running the scripts.** Run the entry point with `uv run` (shown as `$WHOQOL`): it declares its dependencies
(PEP 723: pandas, scipy, semopy, statsmodels, matplotlib, python-docx, openpyxl), which `uv` installs on the first
run. There is no `python3` fallback: if `uv` is missing, ask the user to install it (`./install.sh` does it).

```bash
WHOQOL="uv run --quiet {skill_dir}/scripts/whoqol_cli.py"
$WHOQOL {instruments|inspect|template|score|analyze|guide} ...
$WHOQOL analyze --help
```

Every command except `guide` prints a JSON object on stdout.

> **AI assistance & confidentiality.** The tables and figures come from tested code, but the interpretation and the
> methods/results draft are AI-assisted: the researcher verifies, edits and takes responsibility for them before
> publishing, and declares AI use as the target journal requires. Questionnaire answers are personal health data
> (LGPD, GDPR): the scripts run locally and the spreadsheet is never uploaded; never paste raw rows into the chat.

## Inputs

| Argument | Default | Notes |
|---|---|---|
| `path` | — | Spreadsheet: `.xlsx`, `.xls`, `.ods`, `.csv`, `.tsv`, `.sav`. `--sheet` picks a sheet by name or index. |
| `--instrument` / `-i` | `whoqol-bref` | `$WHOQOL instruments` lists the supported ones. |
| `--mapping` | detected | JSON or `.json` file `{"Q1": "column", ...}` when detection fails or is positional. |
| `--metadata` | none | Data dictionary from `template` (`.xlsx`/`.json`), or a `variables`/`variaveis` sheet in the workbook. |
| `-g/--group`, `-c/--continuous`, `--covariate` | none | Repeatable. Grouping, continuous and adjustment variables. |
| `--reference` | none | JSON or `.json` with published means per domain, each with its `source`. Never invented. |
| `--cutoff` | none | e.g. `60` (Silva et al., 2014, older adults only), only when the user asks and it fits the population. |
| `--method` | `auto` | `parametric`, `nonparametric` or `auto` (Shapiro-Wilk/CLT, reported). |
| `--lang` | `auto` | Report language; `auto` follows the questionnaire's language (pt/en/es, English otherwise). |
| `--instrument-version` | `auto` | Language version administered (cited in the methods text). |
| `--no-cfa` | off | Skip the CFA (fine with n < 100 and a non-psychometric aim). |
| `-o/--output-dir` | `<input stem>_whoqol/` | All outputs. |

## Workflow

### Step 1. Inspect

```bash
$WHOQOL inspect "<path>" [--sheet <name>] [--metadata "<dictionary>"]
```

- All items detected (`items_detected == items_expected`)? If not, show `missing_items`/`conflicts` and get the
  right mapping (`--mapping '{"Q1": "column"}'`).
- Unrecognized answers (`unrecognized`)? Ask how to handle them before going on.
- A positional mapping (warning in `conflicts`) must be confirmed by the user.
- `version_language` null (numeric data)? Ask which validated version was administered → `--instrument-version`.

### Step 2. Data dictionary (optional)

When there are coded variables (1/2), ordinal categories (education, age band, income), missing codes (99, -9) or
the user wants to record the study context, offer a pre-filled dictionary in their language:

```bash
$WHOQOL template "<path>" --lang pt|en|es [-o "<dictionary.xlsx>"]
```

The user reviews the `variables` and `study` sheets; pass `--metadata <file>` afterwards. Do not require it for a
self-explanatory spreadsheet.

### Step 3. Agree on the plan

One concise question (Claude Code: `AskUserQuestion`; Antigravity: ask in chat): aim (descriptive, group
comparison, psychometric validation, associated factors), grouping / continuous / adjustment variables, population
(norms, cut-offs), published reference values, report language. Use `other_columns[].role_guess` to propose
options. **Headless:** use the variables the user named and list your choices in the final answer.

### Step 4. Analyse

```bash
$WHOQOL analyze "<path>" [-o "<output_dir>"] [-g <var> ...] [-c <var> ...] [--covariate <var> ...] \
  [--mapping <json>] [--metadata <file>] [--reference <json>] [--cutoff <n>] [--method auto] \
  [--lang auto] [--instrument-version auto] [--no-cfa]
```

The CFA can take a minute on large samples. `$WHOQOL score "<path>"` scores only (no statistics).

### Step 5. Interpret

Read [interpretation.md](./references/interpretation.md) (and [psychometrics.md](./references/psychometrics.md) /
[reporting.md](./references/reporting.md) as needed). Start from `flags`. Structure:

- **Sample and data quality**: analysed/excluded, missingness (Q21), straight-lining.
- **QoL profile**: domains in order, mean (SD) and 95% CI on 0-100; global items (Q1-Q2); items that explain low
  domains.
- **Psychometric properties**: α/ω (3-item social domain), CFA, HTMT, multitrait scaling.
- **Comparisons/associations**: effect size + CI, Holm p, practical relevance (½ SD, MDC).
- **Alerts and limitations**: from `flags`.
- **Files**: the paths in `files` (report.md, tables.docx, results.xlsx, figures, methods_results_{pt,en,es}.md,
  cfa_wlsmv_lavaan.R).

### Step 6. Next steps

Offer: WLSMV CFA in R for a psychometric paper, sensitivity analysis without straight-liners, adjusted regression,
comparison with cited norms.

## Rules

- 0-100 scores are not percentages. Higher = better QoL (reverse-coded items already handled).
- No official WHO cut-offs; the cut-off of 60 (Silva et al., 2014) applies to older adults only.
- Normative values only from a verifiable source given by the user or checked in the original paper.
- Cross-sectional designs show association, not causation.
- Follow `rules/AGENTS.md` (research integrity and data protection).

## Files

- [workflow.md](./references/workflow.md) — the agent workflow in short form.
- [interpretation.md](./references/interpretation.md), [psychometrics.md](./references/psychometrics.md),
  [reporting.md](./references/reporting.md), [references.md](./references/references.md) — methodological guides.
- `$WHOQOL guide scoring` — scoring rules, generated from the instrument definition.
- `scripts/whoqol_cli.py` — entry point; `scripts/whoqol/` — the analysis package (instrument registry in
  `instruments/`).
