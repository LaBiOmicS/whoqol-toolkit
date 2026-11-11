"""WHOQOL-100 and the instruments built on it: WHOQOL-HIV (120 items) and WHOQOL-100 + SRPB (132 items).

Source: WHOQOL User Manual (WHO/MNH/MHP/98.4.Rev.1), Appendix 9 SPSS syntax (also distributed by UFRGS):
* reverse F2.2 F2.4 F3.2 F3.4 F7.2 F7.3 F9.3 F9.4 F10.2 F10.4 F13.1 F15.4 F16.3 F18.2 F18.4 F22.2 F23.2 F23.4;
* facet = MEAN.3(four items) x 4 (4-20); overall facet = MEAN.3(G1-G4) x 4;
* domains = mean of facet scores, with the negatively framed facets reversed (24 - facet):
  PHYS = MEAN.2(24-pain, energy, sleep); PSYCH = MEAN.4(pfeel, think, esteem, body, 24-neg);
  IND = MEAN.3(mobil, activ, 24-medic, work); SOCIAL = MEAN.2(relat, supp, sexx);
  ENVIR = MEAN.6(eight facets); SRPB = spirituality facet (F24);
* cases with fewer than 80 valid items are deleted.
WHOQOL-HIV: UFRGS WHOQOL-HIV manual and syntax (facets F50-F54 added to domains I, IV and VI).
WHOQOL-SRPB: WHO SRPB scoring - domain VI = mean of F24 and the eight SRPB facets.
"""

from __future__ import annotations

from dataclasses import replace

from .base import Domain, Instrument, LanguageVersion
from .item_texts import HIV120_PT, SRPB_PT, WHOQOL100_EN, WHOQOL100_PT
from .whoqol_bref import WHOQOL_BREF
from .whoqol_srpb import SRPB_CODES, SRPB_EN, SRPB_GROUP_2006, SRPB_ITEMS, SRPB_VERSIONS, srpb_facets

# number, key, pt, en
FACETS = (
    (1, "pain", "Dor e desconforto", "Pain and discomfort"),
    (2, "energy", "Energia e fadiga", "Energy and fatigue"),
    (3, "sleep", "Sono e descanso", "Sleep and rest"),
    (4, "positive_feelings", "Sentimentos positivos", "Positive feelings"),
    (5, "cognition", "Pensamento, aprendizagem, memória e concentração",
     "Thinking, learning, memory and concentration"),
    (6, "self_esteem", "Autoestima", "Self-esteem"),
    (7, "body_image", "Imagem corporal e aparência", "Bodily image and appearance"),
    (8, "negative_feelings", "Sentimentos negativos", "Negative feelings"),
    (9, "mobility", "Mobilidade", "Mobility"),
    (10, "daily_activities", "Atividades da vida diária", "Activities of daily living"),
    (11, "medication", "Dependência de medicação ou de tratamentos", "Dependence on medication or treatments"),
    (12, "work_capacity", "Aptidão para o trabalho", "Work capacity"),
    (13, "personal_relationships", "Relacionamentos pessoais", "Personal relationships"),
    (14, "social_support", "Apoio social", "Social support"),
    (15, "sexual_activity", "Atividade sexual", "Sexual activity"),
    (16, "safety", "Segurança física", "Physical safety and security"),
    (17, "home", "Moradia", "Home environment"),
    (18, "finances", "Finanças", "Financial resources"),
    (19, "health_care", "Cuidados de saúde e assistência social", "Health and social care: accessibility and quality"),
    (20, "information", "Informação e novas habilidades", "Opportunities for acquiring new information and skills"),
    (21, "leisure", "Lazer", "Participation in and opportunities for recreation/leisure activities"),
    (22, "physical_environment", "Ambiente físico (poluição, barulho, trânsito, clima)",
     "Physical environment (pollution/noise/traffic/climate)"),
    (23, "transport", "Transporte", "Transport"),
    (24, "srpb_facet", "Espiritualidade/religião/crenças pessoais (faceta F24)",
     "Spirituality/religion/personal beliefs (facet F24)"),
)
HIV_FACETS = (
    (50, "hiv_symptoms", "Sintomas de PVHA", "Symptoms of PLWHA"),
    (51, "social_inclusion", "Inclusão social", "Social inclusion"),
    (52, "forgiveness_blame", "Perdão e culpa", "Forgiveness and blame"),
    (53, "future_concerns", "Preocupações sobre o futuro", "Concerns about the future"),
    (54, "death_dying", "Morte e morrer", "Death and dying"),
)
REVERSED_100 = ("F2.2", "F2.4", "F3.2", "F3.4", "F7.2", "F7.3", "F9.3", "F9.4", "F10.2", "F10.4", "F13.1", "F15.4",
                "F16.3", "F18.2", "F18.4", "F22.2", "F23.2", "F23.4")
