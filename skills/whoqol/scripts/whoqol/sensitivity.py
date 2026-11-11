"""Sensitivity of the results to the scoring conventions adopted by the toolkit.

Where the WHO manuals and official syntaxes are silent or disagree, the toolkit adopts one rule and states it in the
methods text (``instruments.md``). This module rescores the same answers with each documented alternative - the
rule of another official source (the UFRGS syntax, the manual's prose) or no rule at all where the source gives none -
and reports how much the scores and the number of scored respondents change. Instruments scored entirely by their
official source (WHOQOL-BREF, WHOQOL-OLD, EUROHIS-QOL 8, WHOQOL-100 four-domain scores) have no alternative.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from .instruments import Instrument
from .scoring import score

# A change in a mean of at least 0.2 SD (Cohen's "small" effect) or in the number of scored respondents of at least
# 5% is flagged: below that, the choice of rule cannot change the conclusions in a meaningful way.
FLAG_SD = 0.2
FLAG_N = 0.05


@dataclass(frozen=True)
class Alternative:
    code: str
    label: dict[str, str]          # short name, per report language
    rule: dict[str, str]           # what the alternative rule does and where it comes from
    build: Callable[[Instrument], Instrument]


# ------------------------------------------------------------------ rule builders
def _domains(inst: Instrument, change: Callable) -> Instrument:
    return replace(inst, domains={k: change(k, d) for k, d in inst.domains.items()})


def _no_missing_rule(inst: Instrument) -> Instrument:
    """SPSS MEAN() without .n: a score is computed from any valid item (or facet); no questionnaire exclusion."""
    return replace(_domains(inst, lambda k, d: replace(d, min_valid=1)), min_valid_total=1)


def _no_exclusion(inst: Instrument) -> Instrument:
    return replace(inst, min_valid_total=1)


def _reverse_f21(inst: Instrument) -> Instrument:
    return replace(inst, reversed_items=inst.reversed_items + ("F2.1",))


def _facet_min(n: int) -> Callable[[Instrument], Instrument]:
    def build(inst: Instrument) -> Instrument:
        return _domains(inst, lambda k, d: replace(d, min_valid=n) if d.role == "facet" and not d.composite else d)
    return build


def _srpb_all_items(inst: Instrument) -> Instrument:
    """The module's eight facets are its top-level (item-based) scores."""
    return replace(_domains(inst, lambda k, d: d if d.composite else replace(d, min_valid=len(d.items))),
                   min_valid_total=1)


def _domain_vi_any_facet(inst: Instrument) -> Instrument:
    return _domains(inst, lambda k, d: replace(d, min_valid=1) if k == "spirituality" else d)


_DIS_UFRGS = {"dis_discrimination": 2, "dis_autonomy": 2, "dis_inclusion": 5, "dis_total": 11}


def _dis_ufrgs(inst: Instrument) -> Instrument:
    """UFRGS WHOQOL-DIS syntax: module facets MEAN.2/MEAN.2/MEAN.5 x 4, total MEAN.11 x 4 (the 0-100 transformation
    of mean x 4 equals that of the sum when every item is present)."""
    return _domains(inst, lambda k, d: replace(d, multiplier=4, min_valid=_DIS_UFRGS[k]) if k in _DIS_UFRGS else d)


# ------------------------------------------------------------------ alternatives per instrument
_UFRGS = {"pt": "sintaxe UFRGS", "en": "UFRGS syntax", "es": "sintaxis UFRGS"}

NO_MISSING_RULE = Alternative(
    "no_missing_rule",
    {"pt": "Sintaxe oficial, sem regra de ausentes", "en": "Official syntax, no missing-data rule",
     "es": "Sintaxis oficial, sin regla de faltantes"},
    {"pt": "como na sintaxe distribuída pela UFRGS, cada escore é a média dos itens respondidos, sem número mínimo, "
           "e nenhum questionário é excluído",
     "en": "as in the syntax distributed by UFRGS, each score is the mean of the answered items with no minimum, and "
           "no questionnaire is excluded",
     "es": "como en la sintaxis distribuida por la UFRGS, cada puntuación es la media de los ítems respondidos, sin "
           "mínimo, y no se excluye ningún cuestionario"},
    _no_missing_rule)

