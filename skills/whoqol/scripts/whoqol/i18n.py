"""Report language: Portuguese, English or Spanish.

By default (``lang="auto"``) the report follows the language of the administered questionnaire,
detected from the item headers and text answers; English when it cannot be detected. JSON outputs
keep English codes and values (machine-readable); only what a person reads (Markdown, DOCX, XLSX
headers, figures) is localized, at rendering time.
"""

from __future__ import annotations

import math

LANGS = ("pt", "en", "es")
FALLBACK = "en"


def report_language(requested: str | None, detected: str | None) -> str:
    if requested and requested != "auto":
        return requested if requested in LANGS else FALLBACK
    return detected if detected in LANGS else FALLBACK


# ---------------------------------------------------------------- numbers
def _isnan(x) -> bool:
    try:
        return x is None or math.isnan(float(x))
    except (TypeError, ValueError):
        return True


def fmt(x, nd: int = 1, lang: str = "en") -> str:
    if _isnan(x):
        return "—"
    s = f"{float(x):.{nd}f}"
    return s.replace(".", ",") if lang in ("pt", "es") else s


def fmt_r(x, lang: str = "en", nd: int = 2) -> str:
    """Statistics bounded by 1 (APA, English: no leading zero)."""
    s = fmt(x, nd, lang)
    if lang == "en" and s != "—":
        if s.startswith("0."):
            s = s[1:]
        elif s.startswith("-0."):
            s = "-" + s[2:]
    return s


def fmt_p(p, lang: str = "en") -> str:
    if _isnan(p):
        return "—"
    p = float(p)
    if p < 0.001:
        return {"pt": "< 0,001", "es": "< 0,001"}.get(lang, "< .001")
    return fmt_r(p, lang, 3)


def p_expr(p, lang: str = "en") -> str:
    """'= 0.012' or '< .001' — to write 'p {expr}' without '= <'."""
    s = fmt_p(p, lang)
    return s if s.startswith("<") or s == "—" else f"= {s}"


def join_list(items, lang: str) -> str:
    items = [str(i) for i in items]
    if len(items) <= 1:
        return "".join(items)
    conj = {"pt": " e ", "en": " and ", "es": " y "}[lang]
    return ", ".join(items[:-1]) + conj + items[-1]