GENERAL = ("G1", "G2", "G3", "G4")


def _items(n: int) -> tuple[str, ...]:
    return tuple(f"F{n}.{i}" for i in range(1, 5))


def _facets(table) -> dict[str, Domain]:
    return {key: Domain(key, _items(n), 3, {"pt": pt, "en": en}, role="facet") for n, key, pt, en in table}


OVERALL = Domain("overall_facet", GENERAL, 3,
                 {"pt": "Qualidade de vida geral e percepção geral de saúde",
                  "en": "Overall quality of life and general health perceptions",
                  "es": "Calidad de vida global y percepción general de salud"}, role="global")

LABELS = {
    "physical": {"pt": "Físico", "en": "Physical", "es": "Físico"},
    "psychological": {"pt": "Psicológico", "en": "Psychological", "es": "Psicológico"},
    "independence": {"pt": "Nível de independência", "en": "Level of independence", "es": "Nivel de independencia"},
    "social": {"pt": "Relações sociais", "en": "Social relationships", "es": "Relaciones sociales"},
    "environment": {"pt": "Meio ambiente", "en": "Environment", "es": "Ambiente"},
    "spirituality": {"pt": "Espiritualidade/religião/crenças pessoais", "en": "Spirituality/religion/personal beliefs",
                     "es": "Espiritualidad/religión/creencias personales"},
}


def _dom(key, facets, min_valid, reversed_facets=()):
    return Domain(key, (), min_valid, LABELS[key], facets=tuple(facets), reversed_facets=tuple(reversed_facets))


ENV = ("safety", "home", "finances", "health_care", "information", "leisure", "physical_environment", "transport")


def _codes(items) -> dict[str, tuple[str, ...]]:
    """SPSS-style names of the manual (F11 = F1.1, F244 = F24.4, F504 = F50.4)."""
    return {it: (it.replace(".", ""),) for it in items if it.startswith("F")}


WHO_MANUAL = ("World Health Organization. WHOQOL user manual. Programme on Mental Health. Geneva: WHO; 1998 "
              "(WHO/MNH/MHP/98.4.Rev.1).")
WHOQOL_GROUP_1998 = ("The WHOQOL Group. The World Health Organization quality of life assessment (WHOQOL): development "
                     "and general psychometric properties. Soc Sci Med. 1998;46(12):1569-1585.")
FLECK_1999 = LanguageVersion(
    "pt-BR", "pt", "Fleck et al., 1999",
    "Fleck MPA, Louzada S, Xavier M, Chachamovich E, Vieira G, Santos L, et al. Aplicação da versão em português do "
    "instrumento de avaliação de qualidade de vida da Organização Mundial da Saúde (WHOQOL-100). Rev Saúde Pública. "
    "1999;33(2):198-205.",
    {"pt": "versão validada para o português brasileiro (Fleck et al., 1999)",
     "en": "validated Brazilian Portuguese version (Fleck et al., 1999)",
     "es": "versión validada al portugués de Brasil (Fleck et al., 1999)"})
ENGLISH_100 = LanguageVersion(
    "en", "en", "The WHOQOL Group, 1998", WHOQOL_GROUP_1998,
    {"pt": "versão genérica em inglês (The WHOQOL Group, 1998)", "en": "generic English version (The WHOQOL Group, 1998)",
     "es": "versión genérica en inglés (The WHOQOL Group, 1998)"})
