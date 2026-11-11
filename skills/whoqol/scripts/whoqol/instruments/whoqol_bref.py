"""WHOQOL-BREF (WHO, 1996; The WHOQOL Group, 1998).

Scoring follows the official SPSS syntax of the WHO manual (WHOQOL-BREF: introduction,
administration, scoring and generic version of the assessment, 1996): items 3, 4 and 26 reversed;
domain = mean x 4 with at least 6/7, 5/6, 2/3 and 6/8 valid items; questionnaire kept only with
>= 21 valid items.
"""

from __future__ import annotations

from .base import Domain, Instrument, LanguageVersion

ITEMS = tuple(f"Q{i}" for i in range(1, 27))

ITEM_TEXT = {
    "pt": {
        "Q1": "Como você avaliaria sua qualidade de vida?",
        "Q2": "Quão satisfeito(a) você está com a sua saúde?",
        "Q3": "Em que medida você acha que sua dor (física) impede você de fazer o que você precisa?",
        "Q4": "O quanto você precisa de algum tratamento médico para levar sua vida diária?",
        "Q5": "O quanto você aproveita a vida?",
        "Q6": "Em que medida você acha que a sua vida tem sentido?",
        "Q7": "O quanto você consegue se concentrar?",
        "Q8": "Quão seguro(a) você se sente em sua vida diária?",
        "Q9": "Quão saudável é o seu ambiente físico (clima, barulho, poluição, atrativos)?",
        "Q10": "Você tem energia suficiente para seu dia-a-dia?",
        "Q11": "Você é capaz de aceitar sua aparência física?",
        "Q12": "Você tem dinheiro suficiente para satisfazer suas necessidades?",
        "Q13": "Quão disponíveis para você estão as informações que precisa no seu dia-a-dia?",
        "Q14": "Em que medida você tem oportunidades de atividade de lazer?",
        "Q15": "Quão bem você é capaz de se locomover?",
        "Q16": "Quão satisfeito(a) você está com o seu sono?",
        "Q17": "Quão satisfeito(a) você está com sua capacidade de desempenhar as atividades do seu dia-a-dia?",
        "Q18": "Quão satisfeito(a) você está com sua capacidade para o trabalho?",
        "Q19": "Quão satisfeito(a) você está consigo mesmo?",
        "Q20": "Quão satisfeito(a) você está com suas relações pessoais (amigos, parentes, conhecidos, colegas)?",
        "Q21": "Quão satisfeito(a) você está com sua vida sexual?",
        "Q22": "Quão satisfeito(a) você está com o apoio que você recebe de seus amigos?",
        "Q23": "Quão satisfeito(a) você está com as condições do local onde mora?",
        "Q24": "Quão satisfeito(a) você está com o seu acesso aos serviços de saúde?",
        "Q25": "Quão satisfeito(a) você está com o seu meio de transporte?",
        "Q26": "Com que frequência você tem sentimentos negativos tais como mau humor, desespero, ansiedade, depressão?",
    },
    "en": {
        "Q1": "How would you rate your quality of life?",
        "Q2": "How satisfied are you with your health?",
        "Q3": "To what extent do you feel that physical pain prevents you from doing what you need to do?",
        "Q4": "How much do you need any medical treatment to function in your daily life?",
        "Q5": "How much do you enjoy life?",
        "Q6": "To what extent do you feel your life to be meaningful?",
        "Q7": "How well are you able to concentrate?",
        "Q8": "How safe do you feel in your daily life?",
        "Q9": "How healthy is your physical environment?",
        "Q10": "Do you have enough energy for everyday life?",
        "Q11": "Are you able to accept your bodily appearance?",
        "Q12": "Have you enough money to meet your needs?",
        "Q13": "How available to you is the information that you need in your day-to-day life?",
        "Q14": "To what extent do you have the opportunity for leisure activities?",
        "Q15": "How well are you able to get around?",
        "Q16": "How satisfied are you with your sleep?",
        "Q17": "How satisfied are you with your ability to perform your daily living activities?",
        "Q18": "How satisfied are you with your capacity for work?",
        "Q19": "How satisfied are you with yourself?",
        "Q20": "How satisfied are you with your personal relationships?",
        "Q21": "How satisfied are you with your sex life?",
        "Q22": "How satisfied are you with the support you get from your friends?",
        "Q23": "How satisfied are you with the conditions of your living place?",
        "Q24": "How satisfied are you with your access to health services?",
        "Q25": "How satisfied are you with your transport?",
        "Q26": "How often do you have negative feelings such as blue mood, despair, anxiety, depression?",
    },
    "es": {
        "Q1": "¿Cómo puntuaría su calidad de vida?",
        "Q2": "¿Cuán satisfecho está con su salud?",
        "Q3": "¿Hasta qué punto piensa que el dolor (físico) le impide hacer lo que necesita?",
        "Q4": "¿Cuánto necesita de cualquier tratamiento médico para funcionar en su vida diaria?",
        "Q5": "¿Cuánto disfruta de la vida?",
        "Q6": "¿Hasta qué punto siente que su vida tiene sentido?",
        "Q7": "¿Cuál es su capacidad de concentración?",
        "Q8": "¿Cuánta seguridad siente en su vida diaria?",
        "Q9": "¿Cuán saludable es el ambiente físico a su alrededor?",
        "Q10": "¿Tiene energía suficiente para su vida diaria?",
        "Q11": "¿Es capaz de aceptar su apariencia física?",
        "Q12": "¿Tiene suficiente dinero para cubrir sus necesidades?",
        "Q13": "¿Qué disponible tiene la información que necesita en su vida diaria?",
        "Q14": "¿Hasta qué punto tiene oportunidad para realizar actividades de ocio?",
        "Q15": "¿Es capaz de desplazarse de un lugar a otro?",
        "Q16": "¿Cuán satisfecho está con su sueño?",
        "Q17": "¿Cuán satisfecho está con su habilidad para realizar sus actividades de la vida diaria?",
        "Q18": "¿Cuán satisfecho está con su capacidad de trabajo?",
        "Q19": "¿Cuán satisfecho está de sí mismo?",
        "Q20": "¿Cuán satisfecho está con sus relaciones personales?",
        "Q21": "¿Cuán satisfecho está con su vida sexual?",
        "Q22": "¿Cuán satisfecho está con el apoyo que obtiene de sus amigos?",
        "Q23": "¿Cuán satisfecho está de las condiciones del lugar donde vive?",
        "Q24": "¿Cuán satisfecho está con el acceso que tiene a los servicios sanitarios?",
        "Q25": "¿Cuán satisfecho está con su transporte?",
        "Q26": "¿Con qué frecuencia tiene sentimientos negativos, tales como tristeza, desesperanza, ansiedad, depresión?",
    },
}

