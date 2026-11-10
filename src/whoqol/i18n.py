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
    "missing_overall": {"pt": "Ausência global", "en": "Overall missingness", "es": "Datos faltantes globales"},
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
}


def t(key: str, lang: str, **kw) -> str:
    s = T[key].get(lang) or T[key][FALLBACK]
    return s.format(**kw) if kw else s


# ---------------------------------------------------------------- flags
# Flags are produced as {"code": ..., **params} by analysis.py and rendered here.
FLAGS: dict[str, dict[str, str]] = {
    "excluded": {
        "pt": "{n} questionário(s) excluído(s) por terem menos de {m} itens válidos (regra da OMS).",
        "en": "{n} questionnaire(s) excluded for having fewer than {m} valid items (WHO rule).",
        "es": "{n} cuestionario(s) excluido(s) por tener menos de {m} ítems válidos (regla de la OMS)."},
    "items_missing": {
        "pt": "Itens com mais de 5% de ausência: {items}.",
        "en": "Items with more than 5% missing: {items}.",
        "es": "Ítems con más del 5% de datos faltantes: {items}."},
    "unrecognized": {
        "pt": "Há respostas não reconhecidas, tratadas como ausentes: revise 'unrecognized_values'.",
        "en": "Some answers were not recognized and were treated as missing: check 'unrecognized_values'.",
        "es": "Hay respuestas no reconocidas, tratadas como faltantes: revise 'unrecognized_values'."},
    "straightlining": {
        "pt": "{n} respondente(s) com a mesma resposta em todos os itens (possível resposta descuidada; "
              "considere análise de sensibilidade).",
        "en": "{n} respondent(s) gave the same answer to every item (possible careless responding; "
              "consider a sensitivity analysis).",
        "es": "{n} encuestado(s) con la misma respuesta en todos los ítems (posible respuesta descuidada; "
              "considere un análisis de sensibilidad)."},
    "duplicates": {
        "pt": "{n} linha(s) com padrão de resposta idêntico a outra (verificar envio duplicado).",
        "en": "{n} row(s) with a response pattern identical to another row (check for duplicate submissions).",
        "es": "{n} fila(s) con un patrón de respuesta idéntico a otra (verificar envíos duplicados)."},
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
    "version_unknown": {
        "pt": "Não foi possível identificar a versão linguística do questionário; informe 'instrument_version' "
              "para citar a validação correta no texto de métodos.",
        "en": "The language version of the questionnaire could not be identified; set 'instrument_version' so "
              "the methods text cites the right validation.",
        "es": "No fue posible identificar la versión lingüística del cuestionario; indique 'instrument_version' "
              "para citar la validación correcta en el texto de métodos."},
}


ES_SYMBOL = {"hedges_g": "g", "rank_biserial_r": "r_rb", "omega2": "ω²", "epsilon2": "ε²",
             "cohen_d": "d", "spearman_rho": "ρ"}


def score_label(key_or_col: str, lang: str, inst) -> str:
    key = key_or_col.replace("_0_100", "").replace("_raw", "")
    if key == "total":
        return t("total_score", lang)
    return inst.domain_label(key, lang)


def render_flag(flag: dict, lang: str, inst) -> str:
    """Localizes a flag {code, **params}: domain keys -> labels, numbers -> local format, codes -> words."""
    tpl = FLAGS[flag["code"]].get(lang) or FLAGS[flag["code"]][FALLBACK]
    p = {k: v for k, v in flag.items() if k != "code"}
    for k in ("domain", "score"):
        if k in p:
            p[k] = score_label(p[k], lang, inst)
    for k in ("a", "cfi", "tli", "rmsea", "srmr"):
        if k in p:
            p[k] = fmt_r(p[k], lang, 3 if k != "a" else 2)
    if "v" in p:
        p["v"] = fmt(p["v"], 2, lang)
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