NUMBER_NOTE = ("question numbers follow the order of the Brazilian form (UFRGS), which is grouped by response scale, "
               "not by facet; check them against the form used, or use the facet codes (F1.1 ... F24.4, G1-G4) as "
               "headers.")
FACET_100 = _facets(FACETS)

# ------------------------------------------------------------------ WHOQOL-100
ITEMS_100 = tuple(it for n, *_ in FACETS for it in _items(n)) + GENERAL

WHOQOL_100 = Instrument(
    key="whoqol-100",
    name="WHOQOL-100",
    items=ITEMS_100,
    reversed_items=REVERSED_100,
    domains={
        **FACET_100,
        "physical": _dom("physical", ("pain", "energy", "sleep"), 2, ("pain",)),
        "psychological": _dom("psychological", ("positive_feelings", "cognition", "self_esteem", "body_image",
                                                "negative_feelings"), 4, ("negative_feelings",)),
        "independence": _dom("independence", ("mobility", "daily_activities", "medication", "work_capacity"), 3,
                             ("medication",)),
        "social": _dom("social", ("personal_relationships", "social_support", "sexual_activity"), 2),
        "environment": _dom("environment", ENV, 6),
        "spirituality": _dom("spirituality", ("srpb_facet",), 1),
        "overall_facet": OVERALL,
    },
    min_valid_total=80,
    item_text={"pt": dict(WHOQOL100_PT), "en": dict(WHOQOL100_EN)},
    item_short={},
    item_patterns={},
    item_codes=_codes(ITEMS_100),
    number_map={n: it for n, it in enumerate(WHOQOL100_PT, 1)},
    number_note=NUMBER_NOTE,
    versions=(FLECK_1999, ENGLISH_100),
    primary_reference=WHO_MANUAL,
    scoring_source="WHOQOL User Manual (WHO/MNH/MHP/98.4.Rev.1), Appendix 9 SPSS syntax.",
    description={
        "pt": ("O WHOQOL-100 é o instrumento completo de avaliação de qualidade de vida da OMS, com 100 itens "
               "respondidos em escalas de cinco pontos: 24 facetas específicas e uma faceta geral de quatro itens, "
               "agrupadas em seis domínios (físico, psicológico, nível de independência, relações sociais, meio "
               "ambiente e espiritualidade/religião/crenças pessoais) (The WHOQOL Group, 1998)"),
        "en": ("The WHOQOL-100 is the full WHO quality-of-life assessment, with 100 items answered on five-point scales: "
               "24 specific facets and one general facet of four items each, grouped into six domains (physical, "
               "psychological, level of independence, social relationships, environment and "
               "spirituality/religion/personal beliefs) (The WHOQOL Group, 1998)"),
        "es": ("El WHOQOL-100 es el instrumento completo de evaluación de la calidad de vida de la OMS, con 100 ítems "
               "respondidos en escalas de cinco puntos: 24 facetas específicas y una faceta general de cuatro ítems, "
               "agrupadas en seis dominios (físico, psicológico, nivel de independencia, relaciones sociales, ambiente "
               "y espiritualidad/religión/creencias personales) (The WHOQOL Group, 1998)"),
    },
    references=(WHOQOL_GROUP_1998,
                "Fleck MPA, Leal OF, Louzada S, Xavier M, Chachamovich E, Vieira G, et al. Desenvolvimento da versão em "
                "português do instrumento de avaliação de qualidade de vida da OMS (WHOQOL-100). Rev Bras Psiquiatr. "
                "1999;21(1):19-28."),
    notes=(
        "Facet scores (pain, negative feelings, dependence on medication) are in the direction of the facet, as in "
        "the manual: higher = more pain, more negative feelings, more dependence. They are reversed (24 - facet) "
        "only inside the domain scores. For reliability, multitrait scaling and the lavaan export their items are "
        "reversed so that every item points to better QoL.",
        "Missing data follow the syntax (MEAN.3 per facet; MEAN.2/4/3/2/6 per domain; at least 80 valid items). The "
        "manual's prose allows up to two missing items per facet; the syntax, used here, allows one.",
        "The manual does not recommend a total score summing all items; none is computed.",
        "Four-domain (WHOQOL-BREF) scores from WHOQOL-100 data: use the key whoqol-100-bref (manual Appendix 8).",
        "CFA: above 60 items the Python CFA is fitted at facet level (facet scores, negative facets reversed, as "
        "indicators of the domains with two or more facets); the generated lavaan script fits the item-level "
        "second-order model (WLSMV).",
    ),
)