ITEM_SHORT = {
    "pt": {
        "Q1": "QV geral", "Q2": "Satisfação com a saúde", "Q3": "Dor e desconforto (inv.)",
        "Q4": "Dependência de tratamento (inv.)", "Q5": "Aproveita a vida", "Q6": "Sentido da vida",
        "Q7": "Concentração", "Q8": "Segurança", "Q9": "Ambiente físico", "Q10": "Energia",
        "Q11": "Aparência", "Q12": "Recursos financeiros", "Q13": "Informações", "Q14": "Lazer",
        "Q15": "Mobilidade", "Q16": "Sono", "Q17": "Atividades diárias", "Q18": "Capacidade para o trabalho",
        "Q19": "Autoestima", "Q20": "Relações pessoais", "Q21": "Vida sexual", "Q22": "Apoio social",
        "Q23": "Moradia", "Q24": "Serviços de saúde", "Q25": "Transporte", "Q26": "Sentimentos negativos (inv.)",
    },
    "en": {
        "Q1": "Overall QoL", "Q2": "Satisfaction with health", "Q3": "Pain and discomfort (rev.)",
        "Q4": "Dependence on treatment (rev.)", "Q5": "Enjoy life", "Q6": "Meaningful life",
        "Q7": "Concentration", "Q8": "Safety", "Q9": "Physical environment", "Q10": "Energy",
        "Q11": "Bodily appearance", "Q12": "Financial resources", "Q13": "Information", "Q14": "Leisure",
        "Q15": "Mobility", "Q16": "Sleep", "Q17": "Activities of daily living", "Q18": "Work capacity",
        "Q19": "Self-esteem", "Q20": "Personal relationships", "Q21": "Sex life", "Q22": "Social support",
        "Q23": "Home environment", "Q24": "Health services", "Q25": "Transport", "Q26": "Negative feelings (rev.)",
    },
    "es": {
        "Q1": "CV global", "Q2": "Satisfacción con la salud", "Q3": "Dolor y malestar (inv.)",
        "Q4": "Dependencia de tratamiento (inv.)", "Q5": "Disfrute de la vida", "Q6": "Sentido de la vida",
        "Q7": "Concentración", "Q8": "Seguridad", "Q9": "Ambiente físico", "Q10": "Energía",
        "Q11": "Apariencia física", "Q12": "Recursos económicos", "Q13": "Información", "Q14": "Ocio",
        "Q15": "Movilidad", "Q16": "Sueño", "Q17": "Actividades diarias", "Q18": "Capacidad de trabajo",
        "Q19": "Autoestima", "Q20": "Relaciones personales", "Q21": "Vida sexual", "Q22": "Apoyo social",
        "Q23": "Vivienda", "Q24": "Servicios de salud", "Q25": "Transporte", "Q26": "Sentimientos negativos (inv.)",
    },
}