F21_UFRGS = Alternative(
    "f21_reversed",
    {"pt": "F2.1 invertido (" + _UFRGS["pt"] + ")", "en": "F2.1 reversed (" + _UFRGS["en"] + ")",
     "es": "F2.1 invertido (" + _UFRGS["es"] + ")"},
    {"pt": "o item F2.1 (energia suficiente) é invertido, como na sintaxe da UFRGS; o toolkit não o inverte porque "
           "a redação é positiva",
     "en": "item F2.1 (enough energy) is reversed, as in the UFRGS syntax; the toolkit does not reverse it because "
           "its wording is positive",
     "es": "el ítem F2.1 (energía suficiente) se invierte, como en la sintaxis de la UFRGS; el toolkit no lo invierte "
           "porque su redacción es positiva"},
    _reverse_f21)

F21_SRPB = replace(
    F21_UFRGS,
    code="f21_reversed_srpb",
    label={"pt": "F2.1 invertido (texto do SRPB)", "en": "F2.1 reversed (SRPB text)",
           "es": "F2.1 invertido (texto del SRPB)"},
    rule={"pt": "o item F2.1 (energia suficiente) é invertido, como no texto de pontuação do WHOQOL-SRPB",
          "en": "item F2.1 (enough energy) is reversed, as in the WHOQOL-SRPB scoring text",
          "es": "el ítem F2.1 (energía suficiente) se invierte, como en el texto de puntuación del WHOQOL-SRPB"})

FACET_TWO_MISSING = Alternative(
    "facet_two_missing",
    {"pt": "Texto do manual: até dois ausentes por faceta", "en": "Manual text: up to two missing per facet",
     "es": "Texto del manual: hasta dos faltantes por faceta"},
    {"pt": "cada faceta é calculada com dois de quatro itens, como permite o texto do manual (a sintaxe do manual, "
           "usada pelo toolkit, exige três)",
     "en": "each facet is computed from two of four items, as the manual's text allows (the manual's syntax, used by "
           "the toolkit, requires three)",
     "es": "cada faceta se calcula con dos de cuatro ítems, como permite el texto del manual (la sintaxis del manual, "
           "usada por el toolkit, exige tres)"},
    _facet_min(2))

SRPB_ALL_ITEMS = Alternative(
    "srpb_all_items",
    {"pt": "Instruções do SRPB: todos os itens", "en": "SRPB instructions: all items",
     "es": "Instrucciones del SRPB: todos los ítems"},
    {"pt": "cada faceta exige os quatro itens, como nas instruções de pontuação do SRPB, sem regra de exclusão do "
           "questionário",
     "en": "each facet requires all four items, as in the SRPB scoring instructions, with no questionnaire exclusion",
     "es": "cada faceta exige los cuatro ítems, como en las instrucciones de puntuación del SRPB, sin regla de "
           "exclusión del cuestionario"},
    _srpb_all_items)

NO_EXCLUSION = Alternative(
    "no_exclusion",
    {"pt": "Sem exclusão de questionários", "en": "No questionnaire exclusion", "es": "Sin exclusión de cuestionarios"},
    {"pt": "nenhum questionário é excluído pela proporção de itens ausentes (a fonte não define essa regra; o toolkit "
           "exclui com mais de 20% em branco)",
     "en": "no questionnaire is excluded for its share of missing items (the source sets no such rule; the toolkit "
           "excludes those with more than 20% blank)",
     "es": "no se excluye ningún cuestionario por la proporción de ítems faltantes (la fuente no define esa regla; "
           "el toolkit excluye los que tienen más del 20% en blanco)"},
    _no_exclusion)

DOMAIN_VI_ANY = Alternative(
    "domain_vi_any_facet",
    {"pt": "Domínio VI sem mínimo de facetas", "en": "Domain VI with no facet minimum",
     "es": "Dominio VI sin mínimo de facetas"},
    {"pt": "o domínio de espiritualidade é a média das facetas disponíveis, sem o mínimo de sete de nove",
     "en": "the spirituality domain is the mean of the available facets, without the minimum of seven of nine",
     "es": "el dominio de espiritualidad es la media de las facetas disponibles, sin el mínimo de siete de nueve"},
    _domain_vi_any_facet)

DIS_UFRGS = Alternative(
    "dis_ufrgs",
    {"pt": "Módulo DIS pela " + _UFRGS["pt"], "en": "DIS module by the " + _UFRGS["en"],
     "es": "Módulo DIS según la " + _UFRGS["es"]},
    {"pt": "facetas do módulo como média × 4 com imputação (mínimo de 2, 2 e 5 itens) e total com 11 de 12 itens, "
           "como na sintaxe da UFRGS; o toolkit segue o manual da OMS (somas, todos os itens; total com 10 de 12)",
     "en": "module facets as mean × 4 with imputation (minimum 2, 2 and 5 items) and total with 11 of 12 items, as in "
           "the UFRGS syntax; the toolkit follows the WHO manual (sums, every item; total with 10 of 12)",
     "es": "facetas del módulo como media × 4 con imputación (mínimo de 2, 2 y 5 ítems) y total con 11 de 12 ítems, "
           "como en la sintaxis de la UFRGS; el toolkit sigue el manual de la OMS (sumas, todos los ítems; total con "
           "10 de 12)"},
    _dis_ufrgs)