# ------------------------------------------------------------------ WHOQOL-HIV
FACET_HIV = {**FACET_100, **_facets(HIV_FACETS)}
ITEMS_HIV = ITEMS_100[:-4] + tuple(it for n, *_ in HIV_FACETS for it in _items(n)) + GENERAL

_CONVENTION_100 = {
    "pt": ("Como a sintaxe do {name} não define regra para dados ausentes, adotaram-se as do WHOQOL-100: um item "
           "ausente por faceta, uma faceta ausente por domínio ({extra}) e exclusão de questionários com mais de 20% "
           "dos itens ausentes."),
    "en": ("As the {name} syntax defines no missing-data rule, the WHOQOL-100 rules were adopted: one missing item per "
           "facet, one missing facet per domain ({extra}) and exclusion of questionnaires with more than 20% of the "
           "items missing."),
    "es": ("Como la sintaxis del {name} no define una regla para datos faltantes, se adoptaron las del WHOQOL-100: un "
           "ítem faltante por faceta, una faceta faltante por dominio ({extra}) y exclusión de los cuestionarios con "
           "más del 20% de los ítems faltantes."),
}
_EXTRA_HIV = {"pt": "duas no domínio meio ambiente", "en": "two in the environment domain",
              "es": "dos en el dominio ambiente"}

