"""WHOQOL-OLD module (24 items, six facets and a total score).

Source: WHOQOL-OLD Manual (WHO European Office, Copenhagen, November 2005; M. Power and S. Schmidt for the
WHOQOL-OLD Group) - scoring list (Table 5) and SPSS syntax (Appendix): reverse old_01, old_02, old_06-old_10;
facet = SUM.4 (all four items, 4-20), total = SUM.24 (24-120), transformed = 100 x (mean - 1)/4.
Brazilian Portuguese wording and facet names: UFRGS form; Fleck, Chachamovich & Trentini (2006).
"""

from __future__ import annotations

from .base import Domain, Instrument, LanguageVersion
from .item_texts import OLD_PT

ITEMS = tuple(f"old_{n:02d}" for n in range(1, 25))
CODES = {it: (code,) for it, (code, _) in zip(ITEMS, OLD_PT, strict=True)}   # F25.1 ... in the Brazilian form


def _facet(key, items, pt, en):
    return Domain(key, tuple(f"old_{n:02d}" for n in items), 4, {"pt": pt, "en": en}, multiplier=4)


DOMAINS = {
    "sensory_abilities": _facet("sensory_abilities", (1, 2, 10, 20), "Funcionamento dos sentidos", "Sensory abilities"),
    "autonomy": _facet("autonomy", (3, 4, 5, 11), "Autonomia", "Autonomy"),
    "past_present_future": _facet("past_present_future", (12, 13, 15, 19), "Atividades passadas, presentes e futuras",
                                  "Past, present and future activities"),
    "social_participation": _facet("social_participation", (14, 16, 17, 18), "Participação social",
                                   "Social participation"),
    "death_dying": _facet("death_dying", (6, 7, 8, 9), "Morte e morrer", "Death and dying"),
    "intimacy": _facet("intimacy", (21, 22, 23, 24), "Intimidade", "Intimacy"),
    "old_total": Domain("old_total", ITEMS, 24, {"pt": "Escore total WHOQOL-OLD", "en": "WHOQOL-OLD total score"},
                        role="total", multiplier=24),
}

WHOQOL_OLD = Instrument(
    key="whoqol-old",
    name="WHOQOL-OLD",
    items=ITEMS,
    reversed_items=("old_01", "old_02", "old_06", "old_07", "old_08", "old_09", "old_10"),
    domains=DOMAINS,
    min_valid_total=20,
    item_text={"pt": {it: text for it, (_, text) in zip(ITEMS, OLD_PT, strict=True)}},
    item_short={},
    item_patterns={},
    item_codes=CODES,
    versions=(
        LanguageVersion(
            "pt-BR", "pt", "Fleck et al., 2006",
            "Fleck MP, Chachamovich E, Trentini C. Development and validation of the Portuguese version of the "
            "WHOQOL-OLD module. Rev Saúde Pública. 2006;40(5):785-791.",
            {"pt": "versão validada para o português brasileiro (Fleck et al., 2006)",
             "en": "validated Brazilian Portuguese version (Fleck et al., 2006)",
             "es": "versión validada al portugués de Brasil (Fleck et al., 2006)"}),
        LanguageVersion(
            "en", "en", "Power et al., 2005",
            "Power M, Quinn K, Schmidt S; WHOQOL-OLD Group. Development of the WHOQOL-Old module. Qual Life Res. "
            "2005;14(10):2197-2214. doi:10.1007/s11136-005-7380-9",
            {"pt": "versão original em inglês (Power et al., 2005)", "en": "original English version (Power et al., 2005)",
             "es": "versión original en inglés (Power et al., 2005)"}),
    ),
    primary_reference=("Power M, Schmidt S; WHOQOL-OLD Group. WHOQOL-OLD manual. Copenhagen: World Health "
                       "Organization, European Office; 2005."),
    scoring_source="WHOQOL-OLD Manual (WHO European Office, 2005), scoring list and SPSS syntax.",
    description={
        "pt": ("O WHOQOL-OLD é o módulo da OMS para adultos idosos, com 24 itens respondidos em escalas de cinco "
               "pontos e agrupados em seis facetas de quatro itens (funcionamento dos sentidos; autonomia; atividades "
               "passadas, presentes e futuras; participação social; morte e morrer; intimidade), além de um escore "
               "total (Power et al., 2005); é aplicado em conjunto com o WHOQOL-BREF ou o WHOQOL-100"),
        "en": ("The WHOQOL-OLD is the WHO module for older adults, with 24 items answered on five-point scales and "
               "grouped into six four-item facets (sensory abilities; autonomy; past, present and future activities; "
               "social participation; death and dying; intimacy) plus a total score (Power et al., 2005); it is "
               "administered together with the WHOQOL-BREF or the WHOQOL-100"),
        "es": ("El WHOQOL-OLD es el módulo de la OMS para adultos mayores, con 24 ítems respondidos en escalas de cinco "
               "puntos y agrupados en seis facetas de cuatro ítems (habilidades sensoriales; autonomía; actividades "
               "pasadas, presentes y futuras; participación social; muerte y morir; intimidad), además de una "
               "puntuación total (Power et al., 2005); se aplica junto con el WHOQOL-BREF o el WHOQOL-100"),
    },
    references=(
        "Power M, Quinn K, Schmidt S; WHOQOL-OLD Group. Development of the WHOQOL-Old module. Qual Life Res. "
        "2005;14(10):2197-2214. doi:10.1007/s11136-005-7380-9",
    ),
    notes=(
        "Facets and the total require every item (SPSS SUM.4 / SUM.24 in the manual): no imputation.",
        "Questionnaire exclusion: the manual does not recommend using forms with more than 20% of the items "
        "missing, i.e. fewer than 20 of 24 valid items.",
        "The WHOQOL-OLD is scored separately from the WHOQOL-BREF/WHOQOL-100 administered with it: run the toolkit "
        "once per instrument on the same spreadsheet (-i whoqol-bref, then -i whoqol-old).",
        "Item codes F25.1-F30.7 of the Brazilian form are accepted as headers; old_01-old_24 follow the order of "
        "the form.",
    ),
)
