"""WHOQOL-BREF + WHOQOL-DIS disabilities module, physical (PD) and intellectual (ID) disability versions.

Source: The WHOQOL-DISABILITIES module - manual (WHO, August 2011; M. Power for the WHOQOL-DIS Group):
* Q27 (27G, "Does your disability have a negative effect on your day-to-day life?") is scored alone, reversed;
* module items Q28-Q39 (dis_02-dis_13): discrimination Q28-Q30 (reversed), autonomy Q31-Q33, inclusion Q34-Q39;
  facet raw score = sum of its items (all items required, PD 3-15/6-30, ID 3-9/6-18);
  total = MEAN.10(12 items) x 12 (PD 12-60, ID 12-36);
* ID version: all items on 3-point scales except Q1, Q2 and Q27 (5-point); reversal 1=3, 3=1.
WHOQOL-BREF domains follow the WHOQOL-BREF manual. Wording: manual Appendix 1 (English) and UFRGS forms (pt-BR).
Brazilian forms (``-br`` keys and the proxy version): national items Q40-Q43 scored as in the UFRGS syntax,
domDIS_nac = MEAN.3(q40 q41 q42 q43) x 4. Proxy version: UFRGS form "WHOQOL-BREF-ID e Módulo Incapacidades (Versão por
Representante)", field test version 31/01/08, every item on a five-point scale.
"""

from __future__ import annotations

from dataclasses import replace

from .base import Domain, Instrument, LanguageVersion
from .item_texts import DIS_ID_PROXY_PT
from .whoqol_bref import DOMAINS as BREF_DOMAINS
from .whoqol_bref import ITEM_PATTERNS as BREF_PATTERNS
from .whoqol_bref import ITEM_SHORT as BREF_SHORT
from .whoqol_bref import ITEM_TEXT as BREF_TEXT
from .whoqol_bref import ITEMS as BREF_ITEMS

MODULE = tuple(f"Q{n}" for n in range(27, 40))
ITEMS = BREF_ITEMS + MODULE

DIS_PT = {
    "Q27": "Sua incapacidade (deficiência/limitação) tem um efeito negativo (ruim) em sua vida diária?",
    "Q28": "Você sente que algumas pessoas tratam você de forma injusta?",
    "Q29": "Você precisa de que alguém “tome seu partido” quando tem problemas?",
    "Q30": "Você se preocupa com o que poderia acontecer com você no futuro?",
    "Q31": "Você se sente no controle da sua vida?",
    "Q32": "Você faz suas próprias escolhas sobre sua vida no dia-a-dia?",
    "Q33": "Você toma as grandes decisões na sua vida?",
    "Q34": "Você está satisfeito(a) com sua habilidade para se comunicar com outras pessoas?",
    "Q35": "Você sente que as outras pessoas aceitam você?",
    "Q36": "Você sente que as outras pessoas respeitam você?",
    "Q37": "Você está satisfeito(a) com suas chances de se envolver em atividades sociais?",
    "Q38": "Você está satisfeito(a) com suas chances para se envolver nas atividades de sua comunidade (locais)?",
    "Q39": "Você sente que seus sonhos, expectativas e desejos irão se realizar?",
}
DIS_EN = {
    "Q27": "Does your disability have a negative (bad) effect on your day-to-day life?",
    "Q28": "Do you feel that some people treat you unfairly?",
    "Q29": "Do you need someone to stand up for you when you have problems?",
    "Q30": "Do you worry about what might happen to you in the future?",
    "Q31": "Do you feel in control of your life?",
    "Q32": "Do you make your own choices about your day-to-day life?",
    "Q33": "Do you get to make the big decisions in your life?",
    "Q34": "Are you satisfied with your ability to communicate with other people?",
    "Q35": "Do you feel that other people accept you?",
    "Q36": "Do you feel that other people respect you?",
    "Q37": "Are you satisfied with your chances to be involved in social activities?",
    "Q38": "Are you satisfied with your chances to be involved in local activities?",
    "Q39": "Do you feel that your dreams, hopes and wishes will happen?",
}
DIS_SHORT_EN = {  # item labels of the manual's descriptive tables
    "Q27": "Impact of disability", "Q28": "Discrimination", "Q29": "Advocacy", "Q30": "Future prospects",
    "Q31": "Control", "Q32": "Choice", "Q33": "Autonomy", "Q34": "Communication ability", "Q35": "Social acceptance",
    "Q36": "Respect", "Q37": "Interaction", "Q38": "Contribution", "Q39": "Personal potential",
}
CODES = {f"Q{n}": (f"dis_{n - 26:02d}",) for n in range(27, 40)}