# ---------------------------------------------------------------- strings
T: dict[str, dict[str, str]] = {
    # generic
    "score": {"pt": "Escore", "en": "Score", "es": "Puntuación"},
    "domain": {"pt": "Domínio", "en": "Domain", "es": "Dominio"},
    "items": {"pt": "Itens", "en": "Items", "es": "Ítems"},
    "statistic": {"pt": "Estatística", "en": "Statistic", "es": "Estadístico"},
    "effect_size": {"pt": "Tamanho de efeito", "en": "Effect size", "es": "Tamaño del efecto"},
    "note": {"pt": "Nota.", "en": "Note.", "es": "Nota."},
    "figure": {"pt": "Figura", "en": "Figure", "es": "Figura"},
    "references": {"pt": "Referências", "en": "References", "es": "Referencias"},
    "sd": {"pt": "DP", "en": "SD", "es": "DE"},
    "mean_sd": {"pt": "Média (DP)", "en": "M (SD)", "es": "Media (DE)"},
    "ci95": {"pt": "IC 95%", "en": "95% CI", "es": "IC 95%"},
    "ci90": {"pt": "IC 90%", "en": "90% CI", "es": "IC 90%"},
    "median_iqr": {"pt": "Mediana [IIQ]", "en": "Mdn [IQR]", "es": "Mediana [RIC]"},
    "raw_mean_sd": {"pt": "Média {range} (DP)", "en": "M {range} (SD)", "es": "Media {range} (DE)"},
    "floor": {"pt": "Piso %", "en": "Floor %", "es": "Suelo %"},
    "ceiling": {"pt": "Teto %", "en": "Ceiling %", "es": "Techo %"},
    "alpha_ci": {"pt": "α (IC 95%)", "en": "α (95% CI)", "es": "α (IC 95%)"},
    "mean_interitem": {"pt": "r̄ interitem", "en": "Mean inter-item r", "es": "r̄ interítem"},
    "sem": {"pt": "EPM", "en": "SEM", "es": "EEM"},
    "mdc95": {"pt": "MMD95", "en": "MDC95", "es": "CMD95"},
    "half_sd": {"pt": "½ DP", "en": "½ SD", "es": "½ DE"},
    "total_items": {"pt": "Total ({n} itens)", "en": "Total ({n} items)", "es": "Total ({n} ítems)"},
    "total_score": {"pt": "Escore total (todos os itens; não oficial)", "en": "Total score (all items; unofficial)",
                    "es": "Puntuación total (todos los ítems; no oficial)"},
    "df": {"pt": "gl", "en": "df", "es": "gl"},
    "term": {"pt": "Termo", "en": "Term", "es": "Término"},
    "r2adj": {"pt": "R² ajustado", "en": "Adjusted R²", "es": "R² ajustado"},
    # tests (codes produced by stats.py)
    "test_welch_t": {"pt": "t de Welch", "en": "Welch's t", "es": "t de Welch"},
    "test_mann_whitney": {"pt": "U de Mann-Whitney", "en": "Mann-Whitney U", "es": "U de Mann-Whitney"},
    "test_welch_anova": {"pt": "ANOVA de Welch", "en": "Welch's ANOVA", "es": "ANOVA de Welch"},
    "test_kruskal": {"pt": "H de Kruskal-Wallis", "en": "Kruskal-Wallis H", "es": "H de Kruskal-Wallis"},
    "test_games_howell": {"pt": "Games-Howell", "en": "Games-Howell", "es": "Games-Howell"},
    "test_dunn": {"pt": "Dunn (Holm)", "en": "Dunn (Holm)", "es": "Dunn (Holm)"},
    "mag_trivial": {"pt": "trivial", "en": "trivial", "es": "trivial"},
    "mag_small": {"pt": "pequeno", "en": "small", "es": "pequeño"},
    "mag_medium": {"pt": "médio", "en": "medium", "es": "mediano"},
    "mag_large": {"pt": "grande", "en": "large", "es": "grande"},
    "reason_user": {"pt": "escolhido pelo usuário", "en": "chosen by the user", "es": "elegido por el usuario"},
    "reason_clt": {"pt": "todos os grupos com n ≥ 30 (teorema central do limite)",
                   "en": "all groups with n ≥ 30 (central limit theorem)",
                   "es": "todos los grupos con n ≥ 30 (teorema central del límite)"},
    "reason_shapiro_reject": {"pt": "Shapiro-Wilk rejeitou a normalidade em algum grupo com n < 30",
                              "en": "Shapiro-Wilk rejected normality in a group with n < 30",
                              "es": "Shapiro-Wilk rechazó la normalidad en algún grupo con n < 30"},
    "reason_shapiro_ok": {"pt": "Shapiro-Wilk não rejeitou a normalidade em nenhum grupo",
                          "en": "Shapiro-Wilk did not reject normality in any group",
                          "es": "Shapiro-Wilk no rechazó la normalidad en ningún grupo"},
    # tables
    "t_desc": {"pt": "Tabela {n}. Escores do {inst} (0–100), efeitos piso/teto e consistência interna",
               "en": "Table {n}. {inst} scores (0–100), floor/ceiling effects and internal consistency",
               "es": "Tabla {n}. Puntuaciones del {inst} (0–100), efectos suelo/techo y consistencia interna"},
    "n_desc": {"pt": "Escores transformados para 0–100 conforme a OMS. Piso/teto: % no escore mínimo/máximo "
                     "(> 15% indica efeito). α: alfa de Cronbach; ω: ômega de McDonald (modelo unifatorial).",
               "en": "Scores transformed to 0–100 following the WHO. Floor/ceiling: % at the minimum/maximum "
                     "(> 15% indicates an effect). α: Cronbach's alpha; ω: McDonald's omega (one-factor model).",
               "es": "Puntuaciones transformadas a 0–100 según la OMS. Suelo/techo: % en la puntuación mínima/máxima "
                     "(> 15% indica efecto). α: alfa de Cronbach; ω: omega de McDonald (modelo unifactorial)."},
    "t_rel": {"pt": "Tabela {n}. Confiabilidade e precisão de medida por domínio",
              "en": "Table {n}. Reliability and measurement precision by domain",
              "es": "Tabla {n}. Fiabilidad y precisión de medida por dominio"},
    "n_rel": {"pt": "IC 95% do α pelo método de Feldt. EPM = DP × √(1 − α); MMD95 = 1,96 × √2 × EPM; "
                    "½ DP como referência distributiva de diferença mínima importante (Norman et al., 2003).",
              "en": "95% CI for α by Feldt's method. SEM = SD × √(1 − α); MDC95 = 1.96 × √2 × SEM; "
                    "½ SD as a distribution-based minimal important difference (Norman et al., 2003).",
              "es": "IC 95% de α por el método de Feldt. EEM = DE × √(1 − α); CMD95 = 1,96 × √2 × EEM; "
                    "½ DE como referencia distributiva de diferencia mínima importante (Norman et al., 2003)."},
    "t_corr": {"pt": "Tabela {n}. Correlações de Spearman entre os escores",
               "en": "Table {n}. Spearman correlations between scores",
               "es": "Tabla {n}. Correlaciones de Spearman entre las puntuaciones"},
    "n_corr": {"pt": "* p < 0,05; ** p < 0,01; *** p < 0,001.", "en": "* p < .05; ** p < .01; *** p < .001.",
               "es": "* p < 0,05; ** p < 0,01; *** p < 0,001."},
    "t_cfa": {"pt": "Tabela {n}. Índices de ajuste da análise fatorial confirmatória ({k} fatores, {i} itens)",
              "en": "Table {n}. Confirmatory factor analysis fit indices ({k} factors, {i} items)",
              "es": "Tabla {n}. Índices de ajuste del análisis factorial confirmatorio ({k} factores, {i} ítems)"},
    "t_cfa_facet": {"pt": "Tabela {n}. Índices de ajuste da análise fatorial confirmatória por facetas ({k} fatores, "
                          "{i} facetas)",
                    "en": "Table {n}. Facet-level confirmatory factor analysis fit indices ({k} factors, {i} facets)",
                    "es": "Tabla {n}. Índices de ajuste del análisis factorial confirmatorio por facetas ({k} factores, "
                          "{i} facetas)"},
    "n_cfa": {"pt": "Estimador de máxima verossimilhança. Critérios: CFI/TLI ≥ 0,90 (aceitável) ou ≥ 0,95 (bom); "
                    "RMSEA ≤ 0,08; SRMR ≤ 0,08 (Hu & Bentler, 1999).",
              "en": "Maximum likelihood estimator. Criteria: CFI/TLI ≥ .90 (acceptable) or ≥ .95 (good); "
                    "RMSEA ≤ .08; SRMR ≤ .08 (Hu & Bentler, 1999).",
              "es": "Estimador de máxima verosimilitud. Criterios: CFI/TLI ≥ 0,90 (aceptable) o ≥ 0,95 (bueno); "
                    "RMSEA ≤ 0,08; SRMR ≤ 0,08 (Hu & Bentler, 1999)."},
    "t_group": {"pt": "Tabela {n}. Escores do {inst} segundo {name}", "en": "Table {n}. {inst} scores by {name}",
                "es": "Tabla {n}. Puntuaciones del {inst} según {name}"},
    "n_group": {"pt": "Valores: {desc}. Teste: {test}. p (Holm): corrigido para comparações múltiplas entre escores. "
                      "Escolha do teste: {reason}.",
                "en": "Values: {desc}. Test: {test}. p (Holm): adjusted for multiple comparisons across scores. "
                      "Test choice: {reason}.",
                "es": "Valores: {desc}. Prueba: {test}. p (Holm): ajustado por comparaciones múltiples entre "
                      "puntuaciones. Elección de la prueba: {reason}."},
    # markdown report
    "report_title": {"pt": "Relatório de análise do {inst}", "en": "{inst} analysis report",
                     "es": "Informe de análisis del {inst}"},
    "file": {"pt": "Arquivo", "en": "File", "es": "Archivo"},
    "h_sample": {"pt": "Amostra e qualidade dos dados", "en": "Sample and data quality",
                 "es": "Muestra y calidad de los datos"},
    "rows": {"pt": "Linhas na planilha", "en": "Rows in the spreadsheet", "es": "Filas en la hoja"},
    "complete": {"pt": "Questionários completos ({k} itens)", "en": "Complete questionnaires ({k} items)",
                 "es": "Cuestionarios completos ({k} ítems)"},
    "excluded": {"pt": "Excluídos (< {m} itens válidos)", "en": "Excluded (< {m} valid items)",
                 "es": "Excluidos (< {m} ítems válidos)"},
    "analysed": {"pt": "Analisados", "en": "Analysed", "es": "Analizados"},
    "missing_overall": {"pt": "Dados ausentes (total)", "en": "Missing data (overall)", "es": "Datos faltantes (total)"},
    "detected_version": {"pt": "Versão detectada", "en": "Detected version", "es": "Versión detectada"},
    "h_flags": {"pt": "Alertas para interpretação", "en": "Interpretation flags", "es": "Alertas para la interpretación"},
    "h_posthoc": {"pt": "Comparações post hoc — {name}", "en": "Post hoc comparisons — {name}",
                  "es": "Comparaciones post hoc — {name}"},
    "h_regression": {"pt": "Regressão linear ajustada (EP robusto HC3)",
                     "en": "Adjusted linear regression (HC3 robust SE)",
                     "es": "Regresión lineal ajustada (EE robusto HC3)"},
    "h_reference": {"pt": "Comparação com valores de referência", "en": "Comparison with reference values",
                    "es": "Comparación con valores de referencia"},
    "h_cutoff": {"pt": "Ponto de corte ≥ {c}", "en": "Cut-off ≥ {c}", "es": "Punto de corte ≥ {c}"},
    "h_figures": {"pt": "Figuras", "en": "Figures", "es": "Figuras"},
    "docx_title": {"pt": "{inst} — tabelas e figuras", "en": "{inst} — tables and figures",
                   "es": "{inst} — tablas y figuras"},
    # figures
    "fig_dist_title": {"pt": "Distribuição dos escores por domínio", "en": "Domain score distribution",
                       "es": "Distribución de las puntuaciones por dominio"},
    "fig_score_axis": {"pt": "Escore (0–100)", "en": "Score (0–100)", "es": "Puntuación (0–100)"},
    "fig_dist_note": {"pt": "Caixa: mediana e IIQ; losango: média", "en": "Box: median and IQR; diamond: mean",
                      "es": "Caja: mediana y RIC; rombo: media"},
    "fig_items_title": {"pt": "Distribuição das respostas por item (escala original 1–5)",
                        "en": "Item response distribution (original 1–5 scale)",
                        "es": "Distribución de las respuestas por ítem (escala original 1–5)"},
    "fig_response": {"pt": "Resposta", "en": "Response", "es": "Respuesta"},
    "fig_corr_title": {"pt": "Correlações de Spearman entre escores", "en": "Spearman correlations between scores",
                       "es": "Correlaciones de Spearman entre puntuaciones"},
    "fig_group_title": {"pt": "Escores por {name}", "en": "Scores by {name}", "es": "Puntuaciones según {name}"},
    "fig_mean_ci": {"pt": "Média (IC 95%)", "en": "Mean (95% CI)", "es": "Media (IC 95%)"},
    "h_sensitivity": {"pt": "Análise de sensibilidade das regras de pontuação",
                      "en": "Sensitivity of the results to the scoring rules",
                      "es": "Análisis de sensibilidad de las reglas de puntuación"},
    "sens_intro": {
        "pt": ("Onde o manual ou a sintaxe oficial são omissos ou divergem, o toolkit adota uma regra (descrita nos "
               "métodos). Aqui os mesmos dados são pontuados com cada regra alternativa documentada. Escores 0–100; "
               "Δ = média alternativa − média adotada; as diferenças por pessoa usam só quem tem escore pelas duas "
               "regras. Alertas quando |Δ| ≥ 0,2 DP ou quando o número de escores muda 5% ou mais."),
        "en": ("Where the official manual or syntax is silent or inconsistent, the toolkit adopts one rule (stated in the "
               "methods). Here the same data are scored with each documented alternative rule. Scores 0–100; Δ = "
               "alternative mean − adopted mean; per-person differences use respondents scored by both rules. Flagged "
               "when |Δ| ≥ 0.2 SD or when the number of scores changes by 5% or more."),
        "es": ("Donde el manual o la sintaxis oficial no dicen nada o difieren, el toolkit adopta una regla (descrita en "
               "los métodos). Aquí los mismos datos se puntúan con cada regla alternativa documentada. Puntuaciones "
               "0–100; Δ = media alternativa − media adoptada; las diferencias por persona usan solo a quienes tienen "
               "puntuación con ambas reglas. Alertas cuando |Δ| ≥ 0,2 DE o cuando el número de puntuaciones cambia un "
               "5% o más.")},
    "sens_nochange": {
        "pt": "Nenhum escore mudou com as regras alternativas nestes dados.",
        "en": "No score changed under the alternative rules in these data.",
        "es": "Ninguna puntuación cambió con las reglas alternativas en estos datos."},
    "sens_note": {
        "pt": ("Só aparecem os escores que mudam; facetas cujo valor não muda (só o n) e a tabela completa estão na "
               "aba scoring_sensitivity de results.xlsx."),
        "en": ("Only scores that change are shown; facets whose value does not change (only n does) and the full table "
               "are in the scoring_sensitivity sheet of results.xlsx."),
        "es": ("Solo aparecen las puntuaciones que cambian; las facetas cuyo valor no cambia (solo el n) y la tabla "
               "completa están en la hoja scoring_sensitivity de results.xlsx.")},
    "sens_rule": {"pt": "Regra alternativa", "en": "Alternative rule", "es": "Regla alternativa"},
    "sens_score": {"pt": "Escore", "en": "Score", "es": "Puntuación"},
    "sens_n": {"pt": "n (adotada → alternativa)", "en": "n (adopted → alternative)",
               "es": "n (adoptada → alternativa)"},
    "sens_means": {"pt": "Média (adotada → alternativa)", "en": "Mean (adopted → alternative)",
                   "es": "Media (adoptada → alternativa)"},
    "sens_maxdiff": {"pt": "Máx. dif. absoluta por pessoa", "en": "Max. absolute diff. per person",
                     "es": "Máx. dif. absoluta por persona"},
    "sens_changed": {"pt": "Pessoas com valor alterado", "en": "People with a changed value",
                     "es": "Personas con valor alterado"},
    # plain-language summary and reading aids (Markdown report)
    "h_summary": {"pt": "Em resumo", "en": "In brief", "es": "En resumen"},
    "sum_n": {"pt": "Foram analisados {n} de {rows} questionários", "en": "{n} of {rows} questionnaires were analysed",
              "es": "Se analizaron {n} de {rows} cuestionarios"},
    "sum_n_exc": {"pt": " ({exc} excluídos por terem menos de {m} itens respondidos)",
                  "en": " ({exc} excluded for having fewer than {m} answered items)",
                  "es": " ({exc} excluidos por tener menos de {m} ítems respondidos)"},
    "sum_n_exc1": {"pt": " (1 excluído por ter menos de {m} itens respondidos)",
                   "en": " (1 excluded for having fewer than {m} answered items)",
                   "es": " (1 excluido por tener menos de {m} ítems respondidos)"},
    "sum_profile": {"pt": "Na escala de 0 a 100 (quanto maior, melhor a qualidade de vida), as médias dos domínios "
                          "ficaram entre {lo} ({lo_lab}) e {hi} ({hi_lab}).",
                    "en": "On the 0–100 scale (higher means better quality of life), the domain means ranged from "
                          "{lo} ({lo_lab}) to {hi} ({hi_lab}).",
                    "es": "En la escala de 0 a 100 (cuanto mayor, mejor calidad de vida), las medias de los dominios "
                          "estuvieron entre {lo} ({lo_lab}) y {hi} ({hi_lab})."},
    "sum_similar": {"pt": " A diferença entre eles ({d} pontos) é menor que meio desvio-padrão: nenhum domínio se "
                          "destaca dos demais.",
                    "en": " The gap between them ({d} points) is under half a standard deviation: no domain stands out "
                          "from the others.",
                    "es": " La diferencia entre ellos ({d} puntos) es menor que media desviación estándar: ningún "
                          "dominio se destaca de los demás."},
    "sum_apart": {"pt": " A diferença entre eles ({d} pontos) passa de meio desvio-padrão, o que pode ter relevância "
                        "prática.",
                  "en": " The gap between them ({d} points) exceeds half a standard deviation, which may matter in "
                        "practice.",
                  "es": " La diferencia entre ellos ({d} puntos) supera media desviación estándar, lo que puede tener "
                        "relevancia práctica."},
    "sum_norms": {"pt": "A OMS não define pontos de corte: para dizer se esses valores são altos ou baixos, compare-os "
                        "com valores normativos publicados para uma população semelhante.",
                  "en": "The WHO defines no cut-offs: to say whether these values are high or low, compare them with "
                        "published normative values for a similar population.",
                  "es": "La OMS no define puntos de corte: para saber si estos valores son altos o bajos, compárelos "
                        "con valores normativos publicados para una población similar."},
    "sum_alpha_ok": {"pt": "A consistência interna foi adequada em todos os domínios (α ≥ 0,70).",
                     "en": "Internal consistency was adequate in every domain (α ≥ .70).",
                     "es": "La consistencia interna fue adecuada en todos los dominios (α ≥ 0,70)."},
    "sum_alpha_low": {"pt": "A consistência interna ficou abaixo de 0,70 em {doms}; interprete esses escores com "
                            "cautela.",
                      "en": "Internal consistency was below .70 in {doms}; interpret these scores with caution.",
                      "es": "La consistencia interna quedó por debajo de 0,70 en {doms}; interprete estas puntuaciones "
                            "con cautela."},
    "sum_alpha_many": {"pt": "A consistência interna ficou abaixo de 0,70 em {k} de {n} escalas (veja a Tabela 2); "
                             "interprete esses escores com cautela.",
                       "en": "Internal consistency was below .70 in {k} of {n} scales (see Table 2); interpret these "
                             "scores with caution.",
                       "es": "La consistencia interna quedó por debajo de 0,70 en {k} de {n} escalas (vea la Tabla 2); "
                             "interprete estas puntuaciones con cautela."},
    "sum_single": {"pt": "Na escala de 0 a 100 (quanto maior, melhor a qualidade de vida), o escore médio ({lab}) foi {m}.",
                   "en": "On the 0–100 scale (higher means better quality of life), the mean score ({lab}) was {m}.",
                   "es": "En la escala de 0 a 100 (cuanto mayor, mejor calidad de vida), la puntuación media ({lab}) fue {m}."},
    "sum_fc_none": {"pt": "Não houve efeito piso nem teto (poucas pessoas no mínimo ou no máximo da escala).",
                    "en": "There were no floor or ceiling effects (few people at the scale minimum or maximum).",
                    "es": "No hubo efecto suelo ni techo (pocas personas en el mínimo o el máximo de la escala)."},
    "sum_fc": {"pt": "Muitas pessoas no mínimo ou no máximo da escala (efeito piso/teto) em {scores}: o escore pode "
                     "não captar diferenças nesses extremos.",
               "en": "Many people at the scale minimum or maximum (floor/ceiling effect) in {scores}: the score may "
                     "miss differences at those extremes.",
               "es": "Muchas personas en el mínimo o el máximo de la escala (efecto suelo/techo) en {scores}: la "
                     "puntuación puede no captar diferencias en esos extremos."},
    "sum_group_none": {"pt": "Comparação por {name}: sem diferenças significativas após a correção de Holm.",
                       "en": "Comparison by {name}: no significant differences after Holm correction.",
                       "es": "Comparación según {name}: sin diferencias significativas tras la corrección de Holm."},
    "sum_group": {"pt": "Comparação por {name}: diferença significativa em {scores} (efeito {mags}).",
                  "en": "Comparison by {name}: significant difference in {scores} ({mags} effect).",
                  "es": "Comparación según {name}: diferencia significativa en {scores} (efecto {mags})."},
    "sum_flags": {"pt": "Leia os {k} alertas abaixo antes de interpretar os resultados.",
                  "en": "Read the {k} flags below before interpreting the results.",
                  "es": "Lea las {k} alertas de abajo antes de interpretar los resultados."},
    "sum_flags1": {"pt": "Leia o alerta abaixo antes de interpretar os resultados.",
                   "en": "Read the flag below before interpreting the results.",
                   "es": "Lea la alerta de abajo antes de interpretar los resultados."},
    "howto": {"pt": "Como ler.", "en": "How to read.", "es": "Cómo leer."},
    "howto_desc": {"pt": "Escala 0–100: quanto maior, melhor. O IC 95% é a faixa provável da média na população "
                         "estudada. A coluna {raw} repete a média na escala original do instrumento, útil para comparar "
                         "com estudos que a relatam assim. α e ω ≥ 0,70 indicam que os itens do domínio medem a mesma "
                         "coisa de forma consistente.",
                   "en": "0–100 scale: higher is better. The 95% CI is the likely range of the mean in the population "
                         "studied. The {raw} column repeats the mean on the instrument's original scale, useful for "
                         "comparing with studies that report it that way. α and ω ≥ .70 mean the domain's items "
                         "measure the same thing consistently.",
                   "es": "Escala 0–100: cuanto mayor, mejor. El IC 95% es el rango probable de la media en la población "
                         "estudiada. La columna {raw} repite la media en la escala original del instrumento, útil para "
                         "comparar con estudios que la informan así. α y ω ≥ 0,70 indican que los ítems del dominio "
                         "miden lo mismo de forma consistente."},
    "howto_rel": {"pt": "EPM é o erro típico do escore de uma pessoa. MMD95 é a menor mudança individual que supera o "
                        "erro de medida: no domínio {dom}, mudanças menores que {mdc} pontos podem ser só erro. ½ DP ({hs} "
                        "pontos no domínio {dom}) é uma referência para diferenças médias entre grupos ou momentos que tendem a "
                        "ser perceptíveis. r̄ interitem é a correlação média entre os itens do domínio.",
                  "en": "SEM is the typical error of one person's score. MDC95 is the smallest individual change that "
                        "exceeds measurement error: in the {dom} domain, changes under {mdc} points may be error alone. ½ SD ({hs} "
                        "points in the {dom} domain) is a benchmark for mean differences between groups or time points that tend "
                        "to be noticeable. Mean inter-item r is the average correlation among the domain's items.",
                  "es": "EEM es el error típico de la puntuación de una persona. CMD95 es el menor cambio individual que "
                        "supera el error de medida: en el dominio {dom}, cambios menores que {mdc} puntos pueden ser solo error. "
                        "½ DE ({hs} puntos en el dominio {dom}) es una referencia para diferencias medias entre grupos o momentos "
                        "que suelen ser perceptibles. r̄ interítem es la correlación media entre los ítems del dominio."},
    "howto_corr": {"pt": "ρ indica quanto dois escores variam juntos (0 = nenhuma relação; 1 = relação perfeita). Como "
                         "referência, 0,10, 0,30 e 0,50 correspondem a associações fraca, moderada e forte (Cohen, 1988).",
                   "en": "ρ shows how closely two scores move together (0 = no relation; 1 = perfect relation). As a "
                         "benchmark, .10, .30 and .50 correspond to weak, moderate and strong associations (Cohen, 1988).",
                   "es": "ρ indica cuánto varían juntas dos puntuaciones (0 = ninguna relación; 1 = relación perfecta). "
                         "Como referencia, 0,10, 0,30 y 0,50 corresponden a asociaciones débil, moderada y fuerte "
                         "(Cohen, 1988)."},
    "howto_cfa": {"pt": "Verifica se os itens se agrupam nos domínios previstos. CFI e TLI próximos de 1 e RMSEA e SRMR "
                        "próximos de 0 indicam bom ajuste; os limites estão na nota.",
                  "en": "Checks whether the items group into the expected domains. CFI and TLI near 1 and RMSEA and "
                        "SRMR near 0 indicate good fit; the thresholds are in the note.",
                  "es": "Verifica si los ítems se agrupan en los dominios previstos. CFI y TLI cercanos a 1 y RMSEA y "
                        "SRMR cercanos a 0 indican buen ajuste; los límites están en la nota."},
    "howto_group": {"pt": "p (Holm) < 0,05 indica uma diferença pouco provável de ser obra do acaso; o tamanho de efeito "
                          "diz se ela é grande o bastante para importar na prática.",
                    "en": "p (Holm) < .05 marks a difference unlikely to be due to chance; the effect size tells whether "
                          "it is large enough to matter in practice.",
                    "es": "p (Holm) < 0,05 indica una diferencia poco probable por azar; el tamaño del efecto dice si es "
                          "lo bastante grande para importar en la práctica."},
    "h_validity": {"pt": "Validade de constructo", "en": "Construct validity", "es": "Validez de constructo"},
    "val_mt": {"pt": "Análise multitraço ({n} questionários completos): {pct}% dos itens correlacionaram mais com o "
                     "próprio domínio do que com os demais (ideal: 100%). Itens com correlação corrigida < 0,40 com o "
                     "próprio domínio: {low}.",
               "en": "Multitrait scaling ({n} complete questionnaires): {pct}% of the items correlated more with their "
                     "own domain than with the others (ideal: 100%). Items with corrected correlation < .40 with their "
                     "own domain: {low}.",
               "es": "Análisis multirrasgo ({n} cuestionarios completos): el {pct}% de los ítems correlacionó más con su "
                     "propio dominio que con los demás (ideal: 100%). Ítems con correlación corregida < 0,40 con su "
                     "propio dominio: {low}."},
    "val_htmt": {"pt": "HTMT máximo: {v}, entre {a} e {b}. Valores < 0,85 indicam que os domínios medem aspectos "
                       "distintos (Henseler et al., 2015). A matriz completa está na aba htmt de results.xlsx.",
                 "en": "Highest HTMT: {v}, between {a} and {b}. Values < .85 indicate that the domains measure distinct "
                       "aspects (Henseler et al., 2015). The full matrix is in the htmt sheet of results.xlsx.",
                 "es": "HTMT máximo: {v}, entre {a} y {b}. Valores < 0,85 indican que los dominios miden aspectos "
                       "distintos (Henseler et al., 2015). La matriz completa está en la hoja htmt de results.xlsx."},
    "none": {"pt": "nenhum", "en": "none", "es": "ninguno"},
    "fig_corr_caption": {"pt": "Correlações de Spearman entre os escores (cores mais intensas, associação mais forte)",
                         "en": "Spearman correlations between scores (stronger colours, stronger association)",
                         "es": "Correlaciones de Spearman entre las puntuaciones (colores más intensos, asociación más "
                               "fuerte)"},
}