# Regexes over normalized text (lower case, no accents). Order within each list = priority.
ITEM_PATTERNS: dict[str, list[str]] = {
    "Q1": [r"avaliaria (a )?sua qualidade de vida", r"rate your quality of life",
           r"(puntuaria|calificaria|evaluaria|valoraria) su calidad de vida"],
    "Q2": [r"satisfeit.*com (a )?sua saude", r"satisfied are you with your health", r"satisfech.*con su salud"],
    "Q3": [r"\bdor\b", r"\bpain\b", r"\bdolor\b"],
    "Q4": [r"tratamento medico", r"medical treatment", r"tratamiento medico"],
    "Q5": [r"aproveita a vida", r"enjoy life", r"disfruta"],
    "Q6": [r"vida tem sentido", r"life to be meaningful", r"vida tiene sentido", r"meaningful"],
    "Q7": [r"concentrar", r"concentrate", r"concentracion"],
    "Q8": [r"segur[oa]\b.*vida diaria", r"\bseguro\b", r"feel safe", r"\bseguridad\b", r"\bsafe\b"],
    "Q9": [r"ambiente fisico", r"physical environment"],
    "Q10": [r"\benergia\b", r"\benergy\b"],
    "Q11": [r"aparencia", r"bodily appearance", r"apariencia", r"appearance"],
    "Q12": [r"dinheiro", r"\bdinero\b", r"\bmoney\b"],
    "Q13": [r"informac", r"information"],
    "Q14": [r"\blazer\b", r"leisure", r"\bocio\b"],
    "Q15": [r"locomover", r"get around", r"desplazarse"],
    "Q16": [r"\bsono\b", r"\bsleep\b", r"\bsueno\b"],
    "Q17": [r"desempenhar as atividades", r"daily living activities", r"activities of daily",
            r"actividades de la vida diaria"],
    "Q18": [r"capacidade (para o|de) trabalh", r"capacity for work", r"capacidad (de|para el) trabajo", r"\bwork\b"],
    "Q19": [r"consigo mesm", r"with yourself", r"\bsi mism"],
    "Q20": [r"relac\w* pessoa", r"personal relationships", r"relaciones personales"],
    "Q21": [r"vida sexual", r"sex life"],
    "Q22": [r"\bapoio\b", r"\bapoyo\b", r"support"],
    "Q23": [r"local onde mora", r"living place", r"lugar donde vive", r"condicoes .*mora"],
    "Q24": [r"servicos de saude", r"health services", r"servicios (sanitarios|de salud)"],
    "Q25": [r"transporte", r"transport"],
    "Q26": [r"sentimentos negativos", r"negative feelings", r"sentimientos negativos"],
}

DOMAINS = {
    "physical": Domain("physical", ("Q3", "Q4", "Q10", "Q15", "Q16", "Q17", "Q18"), 6,
                       {"pt": "Físico", "en": "Physical health", "es": "Salud física"}),
    "psychological": Domain("psychological", ("Q5", "Q6", "Q7", "Q11", "Q19", "Q26"), 5,
                            {"pt": "Psicológico", "en": "Psychological", "es": "Psicológico"}),
    "social": Domain("social", ("Q20", "Q21", "Q22"), 2,
                     {"pt": "Relações sociais", "en": "Social relationships", "es": "Relaciones sociales"}),
    "environment": Domain("environment", ("Q8", "Q9", "Q12", "Q13", "Q14", "Q23", "Q24", "Q25"), 6,
                          {"pt": "Meio ambiente", "en": "Environment", "es": "Ambiente"}),
    # Q1 and Q2 belong to no domain; many studies report them as "overall QoL and general health".
    "overall": Domain("overall", ("Q1", "Q2"), 2,
                      {"pt": "QV geral e saúde (Q1–Q2)", "en": "Overall QoL and general health (Q1–Q2)",
                       "es": "CV global y salud general (Q1–Q2)"}, in_measurement_model=False),
}