def _module() -> dict[str, Domain]:
    def q(*ns):
        return tuple(f"Q{n}" for n in ns)
    return {
        "disability_impact": Domain("disability_impact", ("Q27",), 1,
                                    {"pt": "Impacto da incapacidade (Q27)", "en": "Impact of disability (Q27)"},
                                    role="global", multiplier=4),
        "dis_discrimination": Domain("dis_discrimination", q(28, 29, 30), 3,
                                     {"pt": "Discriminação", "en": "Discrimination"}, multiplier=3),
        "dis_autonomy": Domain("dis_autonomy", q(31, 32, 33), 3, {"pt": "Autonomia", "en": "Autonomy"}, multiplier=3),
        "dis_inclusion": Domain("dis_inclusion", q(34, 35, 36, 37, 38, 39), 6, {"pt": "Inclusão", "en": "Inclusion"},
                                multiplier=6),
        "dis_total": Domain("dis_total", q(*range(28, 40)), 10,
                            {"pt": "Escore total do módulo DIS", "en": "WHOQOL-DIS module total score"},
                            role="total", multiplier=12),
    }


def _domains() -> dict[str, Domain]:
    return {**{k: d for k, d in BREF_DOMAINS.items() if k != "overall"}, "overall": BREF_DOMAINS["overall"],
            **_module()}


TEXT = {"pt": {**BREF_TEXT["pt"], **DIS_PT}, "en": {**BREF_TEXT["en"], **DIS_EN}, "es": dict(BREF_TEXT["es"])}
SHORT = {**BREF_SHORT, "en": {**BREF_SHORT["en"], **DIS_SHORT_EN}}

VERSIONS = (
    LanguageVersion(
        "pt-BR", "pt", "Bredemeier et al., 2014",
        "Bredemeier J, Wagner GP, Agranonik M, Perez TS, Fleck MP. The World Health Organization Quality of Life "
        "instrument for people with intellectual and physical disabilities (WHOQOL-Dis): evidence of validity of the "
        "Brazilian version. BMC Public Health. 2014;14:538.",
        {"pt": "versão brasileira (Bredemeier et al., 2014)", "en": "Brazilian version (Bredemeier et al., 2014)",
         "es": "versión brasileña (Bredemeier et al., 2014)"}),
)
POWER_2010 = ("Power MJ, Green AM; WHOQOL-DIS Group. Development of the WHOQOL disabilities module. Qual Life Res. "
              "2010;19(4):571-584. doi:10.1007/s11136-010-9616-6")
VERSIONS += (LanguageVersion("en", "en", "Power & Green, 2010", POWER_2010,
                             {"pt": "versão original em inglês (Power & Green, 2010)",
                              "en": "original English version (Power & Green, 2010)",
                              "es": "versión original en inglés (Power & Green, 2010)"}),)
MANUAL = ("Power M; WHOQOL-DIS Group. The WHOQOL-DISABILITIES module: manual. Geneva: World Health Organization; "
          "2011.")

_COMMON_NOTES = (
    "Module facets are sums of all their items (the manual's ranges hold 'provided all items of a facet have been "
    "completed'); the module total allows two missing items (MEAN.10 x 12, manual Appendix II).",
    "The UFRGS Portuguese syntax scores the module differently (facets as mean x 4 with MEAN.2/MEAN.2/MEAN.5, total "
    "as MEAN.11 x 4, and Q27 transformed as (Q27 - 1) x 100/16); the toolkit follows the WHO manual. National items "
    "Q40-Q43 of the Brazilian form are scored by the keys whoqol-dis-br and whoqol-dis-id-br.",
    "Questionnaire exclusion: no rule is given for the 39-item form; the toolkit keeps the WHOQOL-BREF proportion "
    "(80%: at least 32 of 39 valid items).",
    "Headers dis_01-dis_13 (manual variable names; dis_01 = Q27) are accepted.",
)
_METHODS_NOTE = {
    "pt": ("As facetas do módulo de incapacidades corresponderam à soma de seus itens (todos exigidos) e o escore total "
           "do módulo à média dos 12 itens multiplicada por 12 (mínimo de dez itens); foram excluídos questionários "
           "com mais de 20% dos 39 itens ausentes."),
    "en": ("Disabilities-module facets were the sum of their items (all required) and the module total the mean of the "
           "12 items multiplied by 12 (at least ten valid); questionnaires with more than 20% of the 39 items missing "
           "were excluded."),
    "es": ("Las facetas del módulo de discapacidades correspondieron a la suma de sus ítems (todos exigidos) y la "
           "puntuación total del módulo a la media de los 12 ítems multiplicada por 12 (mínimo de diez); se excluyeron "
           "los cuestionarios con más del 20% de los 39 ítems faltantes."),
}