def t(key: str, lang: str, **kw) -> str:
    s = T[key].get(lang) or T[key][FALLBACK]
    return s.format(**kw) if kw else s


# ---------------------------------------------------------------- flags
# Flags are produced as {"code": ..., **params} by analysis.py and rendered here.
FLAGS: dict[str, dict[str, str]] = {
    "excluded": {
        "pt": "{n} questionários excluídos por terem menos de {m} itens válidos (regra da OMS).",
        "en": "{n} questionnaires excluded for having fewer than {m} valid items (WHO rule).",
        "es": "{n} cuestionarios excluidos por tener menos de {m} ítems válidos (regla de la OMS)."},
    "items_missing": {
        "pt": "Itens com mais de 5% de dados ausentes: {items}.",
        "en": "Items with more than 5% missing: {items}.",
        "es": "Ítems con más del 5% de datos faltantes: {items}."},
    "unrecognized": {
        "pt": "Há respostas não reconhecidas, tratadas como ausentes: revise 'unrecognized_values'.",
        "en": "Some answers were not recognized and were treated as missing: check 'unrecognized_values'.",
        "es": "Hay respuestas no reconocidas, tratadas como faltantes: revise 'unrecognized_values'."},
    "straightlining": {
        "pt": "{n} respondentes deram a mesma resposta em todos os itens (possível resposta descuidada; "
              "considere análise de sensibilidade).",
        "en": "{n} respondents gave the same answer to every item (possible careless responding; "
              "consider a sensitivity analysis).",
        "es": "{n} encuestados dieron la misma respuesta en todos los ítems (posible respuesta descuidada; "
              "considere un análisis de sensibilidad)."},
    "duplicates": {
        "pt": "{n} linhas com padrão de resposta idêntico a outra (verificar envio duplicado).",
        "en": "{n} rows with a response pattern identical to another row (check for duplicate submissions).",
        "es": "{n} filas con un patrón de respuesta idéntico a otra (verificar envíos duplicados)."},
    "small_n": {
        "pt": "Amostra pequena (n = {n}): estimativas imprecisas; priorize os intervalos de confiança.",
        "en": "Small sample (n = {n}): imprecise estimates; focus on the confidence intervals.",
        "es": "Muestra pequeña (n = {n}): estimaciones imprecisas; priorice los intervalos de confianza."},
    "alpha_low": {
        "pt": "α de Cronbach < 0,70 em {domain} (α = {a}).",
        "en": "Cronbach's α < .70 in {domain} (α = {a}).",
        "es": "α de Cronbach < 0,70 en {domain} (α = {a})."},
    "alpha_low_few_items": {
        "pt": "α de Cronbach < 0,70 em {domain} (α = {a}). O domínio tem só {k} itens, e α baixo é comum na "
              "literatura; relate também ω e a correlação média interitem.",
        "en": "Cronbach's α < .70 in {domain} (α = {a}). The domain has only {k} items and a low α is common in "
              "the literature; also report ω and the mean inter-item correlation.",
        "es": "α de Cronbach < 0,70 en {domain} (α = {a}). El dominio tiene solo {k} ítems y un α bajo es común "
              "en la literatura; informe también ω y la correlación media interítem."},
    "alpha_high": {
        "pt": "α > 0,95 em {domain}: possível redundância de itens.",
        "en": "α > .95 in {domain}: possible item redundancy.",
        "es": "α > 0,95 en {domain}: posible redundancia de ítems."},
    "floor": {
        "pt": "Efeito piso (> 15%) em {score} (Terwee et al., 2007).",
        "en": "Floor effect (> 15%) in {score} (Terwee et al., 2007).",
        "es": "Efecto suelo (> 15%) en {score} (Terwee et al., 2007)."},
    "ceiling": {
        "pt": "Efeito teto (> 15%) em {score} (Terwee et al., 2007).",
        "en": "Ceiling effect (> 15%) in {score} (Terwee et al., 2007).",
        "es": "Efecto techo (> 15%) en {score} (Terwee et al., 2007)."},
    "item_r_low": {
        "pt": "Itens com correlação corrigida < 0,40 com o próprio domínio: {items}.",
        "en": "Items with corrected correlation < .40 with their own domain: {items}.",
        "es": "Ítems con correlación corregida < 0,40 con su propio dominio: {items}."},
    "scaling_fail": {
        "pt": "Itens que correlacionam mais com outro domínio do que com o próprio: {items}.",
        "en": "Items that correlate more with another domain than with their own: {items}.",
        "es": "Ítems que correlacionan más con otro dominio que con el propio: {items}."},
    "htmt": {
        "pt": "HTMT > 0,85 (discriminação limitada) entre: {pairs}.",
        "en": "HTMT > .85 (limited discriminant validity) between: {pairs}.",
        "es": "HTMT > 0,85 (discriminación limitada) entre: {pairs}."},
    "cfa_fit": {
        "pt": "AFC (ML): CFI = {cfi}, TLI = {tli}, RMSEA = {rmsea}, SRMR = {srmr}. Confirme com WLSMV "
              "(script lavaan gerado).",
        "en": "CFA (ML): CFI = {cfi}, TLI = {tli}, RMSEA = {rmsea}, SRMR = {srmr}. Confirm with WLSMV "
              "(generated lavaan script).",
        "es": "AFC (ML): CFI = {cfi}, TLI = {tli}, RMSEA = {rmsea}, SRMR = {srmr}. Confirme con WLSMV "
              "(script de lavaan generado)."},
    "cfa_small_n": {
        "pt": "AFC com n = {n} < 100: resultados apenas exploratórios (recomenda-se n ≥ 200).",
        "en": "CFA with n = {n} < 100: exploratory results only (n ≥ 200 recommended).",
        "es": "AFC con n = {n} < 100: resultados solo exploratorios (se recomienda n ≥ 200)."},
    "group_sig": {
        "pt": "Diferença significativa em {score} segundo {name} ({test}, p de Holm {p}; {es} = {v}, efeito {mag}).",
        "en": "Significant difference in {score} by {name} ({test}, Holm p {p}; {es} = {v}, {mag} effect).",
        "es": "Diferencia significativa en {score} según {name} ({test}, p de Holm {p}; {es} = {v}, "
              "efecto {mag})."},
    "group_error": {
        "pt": "Comparação por '{name}' não realizada: {error}",
        "en": "Comparison by '{name}' not performed: {error}",
        "es": "Comparación según '{name}' no realizada: {error}"},
    "group_dropped": {
        "pt": "Grupos de '{name}' com n < 3 excluídos: {groups}.",
        "en": "Groups of '{name}' with n < 3 excluded: {groups}.",
        "es": "Grupos de '{name}' con n < 3 excluidos: {groups}."},
    "sensitivity": {
        "pt": "Com a regra alternativa \"{alt}\", {score} muda {d} pontos na média (n {n1} → {n2}): veja a análise de "
              "sensibilidade antes de interpretar.",
        "en": "With the alternative rule \"{alt}\", {score} changes by {d} points on average (n {n1} → {n2}): see the "
              "sensitivity analysis before interpreting.",
        "es": "Con la regla alternativa \"{alt}\", {score} cambia {d} puntos en la media (n {n1} → {n2}): vea el "
              "análisis de sensibilidad antes de interpretar."},
    "version_unknown": {
        "pt": "Não foi possível identificar a versão linguística do questionário; informe 'instrument_version' "
              "para citar a validação correta no texto de métodos.",
        "en": "The language version of the questionnaire could not be identified; set 'instrument_version' so "
              "the methods text cites the right validation.",
        "es": "No fue posible identificar la versión lingüística del cuestionario; indique 'instrument_version' "
              "para citar la validación correcta en el texto de métodos."},
}


