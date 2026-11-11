# Agent workflow (WHOQOL)

Answer the user in **their** language (Portuguese, English or Spanish). Script outputs are in English; translate
when you report them. Use only numbers returned by the scripts. `$WHOQOL` stands for
`uv run --quiet {skill_dir}/scripts/whoqol_cli.py` (see SKILL.md).

1. **Locate the file.** Ask for the path if missing. Formats: .xlsx, .xls, .ods, .csv, .tsv, .sav.
   Ask which instrument if it is not obvious (`$WHOQOL instruments`); the default is `whoqol-bref`.
2. **Inspect** with `$WHOQOL inspect <path>`. Check:
   - `items_detected == items_expected`? If not, show `missing_items`/`conflicts` and ask which column holds each
     missing item; pass an explicit `--mapping`.
   - `unrecognized` answers per item (typos, another scale): ask how to handle them before going on.
   - A POSITIONAL mapping (warning in `conflicts`) must be confirmed by the user.
   - `version_language`: the language version administered (pt/en/es). If null (numeric data), ask which validated
     version was used and pass `--instrument-version`; the methods text cites it.
3. **Data dictionary (optional).** Offer `$WHOQOL template <path> --lang <user's language>` when there are coded
   variables (1/2 instead of labels), ordinal categories (education, age band, income), missing codes (99, -9) or
   the user wants to record the study context. The user edits the .xlsx; pass `--metadata <file>` afterwards. A sheet named
   `variables`/`variaveis`/`metadata` inside the data workbook is read automatically (data on the first sheet).
   Do not require the dictionary when the spreadsheet is self-explanatory.
4. **Agree on the plan** in one concise question (skip what the dictionary already answers): aim (descriptive,
   group comparison, psychometric validation, associated factors); grouping, continuous and adjustment variables;
   population (for norms and cut-offs); published reference values (`--reference`, never invented); report language.
5. **Run** `$WHOQOL analyze <path> ...`. `--lang auto` follows the questionnaire's language; pass the user's language if
   they want the report in another one. Use `--no-cfa` when n < 100 and the aim is not psychometric.
6. **Interpret** with the returned JSON and [interpretation.md](interpretation.md). Start from `flags`. Structure:
   sample and data quality; QoL profile (domains in order, mean (SD) and 95% CI on 0-100, the items that explain low
   domains); psychometric properties; comparisons/associations (effect size + CI, Holm p, practical relevance);
   alerts and limitations; generated files.
7. **Deliver** the file list (report.md, tables.docx, results.xlsx, figures, methods_results_{pt,en,es}.md, lavaan
   script) and offer next steps: WLSMV CFA in R, sensitivity analysis without straight-liners, adjusted regression,
   comparison with cited norms.
