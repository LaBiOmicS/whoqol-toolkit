"""Generates SYNTHETIC example spreadsheets (not real data) for the WHOQOL-BREF.

- sample_google_forms_pt.xlsx: question text as headers, text answers in Portuguese (Google Forms style)
- sample_forms_es.xlsx: the same in Spanish
- sample_numeric.csv: columns Q1..Q26 with values 1-5
"""
from pathlib import Path

import numpy as np
import pandas as pd

from whoqol.instruments import get_instrument

inst = get_instrument("whoqol-bref")
rng = np.random.default_rng(42)
N = 300
ANCHORS = {
    "pt": {"eval": ["Muito ruim", "Ruim", "Nem ruim nem boa", "Boa", "Muito boa"],
           "eval_m": ["Muito ruim", "Ruim", "Nem ruim nem bom", "Bom", "Muito bom"],
           "sat": ["Muito insatisfeito", "Insatisfeito", "Nem satisfeito nem insatisfeito", "Satisfeito",
                   "Muito satisfeito"],
           "int": ["Nada", "Muito pouco", "Mais ou menos", "Bastante", "Extremamente"],
           "cap": ["Nada", "Muito pouco", "Médio", "Muito", "Completamente"],
           "freq": ["Nunca", "Algumas vezes", "Frequentemente", "Muito frequentemente", "Sempre"]},
    "es": {"eval": ["Muy mal", "Poco", "Lo normal", "Bastante bien", "Muy bien"],
           "eval_m": ["Nada", "Un poco", "Lo normal", "Bastante", "Extremadamente"],
           "sat": ["Muy insatisfecho", "Poco", "Lo normal", "Bastante satisfecho", "Muy satisfecho"],
           "int": ["Nada", "Un poco", "Lo normal", "Bastante", "Extremadamente"],
           "cap": ["Nada", "Un poco", "Moderado", "Bastante", "Totalmente"],
           "freq": ["Nunca", "Raramente", "Medianamente", "Frecuentemente", "Siempre"]},
}
SCALE = {"Q1": "eval", "Q2": "sat", "Q15": "eval_m", "Q26": "freq"}
SCALE.update({f"Q{i}": "int" for i in range(3, 10)})
SCALE.update({f"Q{i}": "cap" for i in range(10, 15)})
SCALE.update({f"Q{i}": "sat" for i in range(16, 26)})

sex = rng.choice(["F", "M"], N, p=[0.6, 0.4])
age = rng.integers(18, 80, N)
edu = rng.choice([1, 2, 3], N, p=[0.25, 0.45, 0.30])  # 1 primary, 2 secondary, 3 higher
model = inst.model_domains
cov = np.full((len(model), len(model)), 0.55) + np.eye(len(model)) * 0.45
lat = rng.multivariate_normal(np.zeros(len(model)), cov, N)
lat[:, 0] -= (age - 48) / 40                 # physical declines with age
lat[:, 1] += np.where(sex == "M", 0.3, 0)    # psychological slightly higher in men
lat[:, 3] += np.select([edu == 1, edu == 3], [-0.5, 0.4], 0)  # environment rises with education

resp = {}
for it in inst.items:
    dk = inst.item_domain(it)
    base = lat.mean(axis=1) * 0.8 if dk not in model else lat[:, model.index(dk)]
    v = np.clip(np.round(3.4 + 0.75 * base + rng.normal(0, 0.66, N)), 1, 5).astype(int)
    resp[it] = 6 - v if it in inst.reversed_items else v
num = pd.DataFrame(resp).astype(float)
for it in inst.items:  # missing answers: more refusals for Q21 (sex life)
    num.loc[rng.random(N) < (0.08 if it == "Q21" else 0.01), it] = np.nan
num.loc[[5, 17, 99], list(inst.items[:8])] = np.nan  # three questionnaires with > 20% missing
num.loc[42, list(inst.items)] = 3                       # a straight-liner

out = Path(__file__).parent
demo = pd.DataFrame({"ID": range(1, N + 1), "Sexo": sex, "Idade": age, "Escolaridade": edu})
pd.concat([demo, num], axis=1).to_csv(out / "sample_numeric.csv", index=False)

for lang, fname, cols in [("pt", "sample_google_forms_pt.xlsx", {"Sexo": "Sexo", "Idade": "Idade",
                                                                   "Escolaridade": "Escolaridade"}),
                          ("es", "sample_forms_es.xlsx", {"Sexo": "Sexo", "Idade": "Edad",
                                                          "Escolaridade": "Nivel educativo"})]:
    txt = pd.DataFrame({f"{int(it[1:])}. {inst.item_text[lang][it]}":
                        [ANCHORS[lang][SCALE[it]][int(x) - 1] if pd.notna(x) else None for x in num[it]]
                        for it in inst.items})
    stamp = "Carimbo de data/hora" if lang == "pt" else "Marca temporal"
    txt.insert(0, stamp, pd.Timestamp("2026-03-01") + pd.to_timedelta(rng.integers(0, 10**6, N), "s"))
    forms = pd.concat([txt, demo.drop(columns="ID").rename(columns=cols)], axis=1)
    # Google Forms often drops the numbering: strip it from a few headers
    forms.columns = [c.split(". ", 1)[1] if c[:2] in ("4.", "9.") else c for c in forms.columns]
    forms.to_excel(out / fname, index=False)
print("ok")
