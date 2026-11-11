"""WHOQOL-SRPB module (32 items, eight facets) and WHOQOL-SRPB BREF (34 items: WHOQOL-BREF + 8).

Sources:
* WHOQOL-SRPB scoring instructions (WHO): no SRPB item is reverse-coded; facet = mean of its four items, x 4;
  the SRPB domain of the WHOQOL-100 = mean of F24 and the eight SRPB facets (see ``whoqol_100.py``).
* WHOQOL-SRPB BREF user manual (UFRGS) and Skevington, Gunson & O'Connell (2013): SRPB domain of nine items
  (BREF Q6 + one item per SRPB facet) = MEAN.8 x 4; TSRPB9 = (SRPB9 - 4) x 100/16.
Item codes SP1.1-SP8.4 are those of the Brazilian form (UFRGS); the international codes differ (SP1.1 = S1.3, ...).
English wording: Skevington et al. (2013), Table 2.
"""

from __future__ import annotations

from .base import Domain, Instrument, LanguageVersion
from .item_texts import SRPB_PT
from .whoqol_bref import DOMAINS as BREF_DOMAINS
from .whoqol_bref import ITEM_PATTERNS as BREF_PATTERNS
from .whoqol_bref import ITEM_SHORT as BREF_SHORT
from .whoqol_bref import ITEM_TEXT as BREF_TEXT
from .whoqol_bref import ITEMS as BREF_ITEMS

SRPB_ITEMS = tuple(f"SP{f}.{i}" for f in range(1, 9) for i in range(1, 5))

FACETS = {  # key: (facet number, pt, en)
    "srpb_connection": (1, "Conexão a ser ou força espiritual", "Connection to a spiritual being"),
    "srpb_meaning": (2, "Sentido na vida", "Meaning and purpose in life"),
    "srpb_awe": (3, "Admiração", "Awe and wonder"),
    "srpb_wholeness": (4, "Totalidade e integração", "Wholeness and integration"),
    "srpb_strength": (5, "Força espiritual", "Spiritual strength"),
    "srpb_peace": (6, "Paz interior", "Inner peace"),
    "srpb_hope": (7, "Esperança e otimismo", "Hope and optimism"),
    "srpb_faith": (8, "Fé", "Faith"),
}

SRPB_EN = {
    "SP1.1": "To what extent does any connection to a spiritual being help you get through hard times?",
    "SP1.2": "To what extent does any connection to a spiritual being help you to tolerate stress?",
    "SP1.3": "To what extent does any connection to a spiritual being help you to understand others?",
    "SP1.4": "To what extent does any connection to a spiritual being provide you with comfort/reassurance?",
    "SP2.1": "To what extent do you find meaning in life?",
    "SP2.2": "To what extent does taking care of other people provide meaning of life for you?",
    "SP2.3": "To what extent do you feel your life has a purpose?",
    "SP2.4": "To what extent do you feel you are here for a reason?",
    "SP3.1": "To what extent are you able to experience awe from your surroundings? (e.g. nature, art, music)",
    "SP3.2": "To what extent do you feel spirituality touched by beauty?",
    "SP3.3": "To what extent do you have feelings of inspirations/excitement in your life?",
    "SP3.4": "To what extent are you grateful for the things in nature that you can enjoy?",
    "SP4.1": "To what extent do you feel any connection between your mind, body and soul?",
    "SP4.2": "How satisfied are you that you have a balance between mind, body and soul?",
    "SP4.3": "To what extent do you feel the way you live is consistent with what you feel and think?",
    "SP4.4": "How much do your beliefs help you to create coherence between what you do, think and feel?",
    "SP5.1": "To what extent do you feel inner spiritual strength?",
    "SP5.2": "To what extent do you find spiritual strength in difficult times?",
    "SP5.3": "How much does spiritual strength help you to live better?",
    # SP5.4: the Brazilian item ("help you to feel happy in life") differs from the published English S5.4.
    "SP6.1": "To what extent do you feel peaceful within yourself?",
    "SP6.2": "To what extent do you have inner peace?",
    "SP6.3": "How much are you able to feel peaceful when you need to?",
    "SP6.4": "To what extent do you feel a sense of harmony in your life?",
    "SP7.1": "How hopeful do you feel?",
    "SP7.2": "To what extent are you hopeful about your life?",
    "SP7.3": "To what extent does being optimistic improve your quality of life?",
    "SP7.4": "How able are you able to remain optimistic in times of uncertainty?",
    "SP8.1": "To what extent does faith contribute to your well-being?",
    "SP8.2": "To what extent does faith give you comfort in daily life?",
    "SP8.3": "To what extent does faith give you strength in daily life?",
    "SP8.4": "To what extent does faith help you to enjoy life?",
}
SRPB_CODES = {it: (it.replace("SP", "SRPB"),) for it in SRPB_ITEMS}


def srpb_facets(min_valid: int = 3, role: str = "domain") -> dict[str, Domain]:
    return {k: Domain(k, tuple(f"SP{n}.{i}" for i in range(1, 5)), min_valid, {"pt": pt, "en": en}, role=role)
            for k, (n, pt, en) in FACETS.items()}