WHOQOL_DIS = Instrument(
    key="whoqol-dis",
    name="WHOQOL-BREF + WHOQOL-DIS (physical disabilities)",
    items=ITEMS,
    reversed_items=("Q3", "Q4", "Q26", "Q27", "Q28", "Q29", "Q30"),
    domains=_domains(),
    min_valid_total=32,
    item_text=TEXT,
    item_short=SHORT,
    item_patterns=BREF_PATTERNS,
    item_codes=CODES,
    versions=VERSIONS,
    primary_reference=MANUAL,
    scoring_source="The WHOQOL-DISABILITIES module manual (WHO, 2011), scoring list and Appendix II.",
    description={
        "pt": ("O WHOQOL-DIS é o módulo da OMS para pessoas com incapacidades, aplicado com o WHOQOL-BREF: um item "
               "geral sobre o impacto da incapacidade e 12 itens em três facetas (discriminação, autonomia e "
               "inclusão), respondidos, na versão para incapacidades físicas, em escalas de cinco pontos (Power & "
               "Green, 2010)"),
        "en": ("The WHOQOL-DIS is the WHO module for people with disabilities, administered with the WHOQOL-BREF: one "
               "general item on the impact of disability and 12 items in three facets (discrimination, autonomy and "
               "inclusion), answered, in the physical-disabilities version, on five-point scales (Power & Green, 2010)"),
        "es": ("El WHOQOL-DIS es el módulo de la OMS para personas con discapacidad, aplicado con el WHOQOL-BREF: un "
               "ítem general sobre el impacto de la discapacidad y 12 ítems en tres facetas (discriminación, autonomía "
               "e inclusión), respondidos, en la versión para discapacidades físicas, en escalas de cinco puntos "
               "(Power & Green, 2010)"),
    },
    references=(POWER_2010,),
    methods_note=_METHODS_NOTE,
    notes=_COMMON_NOTES,
)

WHOQOL_DIS_ID = replace(
    WHOQOL_DIS,
    key="whoqol-dis-id",
    name="WHOQOL-BREF-ID + WHOQOL-DIS (intellectual disabilities)",
    scale_max=3,
    item_scale={"Q1": 5, "Q2": 5, "Q27": 5},
    description={
        "pt": ("O WHOQOL-DIS é o módulo da OMS para pessoas com incapacidades, aplicado com o WHOQOL-BREF: um item "
               "geral sobre o impacto da incapacidade e 12 itens em três facetas (discriminação, autonomia e "
               "inclusão); na versão para incapacidades intelectuais, os itens são respondidos em escalas de três "
               "pontos, exceto os itens gerais 1, 2 e 27 (Power & Green, 2010)"),
        "en": ("The WHOQOL-DIS is the WHO module for people with disabilities, administered with the WHOQOL-BREF: one "
               "general item on the impact of disability and 12 items in three facets (discrimination, autonomy and "
               "inclusion); in the intellectual-disabilities version items are answered on three-point scales, except "
               "the general items 1, 2 and 27 (Power & Green, 2010)"),
        "es": ("El WHOQOL-DIS es el módulo de la OMS para personas con discapacidad, aplicado con el WHOQOL-BREF: un "
               "ítem general sobre el impacto de la discapacidad y 12 ítems en tres facetas (discriminación, autonomía "
               "e inclusión); en la versión para discapacidades intelectuales los ítems se responden en escalas de tres "
               "puntos, excepto los ítems generales 1, 2 y 27 (Power & Green, 2010)"),
    },
    methods_note={k: v + {"pt": " Na versão para incapacidades intelectuais (escalas de três pontos), os domínios do "
                                "WHOQOL-BREF foram calculados como média × 4 (amplitude 4–12) e transformados "
                                "linearmente para 0–100, regra análoga à do manual para as facetas do módulo.",
                          "en": " In the intellectual-disabilities version (three-point scales), WHOQOL-BREF domains "
                                "were computed as mean × 4 (range 4–12) and linearly transformed to 0–100, a rule "
                                "analogous to the manual's for the module facets.",
                          "es": " En la versión para discapacidades intelectuales (escalas de tres puntos), los "
                                "dominios del WHOQOL-BREF se calcularon como media × 4 (rango 4–12) y se transformaron "
                                "linealmente a 0–100, regla análoga a la del manual para las facetas del módulo."}[k]
                  for k, v in _METHODS_NOTE.items()},
    notes=_COMMON_NOTES + (
        "ID version: answers outside 1-3 (1-5 for Q1, Q2, Q27) are set to missing; reversed items use 4 - answer. "
        "Text anchors are not recoded on 3-point scales (enter the numbers 1-3).",
        "The manual gives 0-100 transformations for the module facets only (e.g. 16.7 x (RFS - 3)); WHOQOL-BREF "
        "domains on 3-point items are scored as mean x 4 (4-12) and transformed linearly to 0-100 by the same "
        "principle (toolkit convention, stated in the methods text).",
    ),
)


