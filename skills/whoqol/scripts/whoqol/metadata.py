"""OPTIONAL data dictionary (metadata), in Portuguese, English or Spanish.

A spreadsheet (.xlsx) with a "variables" sheet (required) and a "study" sheet (optional), or the
equivalent JSON. It can also be a sheet inside the data workbook (data on the first sheet).

"variables" sheet, one row per column of the data:
  column          exact column name                  (pt: coluna        es: columna)
  role            item | id | group | continuous | covariate | ignore
                                                     (pt: item|id|grupo|continua|covariavel|ignorar;
                                                      es: item|id|grupo|continua|covariable|ignorar)
  item            Q1..Qk when role = item            (pt/es: item)
  label           readable name for tables/figures   (pt: rotulo        es: etiqueta)
  value_labels    "1=Female; 2=Male"                 (pt: rotulos_valores  es: etiquetas_valores)
  level_order     "Primary; Secondary; Higher"       (pt: ordem_niveis  es: orden_niveles)
  missing_codes   "99; -9; DK"                       (pt: codigos_ausentes es: codigos_faltantes)

"study" sheet: key/value pairs (title, objective, population, country, language version, design,
administration mode, ...). They are passed to the LLM to put the interpretation in context.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from .anchors import normalize_text
from .instruments import Instrument, get_instrument

ROLES = ("item", "id", "group", "continuous", "covariate", "ignore")
_ROLE_ALIASES = {
    "item": "item", "whoqol": "item", "id": "id", "identificador": "id", "identifier": "id",
    "group": "group", "grupo": "group", "categorica": "group", "categorico": "group", "categorical": "group",
    "continuous": "continuous", "continua": "continuous", "continuo": "continuous", "numerica": "continuous",
    "numeric": "continuous",
    "covariate": "covariate", "covariavel": "covariate", "covariable": "covariate", "ajuste": "covariate",
    "ignore": "ignore", "ignorar": "ignore", "": "ignore",
}
_COLUMN_ALIASES = {
    "column": "column", "coluna": "column", "columna": "column", "variable": "column", "variavel": "column",
    "role": "role", "papel": "role", "rol": "role",
    "item": "item", "item_whoqol": "item", "whoqol_item": "item",
    "label": "label", "rotulo": "label", "etiqueta": "label",
    "value_labels": "value_labels", "rotulos_valores": "value_labels", "etiquetas_valores": "value_labels",
    "level_order": "level_order", "ordem_niveis": "level_order", "orden_niveles": "level_order",
    "missing_codes": "missing_codes", "codigos_ausentes": "missing_codes", "codigos_faltantes": "missing_codes",
}
VAR_SHEETS = ("variables", "variaveis", "metadata", "metadados", "metadatos", "dicionario", "diccionario",
              "codebook", "dictionary")
STUDY_SHEETS = ("study", "estudo", "estudio")

# Localized template (headers, roles, sheet names, study keys, help text)
TEMPLATE = {
    "pt": {"sheets": ("variaveis", "estudo", "instrucoes"),
           "cols": ("coluna", "papel", "item", "rotulo", "rotulos_valores", "ordem_niveis", "codigos_ausentes"),
           "roles": {"item": "item", "id": "id", "group": "grupo", "continuous": "continua",
                     "covariate": "covariavel", "ignore": "ignorar"},
           "study_cols": ("chave", "valor", "exemplo"),
           "study": [("titulo", ""), ("objetivo", "ex.: comparar a QV entre turnos de trabalho"),
                     ("populacao", "ex.: idosos da comunidade; estudantes de enfermagem"), ("pais", "ex.: Brasil"),
                     ("versao_idioma", "ex.: português brasileiro (Fleck et al., 2000)"),
                     ("desenho", "ex.: transversal; coorte; ensaio clínico (linha de base)"),
                     ("modo_aplicacao", "ex.: autoaplicado online; entrevista"), ("periodo_coleta", ""),
                     ("amostragem", "ex.: conveniência; probabilística"), ("observacoes", "")],
           "help": [("papel", "item | id | grupo | continua | covariavel | ignorar"),
                    ("item", "Q1..Qk para as colunas do questionário"),
                    ("rotulos_valores", "Ex.: 1=Feminino; 2=Masculino"),
                    ("ordem_niveis", "Ordem das categorias em tabelas e figuras. Ex.: Fundamental; Médio; Superior"),
                    ("codigos_ausentes", "Valores que significam ausência. Ex.: 99; -9; Não sei"),
                    ("estudo", "Preencha a aba 'estudo': ajuda a interpretar (população, desenho, normas).")],
           "help_cols": ("campo", "instrucao")},
    "en": {"sheets": ("variables", "study", "instructions"),
           "cols": ("column", "role", "item", "label", "value_labels", "level_order", "missing_codes"),
           "roles": {r: r for r in ROLES},
           "study_cols": ("key", "value", "example"),
           "study": [("title", ""), ("objective", "e.g. compare QoL across work shifts"),
                     ("population", "e.g. community-dwelling older adults; nursing students"),
                     ("country", "e.g. Brazil"), ("language_version", "e.g. Brazilian Portuguese (Fleck et al., 2000)"),
                     ("design", "e.g. cross-sectional; cohort; clinical trial (baseline)"),
                     ("administration", "e.g. self-administered online; interview"), ("data_collection_period", ""),
                     ("sampling", "e.g. convenience; probability"), ("notes", "")],
           "help": [("role", "item | id | group | continuous | covariate | ignore"),
                    ("item", "Q1..Qk for the questionnaire columns"),
                    ("value_labels", "e.g. 1=Female; 2=Male"),
                    ("level_order", "Order of the categories in tables and figures. e.g. Primary; Secondary; Higher"),
                    ("missing_codes", "Values that mean missing. e.g. 99; -9; Don't know"),
                    ("study", "Fill in the 'study' sheet: it helps the interpretation (population, design, norms).")],
           "help_cols": ("field", "instruction")},
    "es": {"sheets": ("variables", "estudio", "instrucciones"),
           "cols": ("columna", "rol", "item", "etiqueta", "etiquetas_valores", "orden_niveles", "codigos_faltantes"),
           "roles": {"item": "item", "id": "id", "group": "grupo", "continuous": "continua",
                     "covariate": "covariable", "ignore": "ignorar"},
           "study_cols": ("clave", "valor", "ejemplo"),
           "study": [("titulo", ""), ("objetivo", "ej.: comparar la CV entre turnos de trabajo"),
                     ("poblacion", "ej.: adultos mayores de la comunidad; estudiantes de enfermería"),
                     ("pais", "ej.: España"), ("version_idioma", "ej.: versión española (Lucas, 1998)"),
                     ("diseno", "ej.: transversal; cohorte; ensayo clínico (línea de base)"),
                     ("modo_aplicacion", "ej.: autoadministrado en línea; entrevista"), ("periodo_recogida", ""),
                     ("muestreo", "ej.: conveniencia; probabilístico"), ("observaciones", "")],
           "help": [("rol", "item | id | grupo | continua | covariable | ignorar"),
                    ("item", "Q1..Qk para las columnas del cuestionario"),
                    ("etiquetas_valores", "Ej.: 1=Mujer; 2=Hombre"),
                    ("orden_niveles", "Orden de las categorías en tablas y figuras. Ej.: Primaria; Secundaria; Superior"),
                    ("codigos_faltantes", "Valores que significan dato faltante. Ej.: 99; -9; No sabe"),
                    ("estudio", "Complete la hoja 'estudio': ayuda a interpretar (población, diseño, normas).")],
           "help_cols": ("campo", "instruccion")},
}
_EXAMPLE_PREFIXES = ("ex.:", "e.g.", "ej.:")


def _split(s) -> list[str]:
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return []
    return [p.strip() for p in re.split(r"[;|\n]", str(s)) if p.strip()]


def _parse_value_labels(s) -> dict[str, str]:
    out = {}
    for part in _split(s):
        if "=" in part:
            k, v = part.split("=", 1)
            out[_norm_key(k)] = v.strip()
    return out


def _norm_key(v) -> str:
    """'1', 1, 1.0 -> '1', so numeric codes match their labels."""
    try:
        f = float(v)
        return str(int(f)) if f.is_integer() else str(f)
    except (TypeError, ValueError):
        return str(v).strip()


def _find_sheet(names: dict[str, str], options) -> str | None:
    return next((names[n] for n in options if n in names), None)


def load_metadata(path: str | Path, instrument: str | Instrument | None = None) -> dict:
    path = Path(path).expanduser()
    if path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw = {normalize_text(k): v for k, v in raw.items()}
        vars_df = pd.DataFrame(next((raw[k] for k in VAR_SHEETS if k in raw), []))
        study = next((raw[k] for k in STUDY_SHEETS if k in raw), {})
    else:
        xl = pd.ExcelFile(path)
        names = {normalize_text(n): n for n in xl.sheet_names}
        sheet = _find_sheet(names, VAR_SHEETS)
        if sheet is None:
            raise ValueError(f"No metadata sheet found (use one of: {', '.join(VAR_SHEETS)}).")
        vars_df = pd.read_excel(xl, sheet)
        study = {}
        ssheet = _find_sheet(names, STUDY_SHEETS)
        if ssheet:
            s = pd.read_excel(xl, ssheet, header=None).dropna(how="all")
            for _, r in s.iterrows():
                if len(r) < 2 or pd.isna(r.iloc[0]) or pd.isna(r.iloc[1]):
                    continue
                k, v = str(r.iloc[0]).strip(), str(r.iloc[1]).strip()
                if not v or normalize_text(k) in ("chave", "key", "clave", "campo", "field") \
                        or v.lower().startswith(_EXAMPLE_PREFIXES):
                    continue
                study[k] = v
    return parse_variables(vars_df, study, instrument)


def parse_variables(vars_df: pd.DataFrame, study: dict | None = None,
                    instrument: str | Instrument | None = None) -> dict:
    inst = get_instrument(instrument)
    vars_df = vars_df.rename(columns=lambda c: _COLUMN_ALIASES.get(normalize_text(c).replace(" ", "_"),
                                                                     normalize_text(c).replace(" ", "_")))
    if "column" not in vars_df:
        raise ValueError("The variables sheet needs a 'column' (coluna/columna) column.")
    meta = {"mapping": {}, "id_column": None, "group_vars": [], "continuous_vars": [], "covariates": [],
            "ignore": [], "labels": {}, "value_labels": {}, "level_order": {}, "missing_codes": {},
            "study": study or {}, "warnings": []}

    def cell(r, k):
        v = r.get(k, np.nan)
        return None if v is None or (isinstance(v, float) and np.isnan(v)) else v

    for _, r in vars_df.iterrows():
        col = cell(r, "column")
        if col is None:
            continue
        col = str(col).strip()
        role_raw = normalize_text(cell(r, "role") or "")
        role = _ROLE_ALIASES.get(role_raw)
        if role is None:
            meta["warnings"].append(f"Unknown role for '{col}': {role_raw!r} (use one of {list(ROLES)}).")
            continue
        if role == "item":
            from .io import resolve_item_key
            item = resolve_item_key(cell(r, "item") or "", inst)
            if item is None:
                meta["warnings"].append(f"'{col}' has role 'item' but no valid item id of {inst.name} "
                                        f"({inst.items[0]} ... {inst.items[-1]}).")
                continue
            if item in meta["mapping"]:
                meta["warnings"].append(f"Item {item} assigned to more than one column.")
            meta["mapping"][item] = col
        elif role == "id":
            meta["id_column"] = col
        elif role == "group":
            meta["group_vars"].append(col)
        elif role == "continuous":
            meta["continuous_vars"].append(col)
        elif role == "covariate":
            meta["covariates"].append(col)
        else:
            meta["ignore"].append(col)
        if cell(r, "label") and str(cell(r, "label")).strip():
            meta["labels"][col] = str(cell(r, "label")).strip()
        if vl := _parse_value_labels(cell(r, "value_labels")):
            meta["value_labels"][col] = vl
        if order := _split(cell(r, "level_order")):
            meta["level_order"][col] = order
        if mc := _split(cell(r, "missing_codes")):
            meta["missing_codes"][col] = mc
    return meta


def find_embedded(path: str | Path, instrument: str | Instrument | None = None) -> dict | None:
    """A metadata sheet inside the data workbook itself."""
    path = Path(path).expanduser()
    if path.suffix.lower() not in {".xlsx", ".xlsm", ".xls", ".ods"}:
        return None
    names = {normalize_text(n) for n in pd.ExcelFile(path).sheet_names}
    if any(n in names for n in VAR_SHEETS):
        return load_metadata(path, instrument)
    return None


def apply_to_raw(raw: pd.DataFrame, meta: dict) -> pd.DataFrame:
    """Applies missing codes and value labels to the NON-item columns."""
    df = raw.copy()
    item_cols = set(meta.get("mapping", {}).values())
    for col, codes in meta.get("missing_codes", {}).items():
        if col in df:
            keys = {_norm_key(c) for c in codes}
            df[col] = df[col].where(~df[col].map(_norm_key).isin(keys))
    for col, labels in meta.get("value_labels", {}).items():
        if col in df and col not in item_cols:
            df[col] = df[col].map(lambda v, lab=labels: lab.get(_norm_key(v), v) if pd.notna(v) else v)
    return df


def guess_role(name: str, s: pd.Series) -> str:
    """Heuristic: id | continuous | group | ignore (dates, free text)."""
    nun = s.nunique(dropna=True)
    nc = normalize_text(name)
    if pd.api.types.is_datetime64_any_dtype(s) or nc.startswith(
            ("carimbo", "timestamp", "data", "date", "hora", "fecha", "marca temporal")):
        return "ignore"
    num = pd.to_numeric(s, errors="coerce")
    looks_id = bool(re.fullmatch(r"(id|codigo|cod|registro|participante|sujeito|sujeto|record id|n)( .*)?", nc))
    if looks_id or (nun == s.notna().sum() and nun > 10 and num.notna().mean() < 0.9):
        return "id"
    if num.notna().mean() > 0.9 and nun > 10:
        return "continuous"
    if 2 <= nun <= 10:
        return "group"
    return "ignore"


def generate_template(data_path: str | Path, out_path: str | Path | None = None, sheet=None,
                      instrument: str | Instrument | None = None, lang: str = "en") -> str:
    """Pre-filled dictionary from the automatic detection, in the requested language."""
    from .io import detect_mapping, load_table

    tpl = TEMPLATE.get(lang, TEMPLATE["en"])
    c_col, c_role, c_item, c_label, c_vl, c_order, c_miss = tpl["cols"]
    df = load_table(data_path, sheet)
    det = detect_mapping(df, instrument)
    inv = {v: k for k, v in det["mapping"].items()}
    rows = []
    for c in df.columns:
        s = df[c]
        if c in inv:
            rows.append({c_col: c, c_role: tpl["roles"]["item"], c_item: inv[c], c_label: "", c_vl: "",
                         c_order: "", c_miss: ""})
            continue
        role = guess_role(c, s)
        levels = [str(v) for v in s.dropna().unique()] if role == "group" else []
        rows.append({c_col: c, c_role: tpl["roles"][role], c_item: "", c_label: c, c_vl: "",
                     c_order: "; ".join(sorted(levels)), c_miss: ""})
    suffix = {"pt": "_metadados", "es": "_metadatos"}.get(lang, "_metadata")
    out = Path(out_path) if out_path else Path(data_path).expanduser().with_name(Path(data_path).stem + suffix + ".xlsx")
    s_vars, s_study, s_help = tpl["sheets"]
    with pd.ExcelWriter(out, engine="openpyxl") as xw:
        pd.DataFrame(rows).to_excel(xw, sheet_name=s_vars, index=False)
        pd.DataFrame([(k, "", ex) for k, ex in tpl["study"]], columns=tpl["study_cols"]).to_excel(
            xw, sheet_name=s_study, index=False)
        pd.DataFrame(tpl["help"], columns=tpl["help_cols"]).to_excel(xw, sheet_name=s_help, index=False)
    return str(out)