VERSIONS = (
    LanguageVersion(
        "pt-BR", "pt", "Fleck et al., 2000",
        "Fleck MPA, Louzada S, Xavier M, Chachamovich E, Vieira G, Santos L, et al. Aplicação da versão em "
        "português do instrumento abreviado de avaliação da qualidade de vida \"WHOQOL-bref\". Rev Saúde Pública. "
        "2000;34(2):178-183.",
        {"pt": "versão validada para o português brasileiro (Fleck et al., 2000)",
         "en": "validated Brazilian Portuguese version (Fleck et al., 2000)",
         "es": "versión validada al portugués de Brasil (Fleck et al., 2000)"}),
    LanguageVersion(
        "es-ES", "es", "Lucas, 1998",
        "Lucas R. Versión española del WHOQOL. Madrid: Ergon; 1998.",
        {"pt": "versão em espanhol (Lucas, 1998)",
         "en": "Spanish version (Lucas, 1998)",
         "es": "versión española (Lucas, 1998)"}),
    LanguageVersion(
        "en", "en", "The WHOQOL Group, 1998",
        "The WHOQOL Group. Development of the World Health Organization WHOQOL-BREF quality of life assessment. "
        "Psychol Med. 1998;28(3):551-558.",
        {"pt": "versão genérica em inglês (The WHOQOL Group, 1998)",
         "en": "generic English version (The WHOQOL Group, 1998)",
         "es": "versión genérica en inglés (The WHOQOL Group, 1998)"}),
)

WHOQOL_BREF = Instrument(
    key="whoqol-bref",
    name="WHOQOL-BREF",
    items=ITEMS,
    reversed_items=("Q3", "Q4", "Q26"),
    domains=DOMAINS,
    min_valid_total=21,
    item_text=ITEM_TEXT,
    item_short=ITEM_SHORT,
    item_patterns=ITEM_PATTERNS,
    versions=VERSIONS,
    primary_reference=("World Health Organization. WHOQOL-BREF: introduction, administration, scoring and generic "
                       "version of the assessment. Field trial version. Geneva: WHO; 1996."),
    description={
        "pt": ("O WHOQOL-BREF é a versão abreviada do WHOQOL-100, com 26 itens respondidos em escalas de cinco pontos "
               "(The WHOQOL Group, 1998). Dois itens avaliam a qualidade de vida global e a satisfação com a saúde, "
               "e os 24 restantes compõem quatro domínios: físico (7 itens), psicológico (6), relações sociais (3) "
               "e meio ambiente (8)"),
        "en": ("The WHOQOL-BREF is the 26-item abbreviated version of the WHOQOL-100, answered on five-point scales "
               "(The WHOQOL Group, 1998). Two items assess overall quality of life and satisfaction with health, "
               "and the remaining 24 form four domains: physical health (7 items), psychological (6), social "
               "relationships (3) and environment (8)"),
        "es": ("El WHOQOL-BREF es la versión abreviada del WHOQOL-100, con 26 ítems respondidos en escalas de cinco puntos "
               "(The WHOQOL Group, 1998). Dos ítems evalúan la calidad de vida global y la satisfacción con la salud, "
               "y los 24 restantes forman cuatro dominios: salud física (7 ítems), psicológico (6), relaciones "
               "sociales (3) y ambiente (8)"),
    },
    references=(
        "The WHOQOL Group. Development of the World Health Organization WHOQOL-BREF quality of life assessment. "
        "Psychol Med. 1998;28(3):551-558.",
        "Skevington SM, Lotfy M, O'Connell KA. The World Health Organization's WHOQOL-BREF quality of life "
        "assessment: psychometric properties and results of the international field trial. Qual Life Res. "
        "2004;13(2):299-310.",
    ),
)