# ------------------------------------------------------------------ Brazilian forms: national items Q40-Q43
NATIONAL = ("Q40", "Q41", "Q42", "Q43")
NATIONAL_PT = {  # UFRGS forms DISQOL/WHOQOL-Dis_Incapacidade_Fisica_Auto-avaliacao.pdf and ..._Intelectual_...
    "Q40": "Você está satisfeito(a) com as oportunidades que você tem para trabalhar?",
    "Q41": "Você está satisfeito(a) com as adaptações de seu ambiente à sua limitação?",
    "Q42": "Você está satisfeito(a) com as oportunidades que você tem de estudar?",
    "Q43": "Você está satisfeito(a) com a sua alimentação?",
}
NATIONAL_DOMAIN = Domain("dis_national", NATIONAL, 3,
                         {"pt": "Itens nacionais (versão brasileira, Q40–Q43)",
                          "en": "National items (Brazilian version, Q40–Q43)",
                          "es": "Ítems nacionales (versión brasileña, Q40–Q43)"}, multiplier=4)
UFRGS_SYNTAX = "Sintaxe WHOQOL-DIS para SPSS (grupo WHOQOL-UFRGS): domDIS_nac = MEAN.3(q40 q41 q42 q43) x 4."
_NATIONAL_NOTES = (
    "National items Q40-Q43 (work, environmental adaptations, study, food) of the Brazilian forms are scored as in "
    "the UFRGS syntax: MEAN.3 x 4 (one missing item allowed; 4-20, or 4-12 on 3-point items). They are not part of "
    "the module total. Item 44 of the form (physical barriers) has no scoring rule in any source and is not scored.",
    "Questionnaire exclusion: at least 35 of the 43 items valid (80%, toolkit convention).",
)
_NATIONAL_METHODS = {
    "pt": (" Os itens nacionais da versão brasileira (Q40–Q43) formaram um escore próprio, média × 4 com no mínimo três "
           "itens válidos, conforme a sintaxe do grupo WHOQOL brasileiro (UFRGS); o item 44 não foi pontuado."),
    "en": (" The national items of the Brazilian version (Q40–Q43) formed a separate score, mean × 4 with at least three "
           "valid items, as in the syntax of the Brazilian WHOQOL group (UFRGS); item 44 was not scored."),
    "es": (" Los ítems nacionales de la versión brasileña (Q40–Q43) formaron una puntuación propia, media × 4 con al "
           "menos tres ítems válidos, según la sintaxis del grupo WHOQOL brasileño (UFRGS); el ítem 44 no se puntuó."),
}


def _brazilian(base: Instrument, key: str, name: str, text_pt: dict[str, str] | None = None, **kw) -> Instrument:
    doms = {k: d for k, d in base.domains.items() if k != "dis_total"}
    doms.update(dis_national=NATIONAL_DOMAIN, dis_total=base.domains["dis_total"])
    methods = {k: v.replace("39", "43") + _NATIONAL_METHODS[k] for k, v in base.methods_note.items()}
    text = {**base.item_text, "pt": text_pt or {**base.item_text["pt"], **NATIONAL_PT}}
    return replace(base, key=key, name=name, items=base.items + NATIONAL, domains=doms, min_valid_total=35,
                   item_text=text, methods_note=methods, scoring_source=base.scoring_source + " " + UFRGS_SYNTAX,
                   notes=tuple(n for n in base.notes if not n.startswith("Questionnaire exclusion"))
                   + _NATIONAL_NOTES, **kw)


WHOQOL_DIS_BR = _brazilian(WHOQOL_DIS, "whoqol-dis-br",
                           "WHOQOL-BREF + WHOQOL-DIS (physical disabilities), Brazilian form with national items")
