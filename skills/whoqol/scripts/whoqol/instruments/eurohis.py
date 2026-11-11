"""EUROHIS-QOL 8-item index: eight WHOQOL-BREF items summed into one score.

Sources: Schmidt, Mühlan & Power (2006) - simple summation of the eight items (8-40), higher = better QoL;
UFRGS EUROHISQOL syntax - item correspondence with the WHOQOL-BREF (E1=Q1, E2=Q2, E3=Q17, E4=Q19, E5=Q20,
E6=Q23, E7=Q10, E8=Q12).
"""

from __future__ import annotations

from .base import Domain, Instrument, LanguageVersion
from .whoqol_bref import ITEM_PATTERNS, ITEM_SHORT, ITEM_TEXT

FROM_BREF = {"E1": "Q1", "E2": "Q2", "E3": "Q17", "E4": "Q19", "E5": "Q20", "E6": "Q23", "E7": "Q10", "E8": "Q12"}
ITEMS = tuple(FROM_BREF)


def _take(source: dict) -> dict:
    return {lang: {e: texts[q] for e, q in FROM_BREF.items() if q in texts} for lang, texts in source.items()}


EUROHIS_QOL_8 = Instrument(
    key="eurohis-qol-8",
    name="EUROHIS-QOL 8-item index",
    items=ITEMS,
    reversed_items=(),
    domains={"eurohis_index": Domain("eurohis_index", ITEMS, 8,
                                     {"pt": "Índice EUROHIS-QOL", "en": "EUROHIS-QOL index",
                                      "es": "Índice EUROHIS-QOL"}, multiplier=8)},
    min_valid_total=8,
    item_text=_take(ITEM_TEXT),
    item_short=_take(ITEM_SHORT),
    item_patterns={e: ITEM_PATTERNS[q] for e, q in FROM_BREF.items()},
    derived_from=("whoqol-bref", FROM_BREF),
    versions=(
        LanguageVersion(
            "pt-BR", "pt", "Pires et al., 2018",
            "Pires AC, Fleck MPA, Power M, da Rocha NS. Psychometric properties of the EUROHIS-QOL 8-item index "
            "(WHOQOL-8) in a Brazilian sample. Braz J Psychiatry. 2018;40(3):249-255. doi:10.1590/1516-4446-2017-2297",
            {"pt": "versão brasileira (Pires et al., 2018)", "en": "Brazilian version (Pires et al., 2018)",
             "es": "versión brasileña (Pires et al., 2018)"}),
        LanguageVersion(
            "en", "en", "Schmidt et al., 2006",
            "Schmidt S, Mühlan H, Power M. The EUROHIS-QOL 8-item index: psychometric results of a cross-cultural "
            "field study. Eur J Public Health. 2006;16(4):420-428. doi:10.1093/eurpub/cki155",
            {"pt": "versão em inglês (Schmidt et al., 2006)", "en": "English version (Schmidt et al., 2006)",
             "es": "versión en inglés (Schmidt et al., 2006)"}),
    ),
    primary_reference=("Schmidt S, Mühlan H, Power M. The EUROHIS-QOL 8-item index: psychometric results of a "
                       "cross-cultural field study. Eur J Public Health. 2006;16(4):420-428. doi:10.1093/eurpub/cki155"),
    scoring_source="Schmidt, Mühlan & Power (2006); item correspondence from the UFRGS EUROHISQOL syntax.",
    description={
        "pt": ("O índice EUROHIS-QOL de 8 itens é uma medida breve de qualidade de vida derivada do WHOQOL-BREF, "
               "com dois itens de cada domínio (físico, psicológico, relações sociais e meio ambiente) respondidos em "
               "escalas de cinco pontos e somados em um escore único (Schmidt et al., 2006)"),
        "en": ("The EUROHIS-QOL 8-item index is a brief quality-of-life measure derived from the WHOQOL-BREF, with "
               "two items from each domain (physical, psychological, social relationships and environment) answered "
               "on five-point scales and summed into a single score (Schmidt et al., 2006)"),
        "es": ("El índice EUROHIS-QOL de 8 ítems es una medida breve de calidad de vida derivada del WHOQOL-BREF, con "
               "dos ítems de cada dominio (físico, psicológico, relaciones sociales y ambiente) respondidos en escalas "
               "de cinco puntos y sumados en una puntuación única (Schmidt et al., 2006)"),
    },
    references=(),
    methods_note={
        "pt": ("O índice correspondeu à soma dos oito itens (8–40; Schmidt et al., 2006), transformada para 0–100; a "
               "sintaxe do grupo WHOQOL brasileiro (UFRGS) relata a média dos itens (1–5), que equivale à soma "
               "dividida por oito. Como não há regra publicada para dados ausentes, os oito itens foram exigidos."),
        "en": ("The index was the sum of the eight items (8–40; Schmidt et al., 2006), transformed to 0–100; the "
               "Brazilian WHOQOL group's (UFRGS) syntax reports the item mean (1–5), which equals the sum divided by "
               "eight. As no missing-data rule is published, all eight items were required."),
        "es": ("El índice correspondió a la suma de los ocho ítems (8–40; Schmidt et al., 2006), transformada a "
               "0–100; la sintaxis del grupo WHOQOL brasileño (UFRGS) informa la media de los ítems (1–5), que equivale "
               "a la suma dividida entre ocho. Como no hay una regla publicada para datos faltantes, se exigieron los "
               "ocho ítems."),
    },
    notes=(
        "Score = sum of the eight items (8-40; Schmidt et al., 2006), also given on 0-100. The UFRGS syntax reports "
        "the mean of the eight items (1-5) = sum / 8 (its formula prints 'Q5-Q6', a typo for 'Q5+Q6').",
        "No missing-data rule is published: the index requires all eight items.",
        "When the spreadsheet holds the whole WHOQOL-BREF, the eight items are taken from its columns (the BREF "
        "numbering differs: BREF Q10 is EUROHIS item 7). Numbered headers otherwise follow the EUROHIS numbering "
        "(1-8).",
    ),
)