_DIS = (DIS_UFRGS, NO_EXCLUSION)
ALTERNATIVES: dict[str, tuple[Alternative, ...]] = {
    "whoqol-hiv-bref": (NO_MISSING_RULE,),
    "whoqol-hiv": (F21_UFRGS, NO_MISSING_RULE),
    "whoqol-100": (FACET_TWO_MISSING,),
    "whoqol-srpb": (SRPB_ALL_ITEMS,),
    "whoqol-srpb-bref": (NO_EXCLUSION,),
    "whoqol-100-srpb": (F21_SRPB, DOMAIN_VI_ANY),
    "whoqol-dis": _DIS,
    "whoqol-dis-id": _DIS,
    "whoqol-dis-br": _DIS,
    "whoqol-dis-id-br": _DIS,
    "whoqol-dis-id-proxy": _DIS,
}


def alternatives(inst: Instrument) -> tuple[Alternative, ...]:
    return ALTERNATIVES.get(inst.key, ())


# ------------------------------------------------------------------ comparison
def compare(items: pd.DataFrame, inst: Instrument, alt_inst: Instrument) -> pd.DataFrame:
    """One row per score (0-100): reported scores always, facets only when the alternative changes them."""
    main, alt = score(items, inst), score(items, alt_inst)
    rows = []
    for key, d in inst.domains.items():
        col = f"{key}_0_100"
        a, b = main[col], alt[col]
        both = a.notna() & b.notna()
        diff = (b - a)[both]
        changed = int((diff.abs() > 1e-9).sum())
        n_a, n_b = int(a.notna().sum()), int(b.notna().sum())
        if d.role == "facet" and not changed and n_a == n_b:
            continue
        sd = a.std()
        delta = b.mean() - a.mean()
        rows.append({
            "score": key, "n_adopted": n_a, "n_alternative": n_b, "n_both": int(both.sum()),
            "mean_adopted": a.mean(), "mean_alternative": b.mean(), "delta_mean": delta,
            "delta_sd": delta / sd if sd and not np.isnan(sd) else np.nan,
            "mean_paired_diff": diff.mean() if len(diff) else np.nan,
            "max_abs_diff": diff.abs().max() if len(diff) else np.nan,
            "n_values_changed": changed,
        })
    return pd.DataFrame(rows)


def run(items: pd.DataFrame, inst: Instrument) -> list[dict]:
    """Rescore with every alternative of the instrument: [{code, label, rule, table}]."""
    return [{"code": alt.code, "label": alt.label, "rule": alt.rule, "table": compare(items, inst, alt.build(inst))}
            for alt in alternatives(inst)]


def flags(results: list[dict]) -> list[dict]:
    """Rows where the alternative rule moves a mean by >= 0.2 SD or the number of scored respondents by >= 5%."""
    out = []
    for res in results:
        for _, row in res["table"].iterrows():
            dn = abs(row["n_alternative"] - row["n_adopted"]) / max(row["n_adopted"], 1)
            big_mean = not np.isnan(row["delta_sd"]) and abs(row["delta_sd"]) >= FLAG_SD
            if big_mean or dn >= FLAG_N:
                out.append({"code": "sensitivity", "alt": res["code"], "score": row["score"],
                            "d": row["delta_mean"], "n1": int(row["n_adopted"]), "n2": int(row["n_alternative"])})
    return out


def max_change(results: list[dict]) -> dict | None:
    """Largest absolute change of a mean (0-100) and of n across all alternatives, for the results text."""
    rows = [(res, row) for res in results for _, row in res["table"].iterrows()]
    if not rows:
        return None
    res_d, row_d = max(rows, key=lambda x: abs(x[1]["delta_mean"]) if not np.isnan(x[1]["delta_mean"]) else -1)
    res_n, row_n = max(rows, key=lambda x: abs(x[1]["n_alternative"] - x[1]["n_adopted"]))
    return {"d": abs(row_d["delta_mean"]), "d_score": row_d["score"], "d_alt": res_d["code"],
            "dn": abs(int(row_n["n_alternative"] - row_n["n_adopted"])), "dn_score": row_n["score"],
            "dn_alt": res_n["code"]}


def label_of(code: str, lang: str) -> str:
    for alts in ALTERNATIVES.values():
        for alt in alts:
            if alt.code == code:
                return alt.label.get(lang) or alt.label["en"]
    return code
