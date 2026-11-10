# Psychometric criteria used

| Property | Statistic | Reference criterion |
|---|---|---|
| Internal consistency | Cronbach's α (Feldt 95% CI), McDonald's ω | ≥ .70 adequate; > .95 suggests redundancy |
| Homogeneity | mean inter-item correlation | .15–.50 (Clark & Watson, 1995) |
| Item convergent validity | corrected item-domain r | ≥ .40 (Ware & Gandek, 1998) |
| Item discriminant validity | scaling success | r with own domain > r with the other domains |
| Domain discriminant validity | HTMT | < .85 (conservative) or < .90 (Henseler et al., 2015) |
| Factor structure | CFA of correlated domains (ML) | CFI/TLI ≥ .90 acceptable, ≥ .95 good; RMSEA ≤ .08 (≤ .06 good); SRMR ≤ .08 (Hu & Bentler, 1999) |
| Composite reliability / AVE | from standardized loadings | CR ≥ .70; AVE ≥ .50 (often not reached by WHOQOL domains) |
| Floor/ceiling effects | % at minimum/maximum | > 15% (Terwee et al., 2007) |
| Precision | SEM, MDC95 | report; compare MDC with observed differences |

WHOQOL-BREF specifics:
- **Social relationships** has 3 items, so α is usually lower (the lowest domain α in the international field
  trial, Skevington et al., 2004). Report ω and the mean inter-item r and discuss.
- **Q21 (sex life)** usually has more missing answers/refusals.
- Pain (Q3) and medical treatment (Q4) often load lower in young/healthy samples; Q15, Q16 and Q19 sometimes
  correlate more with another domain.
- ML treats Likert items as continuous. For a psychometric paper also run `cfa_wlsmv_lavaan.R` (WLSMV, polychoric
  correlations) and, with groups, test measurement invariance.
- Post hoc modifications (correlated errors) only with a theoretical rationale (e.g. Q3–Q4), reporting the original model.
- Recommended n for CFA: ≥ 200 (practical minimum 100).