SRPB_VERSIONS = (
    LanguageVersion(
        "pt-BR", "pt", "Panzini et al., 2011",
        "Panzini RG, Maganha C, Rocha NS, Bandeira DR, Fleck MP. Validação brasileira do Instrumento de Qualidade de "
        "Vida/espiritualidade, religião e crenças pessoais. Rev Saúde Pública. 2011;45(1):153-165. "
        "doi:10.1590/S0034-89102011000100018",
        {"pt": "versão validada para o português brasileiro (Panzini et al., 2011)",
         "en": "validated Brazilian Portuguese version (Panzini et al., 2011)",
         "es": "versión validada al portugués de Brasil (Panzini et al., 2011)"}),
    LanguageVersion(
        "en", "en", "WHOQOL SRPB Group, 2006",
        "WHOQOL SRPB Group. A cross-cultural study of spirituality, religion, and personal beliefs as components of "
        "quality of life. Soc Sci Med. 2006;62(6):1486-1497.",
        {"pt": "versão internacional (WHOQOL SRPB Group, 2006)", "en": "international version (WHOQOL SRPB Group, 2006)",
         "es": "versión internacional (WHOQOL SRPB Group, 2006)"}),
)
SRPB_GROUP_2006 = SRPB_VERSIONS[1].reference

WHOQOL_SRPB = Instrument(
    key="whoqol-srpb",
    name="WHOQOL-SRPB",
    items=SRPB_ITEMS,
    reversed_items=(),
    domains=srpb_facets(),
    min_valid_total=26,
    item_text={"pt": dict(SRPB_PT), "en": SRPB_EN},
    item_short={},
    item_patterns={},
    item_codes=SRPB_CODES,
    number_map={n: it for n, it in enumerate(SRPB_PT, 1)},
    number_note="question numbers follow the order of the Brazilian form (UFRGS), which is not grouped by facet; "
                "check them against the form used, or use the codes SP1.1-SP8.4 as headers.",
    versions=SRPB_VERSIONS,
    primary_reference=SRPB_GROUP_2006,
    scoring_source="WHOQOL-SRPB scoring instructions (WHO SRPB Group).",
    description={
        "pt": ("O WHOQOL-SRPB é o módulo da OMS sobre espiritualidade, religiosidade e crenças pessoais, com 32 itens "
               "respondidos em escalas de cinco pontos e agrupados em oito facetas de quatro itens (WHOQOL SRPB Group, "
               "2006)"),
        "en": ("The WHOQOL-SRPB is the WHO module on spirituality, religion and personal beliefs, with 32 items answered "
               "on five-point scales and grouped into eight four-item facets (WHOQOL SRPB Group, 2006)"),
        "es": ("El WHOQOL-SRPB es el módulo de la OMS sobre espiritualidad, religiosidad y creencias personales, con 32 "
               "ítems respondidos en escalas de cinco puntos y agrupados en ocho facetas de cuatro ítems (WHOQOL SRPB "
               "Group, 2006)"),
    },
    methods_note={
        "pt": ("Cada faceta exigiu ao menos três de quatro itens válidos e foram excluídos questionários com mais de "
               "20% dos itens ausentes (regras do WHOQOL-100, ao qual o módulo pertence)."),
        "en": ("Each facet required at least three of four valid items and questionnaires with more than 20% of the "
               "items missing were excluded (rules of the WHOQOL-100, to which the module belongs)."),
        "es": ("Cada faceta exigió al menos tres de cuatro ítems válidos y se excluyeron los cuestionarios con más del "
               "20% de los ítems faltantes (reglas del WHOQOL-100, al que pertenece el módulo)."),
    },
    notes=(
        "Facet scores only: the official SRPB domain also needs facet F24 of the WHOQOL-100 (use -i whoqol-100-srpb "
        "for the full 132-item instrument, or -i whoqol-srpb-bref for the nine-item domain of the short form).",
        "The SRPB instructions compute facets from all four items; the toolkit applies the WHOQOL-100 rule "
        "(MEAN.3: one missing item per facet) and excludes forms with fewer than 26 of 32 valid items (80%).",
        "Codes SP1.1-SP8.4 follow the Brazilian form; the international codes of some items differ (e.g. SP1.1 = "
        "S1.3). The Brazilian SP5.4 differs from the published English S5.4.",
    ),
)

# ------------------------------------------------------------------ SRPB BREF
SRPB_BREF_EXTRA = ("SP1.1", "SP2.3", "SP8.2", "SP7.2", "SP3.1", "SP5.3", "SP6.2", "SP4.2")

