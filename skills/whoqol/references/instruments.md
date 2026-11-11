# Supported WHOQOL instruments

`$WHOQOL instruments` lists them; `$WHOQOL guide scoring -i <key>` prints the exact rules of one instrument, generated
from the code. This page explains which key to use, where each rule comes from and where the toolkit had to choose
between sources. All scoring sources were read in the original manuals or syntax files (WHO manuals; UFRGS WHOQOL
group, https://www.ufrgs.br/qualidep); none was written from memory.

## Which key?

| Key | Instrument | Items | Scores |
|---|---|---|---|
| `whoqol-bref` | WHOQOL-BREF | 26 | 4 domains + Q1–Q2 |
| `whoqol-old` | WHOQOL-OLD module (older adults) | 24 | 6 facets (sums 4–20) + total (24–120) |
| `eurohis-qol-8` | EUROHIS-QOL 8-item index | 8 | index (sum 8–40) |
| `whoqol-hiv-bref` | WHOQOL-HIV-BREF | 31 | 6 domains + Q1–Q2 |
| `whoqol-srpb-bref` | WHOQOL-SRPB BREF (BREF + 8 SRPB items) | 34 | 4 BREF domains + 9-item SRPB domain + Q1–Q2 |
| `whoqol-srpb` | WHOQOL-SRPB module alone | 32 | 8 facets |
| `whoqol-dis` | WHOQOL-BREF + WHOQOL-DIS, physical disabilities | 39 | 4 BREF domains, Q1–Q2, Q27, 3 module facets (sums), module total |
| `whoqol-dis-id` | WHOQOL-BREF-ID + WHOQOL-DIS, intellectual disabilities (3-point scales) | 39 | as above |
| `whoqol-dis-br`, `whoqol-dis-id-br` | the same, Brazilian forms with national items Q40–Q43 | 43 | as above + national-items score |
| `whoqol-dis-id-proxy` | WHOQOL-BREF-ID + WHOQOL-DIS answered by a proxy (relative/carer), 5-point scales, Brazilian form | 43 | as `whoqol-dis-br` |
| `whoqol-100` | WHOQOL-100 | 100 | 24 facets + overall facet, 6 domains (mean of facets) |
| `whoqol-hiv` | WHOQOL-HIV (120 items) | 120 | 29 facets + overall facet, 6 domains |
| `whoqol-100-srpb` | WHOQOL-100 + WHOQOL-SRPB | 132 | as WHOQOL-100, domain VI = F24 + 8 SRPB facets |
| `whoqol-100-bref` | WHOQOL-BREF four-domain scores computed from a WHOQOL-100 (or WHOQOL-HIV) sheet | 26 of the 100 | 4 domains + Q1–Q2 |

Modules administered **with** another questionnaire (WHOQOL-OLD with the BREF, for example) are scored separately:
run the toolkit once per instrument on the same spreadsheet (`-i whoqol-bref`, then `-i whoqol-old`). The EUROHIS
index can be scored directly from a WHOQOL-BREF spreadsheet (`-i eurohis-qol-8`): the eight items are taken from
the BREF columns (BREF Q10 is EUROHIS item 7). Likewise `whoqol-100-bref` takes the 26 WHOQOL-BREF questions from
a WHOQOL-100 sheet (manual Appendix 8: Q1 = G1, Q2 = G4, Q3 = F1.4 …) for comparison with WHOQOL-BREF studies.

## Headers the detection understands

- Item ids and the official variable names: `Q1`…, `old_01`…, `HBREF_1`…, `dis_01`… (= Q27), `F1.1`/`F1_1`/`F11`
  (SPSS style of the WHOQOL-100 manual), `G1`…, `SP1.1`…
- The facet codes printed on the Brazilian forms (`F25.1`, `F50.1`, `SP3.1`…), also at the start of a long header
  ("F1.2 Você se preocupa…").
- Question numbers (`1`, `Q01`, `pergunta 1`). For the WHOQOL-100, WHOQOL-HIV and WHOQOL-SRPB, numbers follow the
  order of the **Brazilian (UFRGS) form**, which is grouped by response scale. The generic WHO version (manual
  Appendix 4) has no question numbers at all - items are identified by their facet codes - so with an international
  form use the codes or the question text. For `whoqol-100-srpb` numbers are not mapped. For `whoqol-srpb-bref`,
  numbers 1–26 are the BREF items; the eight SRPB columns need their codes.
- The full question text: Portuguese for every instrument (third person for the proxy form); English for the
  WHOQOL-BREF, WHOQOL-OLD, EUROHIS, WHOQOL-DIS, WHOQOL-SRPB and the 100 WHOQOL-100 questions (manual Appendix 4,
  also used for the WHOQOL-HIV and WHOQOL-100 + SRPB).

## Sources and conventions per instrument

**WHOQOL-OLD** — WHOQOL-OLD Manual (WHO Europe, 2005), scoring list and SPSS syntax: reverse items 1, 2, 6–10;
facets SUM.4 (every item required), total SUM.24; 0–100 = 100 × (mean − 1)/4. Forms with more than 20% of the items
missing are not used (manual).

**EUROHIS-QOL 8** — Schmidt, Mühlan & Power (2006): simple sum of the eight items. *Divergence:* the UFRGS syntax
reports the mean (1–5) and prints `Q5-Q6`, a typo for `Q5+Q6`. No missing-data rule is published: all eight items
are required (toolkit convention).

**WHOQOL-HIV-BREF** — UFRGS WHOQOL-HIV syntax: reverse Q3, Q4, Q5, Q8, Q9, Q10, Q31; domains = mean × 4. *Convention:*
the syntax computes each domain from all of its items and states no missing-data rule; the toolkit adopts the
WHOQOL-BREF rule (one missing item per domain, two in the 8-item environment domain; ≥ 25 of 31 valid items). The
methods text states it.

**WHOQOL-SRPB BREF** — UFRGS manual (Skevington et al., 2013): SRPB9 = MEAN.8(Q6, SP1.1, SP2.3, SP8.2, SP7.2,
SP3.1, SP5.3, SP6.2, SP4.2) × 4. Q6 also stays in the psychological domain. *Convention:* exclusion below 80% of the
34 items.

**WHOQOL-SRPB module** — WHO SRPB scoring: no reversed SRPB item; facet = mean of four items. *Convention:*
WHOQOL-100 rule MEAN.3 per facet and 80% of the items. The official SRPB domain needs WHOQOL-100 facet F24, so the
module alone yields facets only.

**WHOQOL-DIS** — WHOQOL-DISABILITIES manual (WHO, 2011): Q27 reversed and scored alone; Q28–Q30 reversed; facets
are sums of all their items (PD 3–15/6–30, ID 3–9/6–18); total = MEAN.10 × 12, 0–100 = (sum − 12) × 100/48 (PD)
or /24 (ID). ID version: 3-point items except Q1, Q2 and Q27. *Divergence:* the UFRGS Portuguese syntax uses
means × 4 with other minimums (MEAN.2/MEAN.2/MEAN.5, total MEAN.11) and transforms Q27 as (Q27 − 1) × 100/16; the
toolkit follows the WHO manual. *Convention (ID):* BREF domains on 3-point items as mean × 4 (4–12) with the same
linear 0–100 transformation the manual uses for the module.

**WHOQOL-DIS, Brazilian forms** (`-br`, proxy) — national items Q40–Q43 (work, environmental adaptations, study,
food) scored as in the UFRGS syntax, `domDIS_nac = MEAN.3(q40 q41 q42 q43) × 4`, outside the module total. Item 44
(physical barriers) has no scoring rule in any source and is not scored. *Convention:* exclusion below 35 of 43 items.

**WHOQOL-DIS proxy** — UFRGS form "WHOQOL-BREF-ID e Módulo Incapacidades (Versão por Representante)" (DISQOL field
test, 2008; Schmidt et al., 2010): same items in the third person, every item on a 5-point scale. *Convention:* the
manual gives no scoring of its own for proxy ratings; the 5-point rules are applied. Report proxy and self-report
scores separately.

**WHOQOL-100** — WHOQOL User Manual (WHO/MNH/MHP/98.4.Rev.1), Appendix 9: 18 reversed items; facets MEAN.3 × 4;
domains = mean of facets with pain, negative feelings and dependence on medication reversed (24 − facet),
MEAN.2/4/3/2/6; domain VI = F24; cases with < 80 valid items deleted. Facet scores keep the direction of the facet
(higher pain = more pain). *Divergence:* the manual's prose allows two missing items per facet; its syntax (used)
allows one. No total score (the manual advises against it). The manual keeps the six-domain structure for the
WHOQOL-100 and computes four-domain scores from the WHOQOL-BREF items "for comparison purposes only": that is
`whoqol-100-bref`.

**WHOQOL-HIV (120)** — UFRGS WHOQOL-HIV manual and syntax: facets F50 (symptoms, domain I), F51 (social inclusion,
IV), F52–F54 (forgiveness and blame, concerns about the future, death and dying; VI). *Divergences:* the UFRGS syntax
reverses every item of the negative facets and averages plainly (the toolkit reverses those facets at domain level,
as the WHOQOL-100 syntax does — identical domains); it also lists F2.1 among the reversed items, a known error not
reproduced. *Convention:* the syntax states no missing-data rule; the WHOQOL-100 rules are applied (≥ 96 of 120).

**WHOQOL-100 + SRPB** — WHO SRPB scoring: domain VI = mean of F24 and the eight SRPB facets. *Divergence:* that text
reverses F2.1 (error, not reproduced). *Convention:* domain VI needs 7 of 9 facets; ≥ 106 of 132 valid items.

## Sensitivity to the conventions

Every analysis rescores the data with the documented alternative of each convention above and reports the change in
means and in the number of scored respondents (report.md section, `scoring_sensitivity` sheet and JSON key; flag
when a mean moves ≥ 0.2 SD or n ≥ 5%). Alternatives: WHOQOL-HIV-BREF and WHOQOL-HIV, the syntax without a
missing-data rule; WHOQOL-HIV, F2.1 reversed (UFRGS); WHOQOL-100, two missing items per facet (manual prose);
WHOQOL-SRPB, all four items per facet (SRPB instructions); WHOQOL-SRPB BREF, no questionnaire exclusion;
WHOQOL-100 + SRPB, F2.1 reversed (SRPB text) and domain VI without a facet minimum; WHOQOL-DIS (all forms), the
UFRGS module rules and no questionnaire exclusion. The WHOQOL-BREF, WHOQOL-OLD, EUROHIS-QOL 8 (whose UFRGS mean is
the sum / 8) and the four-domain WHOQOL-100 scores follow their official source and have no alternative.

## Psychometrics on the long forms

Reliability, multitrait scaling and HTMT use the item-based scores (facets of the WHOQOL-100/HIV; with items of
negative facets reversed so that every item points to better QoL). The Python CFA is item-level up to 60 items; for
the WHOQOL-100, WHOQOL-HIV and WHOQOL-100 + SRPB it is fitted at facet level (facet scores, negative facets reversed,
as indicators of the domains with two or more facets - WHOQOL-100 domain VI has a single facet and is left out), and
the generated lavaan script fits the item-level second-order model (facets → domains) with WLSMV. Above 40 items
the item-response figure is drawn per domain.

## Language versions cited in the methods text

| Key | pt-BR | en |
|---|---|---|
| `whoqol-old` | Fleck, Chachamovich & Trentini (2006) | Power, Quinn & Schmidt (2005) |
| `eurohis-qol-8` | Pires et al. (2018) | Schmidt, Mühlan & Power (2006) |
| `whoqol-hiv-bref` | Zimpel & Fleck (2007) | O'Connell & Skevington (2012) |
| `whoqol-srpb-bref` | Zimpel et al. (2019) | Skevington, Gunson & O'Connell (2013) |
| `whoqol-srpb`, `whoqol-100-srpb` | Panzini et al. (2011) | WHOQOL SRPB Group (2006) |
| `whoqol-dis`, `whoqol-dis-id`, `-br` | Bredemeier et al. (2014) | Power & Green (2010) |
| `whoqol-dis-id-proxy` | Schmidt et al. (2010) | — |
| `whoqol-100`, `whoqol-100-bref` | Fleck et al. (1999) | The WHOQOL Group (1998) |
| `whoqol-hiv` | Zimpel & Fleck (2007) | WHOQOL HIV Group (2004) |

Full references are in the scoring guide of each instrument and in the report.