WHOQOL_HIV = Instrument(
    key="whoqol-hiv",
    name="WHOQOL-HIV",
    items=ITEMS_HIV,
    reversed_items=REVERSED_100 + ("F51.2", "F51.4"),
    domains={
        **FACET_HIV,
        "physical": _dom("physical", ("pain", "energy", "sleep", "hiv_symptoms"), 3, ("pain", "hiv_symptoms")),
        "psychological": _dom("psychological", ("positive_feelings", "cognition", "self_esteem", "body_image",
                                                "negative_feelings"), 4, ("negative_feelings",)),
        "independence": _dom("independence", ("mobility", "daily_activities", "medication", "work_capacity"), 3,
                             ("medication",)),
        "social": _dom("social", ("personal_relationships", "social_support", "sexual_activity", "social_inclusion"),
                       3),
        "environment": _dom("environment", ENV, 6),
        "spirituality": _dom("spirituality", ("srpb_facet", "forgiveness_blame", "future_concerns", "death_dying"), 3,
                             ("forgiveness_blame", "future_concerns", "death_dying")),
        "overall_facet": OVERALL,
    },
    min_valid_total=96,
    item_text={"pt": dict(HIV120_PT), "en": dict(WHOQOL100_EN)},
    item_short={},
    item_patterns={},
    item_codes=_codes(ITEMS_HIV),
    number_map={n: it for n, it in enumerate(HIV120_PT, 1)},
    number_note=NUMBER_NOTE.replace("F24.4, G1-G4", "F24.4, F50.1 ... F54.4, G1-G4"),
    versions=(
        LanguageVersion(
            "pt-BR", "pt", "Zimpel & Fleck, 2007",
            "Zimpel RR, Fleck MP. Quality of life in HIV-positive Brazilians: application and validation of the "
            "WHOQOL-HIV, Brazilian version. AIDS Care. 2007;19(7):923-930.",
            {"pt": "versão brasileira (Zimpel & Fleck, 2007)", "en": "Brazilian version (Zimpel & Fleck, 2007)",
             "es": "versión brasileña (Zimpel & Fleck, 2007)"}),
        LanguageVersion(
            "en", "en", "WHOQOL HIV Group, 2004",
            "WHOQOL HIV Group. WHOQOL-HIV for quality of life assessment among people living with HIV and AIDS: "
            "results from the field test. AIDS Care. 2004;16(7):882-889.",
            {"pt": "versão internacional (WHOQOL HIV Group, 2004)", "en": "international version (WHOQOL HIV Group, 2004)",
             "es": "versión internacional (WHOQOL HIV Group, 2004)"}),
    ),
    primary_reference=("WHOQOL HIV Group. WHOQOL-HIV for quality of life assessment among people living with HIV and "
                       "AIDS: results from the field test. AIDS Care. 2004;16(7):882-889."),
    scoring_source="WHOQOL-HIV manual and syntax distributed by the UFRGS WHOQOL group, with the WHOQOL-100 rules.",
    description={
        "pt": ("O WHOQOL-HIV é a versão do WHOQOL-100 para pessoas vivendo com HIV, com 120 itens respondidos em "
               "escalas de cinco pontos: as 25 facetas do WHOQOL-100 e cinco facetas específicas (sintomas, inclusão "
               "social, perdão e culpa, preocupações sobre o futuro, morte e morrer), agrupadas em seis domínios "
               "(WHOQOL HIV Group, 2004)"),
        "en": ("The WHOQOL-HIV is the version of the WHOQOL-100 for people living with HIV, with 120 items answered on "
               "five-point scales: the 25 WHOQOL-100 facets and five specific facets (symptoms, social inclusion, "
               "forgiveness and blame, concerns about the future, death and dying), grouped into six domains (WHOQOL "
               "HIV Group, 2004)"),
        "es": ("El WHOQOL-HIV es la versión del WHOQOL-100 para personas que viven con VIH, con 120 ítems respondidos "
               "en escalas de cinco puntos: las 25 facetas del WHOQOL-100 y cinco facetas específicas (síntomas, "
               "inclusión social, perdón y culpa, preocupaciones sobre el futuro, muerte y morir), agrupadas en seis "
               "dominios (WHOQOL HIV Group, 2004)"),
    },
    references=(WHOQOL_GROUP_1998,),
    methods_note={k: v.format(name="WHOQOL-HIV", extra=_EXTRA_HIV[k]) for k, v in _CONVENTION_100.items()},
    notes=(
        "Reverse coding: the UFRGS syntax reverses every item of the negatively framed facets (F1, F8, F11, F50, "
        "F52, F53, F54) and averages plainly; the toolkit reverses those facets at domain level (24 - facet), as the "
        "WHOQOL-100 syntax does. The domain scores are identical; the facet scores keep the direction of the facet.",
        "F2.1 ('Do you have enough energy?') is NOT reversed: the UFRGS syntax lists it among the reversed items, "
        "a known error (the WHOQOL-100 and the WHOQOL-SRPB syntaxes do not reverse it in the WHOQOL-100).",
        "Missing data: the syntax computes facets and domains from all of their items and states no rule; the "
        "toolkit applies the WHOQOL-100 rules (MEAN.3 per facet; one missing facet per domain, two in the "
        "environment domain; at least 96 of 120 valid items). With complete data the domains equal the official "
        "ones; the methods text states the convention.",
        "CFA: above 60 items the Python CFA is fitted at facet level (facet scores, negative facets reversed, as "
        "indicators of the domains with two or more facets); the generated lavaan script fits the item-level "
        "second-order model (WLSMV).",
    ),
)

# ------------------------------------------------------------- WHOQOL-100 + SRPB
SRPB_FACETS = srpb_facets(role="facet")
ITEMS_100_SRPB = ITEMS_100 + SRPB_ITEMS