WHOQOL_SRPB_BREF = Instrument(
    key="whoqol-srpb-bref",
    name="WHOQOL-SRPB BREF",
    items=BREF_ITEMS + SRPB_BREF_EXTRA,
    reversed_items=("Q3", "Q4", "Q26"),
    domains={
        **{k: d for k, d in BREF_DOMAINS.items() if k != "overall"},
        "srpb": Domain("srpb", ("Q6", *SRPB_BREF_EXTRA), 8,
                       {"pt": "Espiritualidade, religiosidade e crenças pessoais",
                        "en": "Spirituality, religion and personal beliefs",
                        "es": "Espiritualidad, religión y creencias personales"}),
        "overall": BREF_DOMAINS["overall"],
    },
    min_valid_total=28,
    item_text={"pt": {**BREF_TEXT["pt"], **{k: SRPB_PT[k] for k in SRPB_BREF_EXTRA}},
               "en": {**BREF_TEXT["en"], **{k: SRPB_EN[k] for k in SRPB_BREF_EXTRA}},
               "es": dict(BREF_TEXT["es"])},
    item_short=BREF_SHORT,
    item_patterns=BREF_PATTERNS,
    item_codes={k: SRPB_CODES[k] for k in SRPB_BREF_EXTRA},
    number_map={n: f"Q{n}" for n in range(1, 27)},
    number_note="numbers 1-26 are the WHOQOL-BREF items; name the eight SRPB columns with their codes "
                "(SP1.1, SP2.3, SP8.2, SP7.2, SP3.1, SP5.3, SP6.2, SP4.2) or map them with --mapping.",
    versions=(
        LanguageVersion(
            "pt-BR", "pt", "Zimpel et al., 2019",
            "Zimpel RR, Panzini RG, Bandeira DR, Fleck MPA, da Rocha NS. Psychometric properties of the WHOQOL-SRPB "
            "BREF, Brazilian Portuguese version. Braz J Psychiatry. 2019;41(5):411-418. doi:10.1590/1516-4446-2018-0083",
            {"pt": "versão brasileira (Zimpel et al., 2019)", "en": "Brazilian version (Zimpel et al., 2019)",
             "es": "versión brasileña (Zimpel et al., 2019)"}),
        LanguageVersion(
            "en", "en", "Skevington et al., 2013",
            "Skevington SM, Gunson KS, O'Connell KA. Introducing the WHOQOL-SRPB BREF: developing a short-form "
            "instrument for assessing spiritual, religious and personal beliefs within quality of life. Qual Life Res. "
            "2013;22(5):1073-1083. doi:10.1007/s11136-012-0237-0",
            {"pt": "versão internacional (Skevington et al., 2013)", "en": "international version (Skevington et al., 2013)",
             "es": "versión internacional (Skevington et al., 2013)"}),
    ),
    primary_reference=("Skevington SM, Gunson KS, O'Connell KA. Introducing the WHOQOL-SRPB BREF: developing a "
                       "short-form instrument for assessing spiritual, religious and personal beliefs within quality of "
                       "life. Qual Life Res. 2013;22(5):1073-1083. doi:10.1007/s11136-012-0237-0"),
    scoring_source="WHOQOL-SRPB BREF user manual (UFRGS): SRPB9 = MEAN.8(Q6, SP1.1, SP2.3, SP8.2, SP7.2, SP3.1, "
                   "SP5.3, SP6.2, SP4.2) x 4; WHOQOL-BREF domains per the WHO manual.",
    description={
        "pt": ("O WHOQOL-SRPB BREF reúne os 26 itens do WHOQOL-BREF e oito itens do módulo de espiritualidade, "
               "religiosidade e crenças pessoais, respondidos em escalas de cinco pontos; além dos quatro domínios do "
               "WHOQOL-BREF, produz um domínio de espiritualidade com nove itens (Skevington et al., 2013)"),
        "en": ("The WHOQOL-SRPB BREF combines the 26 WHOQOL-BREF items with eight items of the spirituality, religion "
               "and personal beliefs module, answered on five-point scales; besides the four WHOQOL-BREF domains, it "
               "yields a nine-item spirituality domain (Skevington et al., 2013)"),
        "es": ("El WHOQOL-SRPB BREF reúne los 26 ítems del WHOQOL-BREF y ocho ítems del módulo de espiritualidad, "
               "religiosidad y creencias personales, respondidos en escalas de cinco puntos; además de los cuatro "
               "dominios del WHOQOL-BREF, produce un dominio de espiritualidad de nueve ítems (Skevington et al., 2013)"),
    },
    references=(SRPB_GROUP_2006,
                "The WHOQOL Group. Development of the World Health Organization WHOQOL-BREF quality of life "
                "assessment. Psychol Med. 1998;28(3):551-558."),
    methods_note={
        "pt": ("O domínio de espiritualidade correspondeu à média de seus nove itens (mínimo de oito) multiplicada por "
               "quatro; foram excluídos questionários com mais de 20% dos 34 itens ausentes."),
        "en": ("The spirituality domain was the mean of its nine items (at least eight valid) multiplied by four; "
               "questionnaires with more than 20% of the 34 items missing were excluded."),
        "es": ("El dominio de espiritualidad correspondió a la media de sus nueve ítems (mínimo de ocho) multiplicada "
               "por cuatro; se excluyeron los cuestionarios con más del 20% de los 34 ítems faltantes."),
    },
    notes=(
        "Q6 (meaningful life) counts in both the psychological and the SRPB domains, as in the manual.",
        "Questionnaire exclusion: the manual gives none for the 34-item form; the toolkit keeps the WHOQOL-BREF "
        "proportion (80%: at least 28 of 34 valid items).",
    ),
)
