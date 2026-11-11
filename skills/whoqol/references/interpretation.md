# How to interpret the results

## Scores
- 0–100 (or the raw range of each score: 4–20 for WHOQOL domains and facets, sums for the WHOQOL-OLD total, WHOQOL-DIS
  module and EUROHIS index): **higher = better quality of life** in every domain (negative items are already
  reversed). Exception: WHOQOL-100/WHOQOL-HIV facet scores of negatively framed facets (pain, negative feelings,
  dependence on medication, symptoms, forgiveness and blame, concerns about the future, death and dying) keep the
  direction of the facet, as in the WHO manual; the domains that contain them are reversed.
- 0–100 is **not a percentage**; it is a linear transformation. Write "a score of 62.5 (0–100)", not "62.5% quality of life".
- **There are no official WHO cut-offs.** Options, always citing the source:
  - Silva et al. (2014, Rev Saúde Pública): cut-off 60 for "good QoL" in Brazilian **older adults**; do not
    generalize to other populations.
  - Item-mean classifications ("needs improvement" 1–2.9; "fair" 3–3.9; "good" 4–4.9; "very good" 5), common in
    Brazilian theses, are **not validated**; use at most as a complementary description.
- Comparison with **normative values** is more informative than any classification. Use only values provided by the
  user or verified in the original paper (e.g. Brazilian norms, Cruz et al., 2011, Qual Life Res; Australian norms,
  Hawthorne et al., 2006; international field trial, Skevington et al., 2004). Never estimate or recall normative
  means without checking.
- The lowest domain is where the discussion should focus. Use the item table/figure 2 to explain it (e.g. a low
  environment score driven by Q12 money and Q14 leisure).

## Practical relevance
- No minimal important difference is established for the WHOQOL-BREF. Use distribution-based benchmarks: **½ SD**
  (Norman et al., 2003) and **MDC95** (minimal detectable change, for within-person or longitudinal comparisons).
- Group differences below ~5 points (0–100) are rarely relevant even when p < .05 in large samples.
- Prefer **effect sizes with CI** over p values. Magnitudes (Cohen, 1988): g .2/.5/.8; r .1/.3/.5; ω²/ε² .01/.06/.14.

## Comparisons and associations
- Use Holm-adjusted p when the domains are compared together.
- With 3+ groups, describe post hoc pairs (Games-Howell or Dunn) only when the global test is significant.
- The parametric/non-parametric choice is made once per grouping variable; report the criterion (`method_reason`).
- Cross-sectional designs show **association, not causation**. Check confounding (age, sex, income, health
  condition) and suggest adjusted regression (`covariates`).
- Correlations between domains are typically moderate to strong (ρ .4–.7); very high values (> .85) indicate overlap.
- Convergent validity: domains should correlate positively with the global items (Q1, Q2).

## Data quality to comment on
- Exclusions by the minimum-valid-items rule and the % missing (especially Q21).
- Identical answers to every item (straight-lining): suggest a sensitivity analysis without them.
- Floor/ceiling effects > 15% limit the detection of differences and change.

## Wording
- Avoid "quality of life was good/poor" without a reference; prefer "scores below the normative values of X" or
  "the Y domain had the lowest scores".
- Use the same metric throughout (0–100 recommended; give 4–20 in a table if the journal or field uses it).