WHOQOL_100_SRPB = Instrument(
    key="whoqol-100-srpb",
    name="WHOQOL-100 + WHOQOL-SRPB",
    items=ITEMS_100_SRPB,
    reversed_items=REVERSED_100,
    domains={
        **FACET_100, **SRPB_FACETS,
        **{k: d for k, d in WHOQOL_100.domains.items() if d.composite and k != "spirituality"},
        "spirituality": _dom("spirituality", ("srpb_facet", *SRPB_FACETS), 7),
        "overall_facet": OVERALL,
    },
    min_valid_total=106,
    item_text={"pt": {**WHOQOL100_PT, **SRPB_PT}, "en": {**WHOQOL100_EN, **SRPB_EN}},
    item_short={},
    item_patterns={},
    item_codes={**_codes(ITEMS_100), **SRPB_CODES},
    number_map={},
    versions=(
        LanguageVersion(SRPB_VERSIONS[0].code, "pt", SRPB_VERSIONS[0].citation, SRPB_VERSIONS[0].reference,
                        SRPB_VERSIONS[0].description),
        SRPB_VERSIONS[1],
    ),
    primary_reference=SRPB_GROUP_2006,
    scoring_source="WHOQOL-SRPB scoring instructions (WHO SRPB Group) with the WHOQOL-100 Appendix 9 syntax.",
    description={
        "pt": ("O WHOQOL-SRPB, aplicado com o WHOQOL-100 (132 itens), amplia o domínio de espiritualidade, "
               "religiosidade e crenças pessoais com oito facetas de quatro itens (conexão espiritual, sentido na "
               "vida, admiração, totalidade e integração, força espiritual, paz interior, esperança e otimismo, fé) "
               "(WHOQOL SRPB Group, 2006)"),
        "en": ("The WHOQOL-SRPB, administered with the WHOQOL-100 (132 items), extends the spirituality, religion and "
               "personal beliefs domain with eight four-item facets (spiritual connection, meaning and purpose, awe, "
               "wholeness and integration, spiritual strength, inner peace, hope and optimism, faith) (WHOQOL SRPB "
               "Group, 2006)"),
        "es": ("El WHOQOL-SRPB, aplicado con el WHOQOL-100 (132 ítems), amplía el dominio de espiritualidad, "
               "religiosidad y creencias personales con ocho facetas de cuatro ítems (conexión espiritual, sentido de "
               "la vida, asombro, totalidad e integración, fuerza espiritual, paz interior, esperanza y optimismo, fe) "
               "(WHOQOL SRPB Group, 2006)"),
    },
    references=(WHO_MANUAL, WHOQOL_GROUP_1998),
    methods_note={
        "pt": ("O domínio de espiritualidade correspondeu à média da faceta F24 do WHOQOL-100 e das oito facetas do "
               "WHOQOL-SRPB (mínimo de sete facetas válidas, convenção análoga à do domínio meio ambiente); foram "
               "excluídos questionários com mais de 20% dos 132 itens ausentes."),
        "en": ("The spirituality domain was the mean of WHOQOL-100 facet F24 and the eight WHOQOL-SRPB facets (at least "
               "seven valid facets, a convention analogous to the environment domain); questionnaires with more than "
               "20% of the 132 items missing were excluded."),
        "es": ("El dominio de espiritualidad correspondió a la media de la faceta F24 del WHOQOL-100 y de las ocho "
               "facetas del WHOQOL-SRPB (mínimo de siete facetas válidas, convención análoga a la del dominio "
               "ambiente); se excluyeron los cuestionarios con más del 20% de los 132 ítems faltantes."),
    },
    notes=(
        "The SRPB scoring text reverses 31 items and averages plainly. Its list includes F1.1-F1.4, F8.1-F8.4 and "
        "F11.1-F11.4 (equivalent to reversing those facets at domain level, as done here) and F2.1, an error that "
        "the WHOQOL-100 syntax does not contain; F2.1 is not reversed.",
        "Missing data: WHOQOL-100 syntax for facets and the five first domains; domain VI needs 7 of its 9 facets "
        "(toolkit convention, the SRPB text gives no rule); at least 106 of 132 valid items (80%).",
        "Headers must be item codes (F1.1 ... F24.4, G1-G4, SP1.1 ... SP8.4): question numbers are not mapped, "
        "since the order of the combined forms varies.",
        "CFA: above 60 items the Python CFA is fitted at facet level (facet scores, negative facets reversed, as "
        "indicators of the domains with two or more facets); the generated lavaan script fits the item-level "
        "second-order model (WLSMV).",
    ),
)