FLAGS_ONE: dict[str, dict[str, str]] = {
    "excluded": {
        "pt": "1 questionário excluído por ter menos de {m} itens válidos (regra da OMS).",
        "en": "1 questionnaire excluded for having fewer than {m} valid items (WHO rule).",
        "es": "1 cuestionario excluido por tener menos de {m} ítems válidos (regla de la OMS)."},
    "straightlining": {
        "pt": "1 respondente deu a mesma resposta em todos os itens (possível resposta descuidada; "
              "considere análise de sensibilidade).",
        "en": "1 respondent gave the same answer to every item (possible careless responding; "
              "consider a sensitivity analysis).",
        "es": "1 encuestado dio la misma respuesta en todos los ítems (posible respuesta descuidada; "
              "considere un análisis de sensibilidad)."},
    "duplicates": {
        "pt": "1 linha com padrão de resposta idêntico a outra (verificar envio duplicado).",
        "en": "1 row with a response pattern identical to another row (check for duplicate submissions).",
        "es": "1 fila con un patrón de respuesta idéntico a otra (verificar envíos duplicados)."},
}


ES_SYMBOL = {"hedges_g": "g", "rank_biserial_r": "r_rb", "omega2": "ω²", "epsilon2": "ε²",
             "cohen_d": "d", "spearman_rho": "ρ"}


