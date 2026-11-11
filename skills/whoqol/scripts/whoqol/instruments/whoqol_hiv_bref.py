"""WHOQOL-HIV-BREF (31 items, six domains).

Source: UFRGS WHOQOL-HIV syntax/manual (translation of the WHO WHOQOL-HIV instructions): reverse Q3, Q4, Q5, Q8,
Q9, Q10, Q31; each domain = mean of its items x 4 (4-20); Q1 and Q2 are examined separately. Variable names
HBREF_1 ... HBREF_31. Brazilian Portuguese wording: UFRGS form.
"""

from __future__ import annotations

from .base import Domain, Instrument, LanguageVersion
from .item_texts import HIVBREF_PT

ITEMS = tuple(f"Q{n}" for n in range(1, 32))
CODES = {f"Q{n}": (f"HBREF_{n}", code) for n, (code, _) in enumerate(HIVBREF_PT, 1)}


def _dom(key, items, min_valid, labels, **kw):
    return Domain(key, tuple(f"Q{n}" for n in items), min_valid, labels, **kw)


DOMAINS = {
    "physical": _dom("physical", (3, 4, 14, 21), 3, {"pt": "Físico", "en": "Physical", "es": "Físico"}),
    "psychological": _dom("psychological", (6, 11, 15, 24, 31), 4,
                          {"pt": "Psicológico", "en": "Psychological", "es": "Psicológico"}),
    "independence": _dom("independence", (5, 20, 22, 23), 3,
                         {"pt": "Nível de independência", "en": "Level of independence",
                          "es": "Nivel de independencia"}),
    "social": _dom("social", (17, 25, 26, 27), 3,
                   {"pt": "Relações sociais", "en": "Social relationships", "es": "Relaciones sociales"}),
    "environment": _dom("environment", (12, 13, 16, 18, 19, 28, 29, 30), 6,
                        {"pt": "Meio ambiente", "en": "Environment", "es": "Ambiente"}),
    "spirituality": _dom("spirituality", (7, 8, 9, 10), 3,
                         {"pt": "Espiritualidade/religião/crenças pessoais",
                          "en": "Spirituality/religion/personal beliefs",
                          "es": "Espiritualidad/religión/creencias personales"}),
    "overall": _dom("overall", (1, 2), 2,
                    {"pt": "QV geral e saúde (Q1–Q2)", "en": "Overall QoL and general health (Q1–Q2)",
                     "es": "CV global y salud general (Q1–Q2)"}, role="global"),
}

WHOQOL_HIV_BREF = Instrument(
    key="whoqol-hiv-bref",
    name="WHOQOL-HIV-BREF",
    items=ITEMS,
    reversed_items=("Q3", "Q4", "Q5", "Q8", "Q9", "Q10", "Q31"),
    domains=DOMAINS,
    min_valid_total=25,
    item_text={"pt": {f"Q{n}": text for n, (_, text) in enumerate(HIVBREF_PT, 1)}},
    item_short={},
    item_patterns={},
    item_codes=CODES,
    versions=(
        LanguageVersion(
            "pt-BR", "pt", "Zimpel & Fleck, 2007",
            "Zimpel RR, Fleck MP. Quality of life in HIV-positive Brazilians: application and validation of the "
            "WHOQOL-HIV, Brazilian version. AIDS Care. 2007;19(7):923-930.",
            {"pt": "versão brasileira (Zimpel & Fleck, 2007)", "en": "Brazilian version (Zimpel & Fleck, 2007)",
             "es": "versión brasileña (Zimpel & Fleck, 2007)"}),
        LanguageVersion(
            "en", "en", "O'Connell & Skevington, 2012",
            "O'Connell KA, Skevington SM. An international quality of life instrument to assess wellbeing in adults "
            "who are HIV-positive: a short form of the WHOQOL-HIV (31 items). AIDS Behav. 2012;16(2):452-460. "
            "doi:10.1007/s10461-010-9863-0",
            {"pt": "versão internacional (O'Connell & Skevington, 2012)",
             "en": "international version (O'Connell & Skevington, 2012)",
             "es": "versión internacional (O'Connell & Skevington, 2012)"}),
    ),
    primary_reference=("O'Connell KA, Skevington SM. An international quality of life instrument to assess wellbeing "
                       "in adults who are HIV-positive: a short form of the WHOQOL-HIV (31 items). AIDS Behav. "
                       "2012;16(2):452-460. doi:10.1007/s10461-010-9863-0"),
    scoring_source="WHOQOL-HIV scoring syntax and manual distributed by the UFRGS WHOQOL group (Portuguese).",
    description={
        "pt": ("O WHOQOL-HIV-BREF é a versão abreviada do WHOQOL-HIV, com 31 itens respondidos em escalas de cinco "
               "pontos: dois itens gerais e 29 itens em seis domínios (físico, psicológico, nível de independência, "
               "relações sociais, meio ambiente e espiritualidade/religião/crenças pessoais), incluindo facetas "
               "específicas para pessoas vivendo com HIV (O'Connell & Skevington, 2012)"),
        "en": ("The WHOQOL-HIV-BREF is the short form of the WHOQOL-HIV, with 31 items answered on five-point scales: "
               "two general items and 29 items in six domains (physical, psychological, level of independence, social "
               "relationships, environment and spirituality/religion/personal beliefs), including facets specific to "
               "people living with HIV (O'Connell & Skevington, 2012)"),
        "es": ("El WHOQOL-HIV-BREF es la versión abreviada del WHOQOL-HIV, con 31 ítems respondidos en escalas de cinco "
               "puntos: dos ítems generales y 29 ítems en seis dominios (físico, psicológico, nivel de independencia, "
               "relaciones sociales, ambiente y espiritualidad/religión/creencias personales), incluidas facetas "
               "específicas para personas que viven con VIH (O'Connell & Skevington, 2012)"),
    },
    references=(
        "WHOQOL HIV Group. WHOQOL-HIV for quality of life assessment among people living with HIV and AIDS: results "
        "from the field test. AIDS Care. 2004;16(7):882-889.",
    ),
    methods_note={
        "pt": ("Como a sintaxe oficial não define regra para dados ausentes, adotou-se a do WHOQOL-BREF: um item "
               "ausente permitido por domínio (dois no domínio meio ambiente) e exclusão de questionários com mais de "
               "20% dos itens ausentes."),
        "en": ("As the official syntax defines no missing-data rule, the WHOQOL-BREF rule was adopted: one missing "
               "item allowed per domain (two in the environment domain) and exclusion of questionnaires with more "
               "than 20% of the items missing."),
        "es": ("Como la sintaxis oficial no define una regla para datos faltantes, se adoptó la del WHOQOL-BREF: un "
               "ítem faltante permitido por dominio (dos en el dominio ambiente) y exclusión de los cuestionarios con "
               "más del 20% de los ítems faltantes."),
    },
    notes=(
        "Missing data: the official syntax computes every domain from all of its items and states no rule. The "
        "toolkit adopts the WHOQOL-BREF convention instead (one missing item per domain, two in the eight-item "
        "environment domain; questionnaires with fewer than 25 of 31 valid items excluded). With complete data the "
        "scores equal the official ones; the methods text states the convention.",
        "Headers HBREF_1 ... HBREF_31 (official variable names) and the facet codes printed on the Brazilian form "
        "(F1.4, F50.1, ...) are accepted.",
    ),
)