# ------------------------------------------------- WHOQOL-BREF four-domain scores from WHOQOL-100 data
# WHOQOL User Manual, Appendix 8 (generic WHOQOL-BREF, with the WHOQOL-100 code of each question) and chapter 5
# ("Four domain solutions for the WHOQOL-100 have been derived here for comparison purposes only").
BREF_FROM_100 = {"Q1": "G1", "Q2": "G4", "Q3": "F1.4", "Q4": "F11.3", "Q5": "F4.1", "Q6": "F24.2", "Q7": "F5.3",
                 "Q8": "F16.1", "Q9": "F22.1", "Q10": "F2.1", "Q11": "F7.1", "Q12": "F18.1", "Q13": "F20.1",
                 "Q14": "F21.1", "Q15": "F9.1", "Q16": "F3.3", "Q17": "F10.3", "Q18": "F12.4", "Q19": "F6.3",
                 "Q20": "F13.3", "Q21": "F15.3", "Q22": "F14.4", "Q23": "F17.3", "Q24": "F19.3", "Q25": "F23.3",
                 "Q26": "F8.1"}

WHOQOL_100_BREF = replace(
    WHOQOL_BREF,
    key="whoqol-100-bref",
    name="WHOQOL-BREF (four domains) from WHOQOL-100 data",
    derived_from=("whoqol-100", BREF_FROM_100),
    versions=(FLECK_1999, ENGLISH_100),
    primary_reference=WHO_MANUAL,
    description={
        "pt": ("Os escores do WHOQOL-BREF (quatro domínios: físico, psicológico, relações sociais e meio ambiente, além "
               "das questões gerais 1 e 2) podem ser calculados a partir do WHOQOL-100, que contém as 26 questões do "
               "WHOQOL-BREF (The WHOQOL Group, 1998)"),
        "en": ("WHOQOL-BREF scores (four domains: physical, psychological, social relationships and environment, plus "
               "general questions 1 and 2) can be computed from the WHOQOL-100, which contains the 26 WHOQOL-BREF "
               "questions (The WHOQOL Group, 1998)"),
        "es": ("Las puntuaciones del WHOQOL-BREF (cuatro dominios: físico, psicológico, relaciones sociales y ambiente, "
               "además de las preguntas generales 1 y 2) pueden calcularse a partir del WHOQOL-100, que contiene las 26 "
               "preguntas del WHOQOL-BREF (The WHOQOL Group, 1998)"),
    },
    references=(WHOQOL_GROUP_1998,),
    scoring_source=("WHOQOL User Manual (WHO/MNH/MHP/98.4.Rev.1): Appendix 8 (WHOQOL-100 code of each WHOQOL-BREF "
                    "question) and Appendix 10 (WHOQOL-BREF syntax)."),
    methods_note={
        "pt": ("Os quatro domínios do WHOQOL-BREF foram calculados a partir dos 26 itens correspondentes do WHOQOL-100 "
               "(códigos do manual da OMS, apêndice 8), com as regras de pontuação do WHOQOL-BREF; o manual usa essa "
               "solução de quatro domínios para comparação, e a estrutura oficial do WHOQOL-100 é a de seis domínios."),
        "en": ("The four WHOQOL-BREF domains were computed from the 26 corresponding WHOQOL-100 items (codes in the WHO "
               "manual, Appendix 8) with the WHOQOL-BREF scoring rules; the manual uses this four-domain solution for "
               "comparison, the official WHOQOL-100 structure being the six-domain one."),
        "es": ("Los cuatro dominios del WHOQOL-BREF se calcularon a partir de los 26 ítems correspondientes del "
               "WHOQOL-100 (códigos del manual de la OMS, apéndice 8), con las reglas de puntuación del WHOQOL-BREF; el "
               "manual usa esta solución de cuatro dominios para comparación, y la estructura oficial del WHOQOL-100 es "
               "la de seis dominios."),
    },
    notes=(
        "Four-domain scoring of WHOQOL-100 (or WHOQOL-HIV, which contains every WHOQOL-100 item) data: the 26 "
        "WHOQOL-BREF questions are taken from their WHOQOL-100 columns (manual Appendix 8) and scored with the "
        "WHOQOL-BREF rules. The manual keeps the six-domain structure as the WHOQOL-100's own and derives four-domain "
        "scores 'for comparison purposes only'; use it to compare with WHOQOL-BREF studies.",
        "The sheet must hold the WHOQOL-100 (at least 80 of its items detected); otherwise the columns are read as a "
        "WHOQOL-BREF.",
    ),
)