def lower_label(label: str, lang: str) -> str:
    """Label for use mid-sentence: lower case in Portuguese/Spanish, keeping acronyms and codes (QV, Q1–Q2, F2.1)."""
    if lang == "en":
        return label
    return " ".join(w if sum(c.isupper() for c in w) > 1 or any(c.isdigit() for c in w) else w.lower()
                    for w in label.split(" "))


def score_label(key_or_col: str, lang: str, inst) -> str:
    key = key_or_col.replace("_0_100", "").replace("_raw", "")
    if key == "total":
        return t("total_score", lang)
    return inst.domain_label(key, lang)


def render_flag(flag: dict, lang: str, inst) -> str:
    """Localizes a flag {code, **params}: domain keys -> labels, numbers -> local format, codes -> words."""
    table = FLAGS_ONE if flag.get("n") == 1 and flag["code"] in FLAGS_ONE else FLAGS
    tpl = table[flag["code"]].get(lang) or table[flag["code"]][FALLBACK]
    p = {k: v for k, v in flag.items() if k != "code"}
    for k in ("domain", "score"):
        if k in p:
            p[k] = score_label(p[k], lang, inst)
    for k in ("a", "cfi", "tli", "rmsea", "srmr"):
        if k in p:
            p[k] = fmt_r(p[k], lang, 3 if k != "a" else 2)
    if "v" in p:
        p["v"] = fmt(p["v"], 2, lang)
    if "d" in p:
        p["d"] = fmt(p["d"], 1, lang)
    if "alt" in p:
        from .sensitivity import label_of
        p["alt"] = label_of(p["alt"], lang)
    if "p" in p:
        p["p"] = p_expr(p["p"], lang)
    if "test" in p:
        p["test"] = t(f"test_{p['test']}", lang)
    if "es" in p:
        p["es"] = ES_SYMBOL.get(p["es"], p["es"])
    if "mag" in p:
        p["mag"] = t(f"mag_{p['mag']}", lang)
    for k in ("items", "groups"):
        if k in p:
            p[k] = ", ".join(map(str, p[k]))
    if "pairs" in p:
        p["pairs"] = "; ".join(f"{score_label(a, lang, inst)}–{score_label(b, lang, inst)}" for a, b in p["pairs"])
    return tpl.format(**p)