WHOQOL_DIS_ID_BR = _brazilian(WHOQOL_DIS_ID, "whoqol-dis-id-br",
                              "WHOQOL-BREF-ID + WHOQOL-DIS (intellectual disabilities), Brazilian form with national "
                              "items")

# ------------------------------------------------------------------ proxy version (intellectual disabilities)
SCHMIDT_2010 = ("Schmidt S, Power M, Green A, Lucas-Carrasco R, Eser E, Dragomirecka E, Fleck M. Self and proxy rating "
                "of quality of life in adults with intellectual disabilities: results from the DISQOL study. Res Dev "
                "Disabil. 2010;31(5):1015-1026. doi:10.1016/j.ridd.2010.04.013")
_PROXY_METHODS = {
    "pt": ("O questionário foi respondido por um representante (familiar ou cuidador que conhece bem a pessoa) na "
           "versão por representante do WHOQOL-BREF-ID e do módulo de incapacidades (Schmidt et al., 2010), com todos "
           "os itens em escalas de cinco pontos; como o manual não traz regras próprias para essa versão, foram "
           "aplicadas as da versão de cinco pontos. "),
    "en": ("The questionnaire was answered by a proxy (a relative or carer who knows the person well) on the proxy "
           "version of the WHOQOL-BREF-ID and disabilities module (Schmidt et al., 2010), with every item on a "
           "five-point scale; as the manual gives no rules for this version, those of the five-point version were "
           "applied. "),
    "es": ("El cuestionario fue respondido por un representante (familiar o cuidador que conoce bien a la persona) en "
           "la versión por representante del WHOQOL-BREF-ID y del módulo de discapacidades (Schmidt et al., 2010), con "
           "todos los ítems en escalas de cinco puntos; como el manual no trae reglas propias para esta versión, se "
           "aplicaron las de la versión de cinco puntos. "),
}
_proxy = _brazilian(WHOQOL_DIS, "whoqol-dis-id-proxy",
                    "WHOQOL-BREF-ID + WHOQOL-DIS, proxy version (intellectual disabilities)", text_pt=DIS_ID_PROXY_PT)
WHOQOL_DIS_ID_PROXY = replace(
    _proxy,
    item_text={"pt": dict(DIS_ID_PROXY_PT)},
    item_short={},
    versions=(LanguageVersion("pt-BR", "pt", "Schmidt et al., 2010", SCHMIDT_2010,
                              {"pt": "versão brasileira por representante do estudo DISQOL (Schmidt et al., 2010)",
                               "en": "Brazilian proxy version of the DISQOL study (Schmidt et al., 2010)",
                               "es": "versión brasileña por representante del estudio DISQOL (Schmidt et al., "
                                     "2010)"}),),
    description={
        "pt": ("A versão por representante do WHOQOL-BREF-ID e do módulo WHOQOL-DIS é respondida por um familiar ou "
               "cuidador em nome da pessoa com incapacidade intelectual: os 26 itens do WHOQOL-BREF, o item sobre o "
               "impacto da incapacidade, 12 itens em três facetas (discriminação, autonomia e inclusão) e os itens "
               "nacionais brasileiros, todos em escalas de cinco pontos (Schmidt et al., 2010)"),
        "en": ("The proxy version of the WHOQOL-BREF-ID and WHOQOL-DIS module is answered by a relative or carer on "
               "behalf of the person with intellectual disability: the 26 WHOQOL-BREF items, the impact-of-disability "
               "item, 12 items in three facets (discrimination, autonomy and inclusion) and the Brazilian national "
               "items, all on five-point scales (Schmidt et al., 2010)"),
        "es": ("La versión por representante del WHOQOL-BREF-ID y del módulo WHOQOL-DIS la responde un familiar o "
               "cuidador en nombre de la persona con discapacidad intelectual: los 26 ítems del WHOQOL-BREF, el ítem "
               "sobre el impacto de la discapacidad, 12 ítems en tres facetas (discriminación, autonomía e inclusión) y "
               "los ítems nacionales brasileños, todos en escalas de cinco puntos (Schmidt et al., 2010)"),
    },
    references=(POWER_2010, SCHMIDT_2010),
    methods_note={k: _PROXY_METHODS[k] + v for k, v in _proxy.methods_note.items()},
    notes=_proxy.notes + (
        "Proxy form: third-person wording (\"Ele/ela ...\"), every item on a five-point scale. The WHO manual gives "
        "no separate scoring for proxy ratings; the five-point (physical disabilities) rules are applied (toolkit "
        "convention, stated in the methods text). Report proxy and self-report scores separately; do not pool them.",
    ),
)
