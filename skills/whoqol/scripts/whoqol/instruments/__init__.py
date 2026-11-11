"""Registry of WHOQOL instruments. Add a new instrument by defining an ``Instrument`` and registering it here."""

from __future__ import annotations

from .base import Domain, Instrument, LanguageVersion
from .eurohis import EUROHIS_QOL_8
from .whoqol_100 import WHOQOL_100, WHOQOL_100_BREF, WHOQOL_100_SRPB, WHOQOL_HIV
from .whoqol_bref import WHOQOL_BREF
from .whoqol_dis import WHOQOL_DIS, WHOQOL_DIS_BR, WHOQOL_DIS_ID, WHOQOL_DIS_ID_BR, WHOQOL_DIS_ID_PROXY
from .whoqol_hiv_bref import WHOQOL_HIV_BREF
from .whoqol_old import WHOQOL_OLD
from .whoqol_srpb import WHOQOL_SRPB, WHOQOL_SRPB_BREF

REGISTRY: dict[str, Instrument] = {i.key: i for i in (
    WHOQOL_BREF, WHOQOL_OLD, EUROHIS_QOL_8, WHOQOL_HIV_BREF, WHOQOL_SRPB_BREF, WHOQOL_SRPB, WHOQOL_DIS, WHOQOL_DIS_ID,
    WHOQOL_DIS_BR, WHOQOL_DIS_ID_BR, WHOQOL_DIS_ID_PROXY, WHOQOL_100, WHOQOL_HIV, WHOQOL_100_SRPB, WHOQOL_100_BREF)}
ALIASES = {"bref": "whoqol-bref", "whoqol bref": "whoqol-bref", "whoqol_bref": "whoqol-bref",
           "old": "whoqol-old", "eurohis": "eurohis-qol-8", "eurohis-qol": "eurohis-qol-8", "whoqol-8": "eurohis-qol-8",
           "hiv-bref": "whoqol-hiv-bref", "srpb-bref": "whoqol-srpb-bref", "srpb": "whoqol-srpb",
           "dis": "whoqol-dis", "whoqol-dis-pd": "whoqol-dis", "dis-id": "whoqol-dis-id", "100": "whoqol-100",
           "hiv": "whoqol-hiv", "whoqol-hiv-120": "whoqol-hiv", "whoqol-120-hiv": "whoqol-hiv",
           "100-srpb": "whoqol-100-srpb", "dis-br": "whoqol-dis-br", "dis-id-br": "whoqol-dis-id-br",
           "dis-proxy": "whoqol-dis-id-proxy", "dis-id-proxy": "whoqol-dis-id-proxy", "100-bref": "whoqol-100-bref",
           "whoqol-100-4d": "whoqol-100-bref"}
DEFAULT = "whoqol-bref"


def get_instrument(key: str | Instrument | None = None) -> Instrument:
    if isinstance(key, Instrument):
        return key
    k = (key or DEFAULT).strip().lower()
    k = ALIASES.get(k.replace("_", "-"), k.replace("_", "-"))
    if k not in REGISTRY:
        raise ValueError(f"Unknown instrument {key!r}. Available: {', '.join(REGISTRY)}")
    return REGISTRY[k]


def available() -> list[dict]:
    return [{"key": i.key, "name": i.name, "items": len(i.items), "scale": f"1-{i.scale_max}",
             "scores": [d.label("en") for d in i.domains.values() if d.role != "facet"],
             "facets": len([d for d in i.domains.values() if d.role == "facet"]),
             "versions": [v.code for v in i.versions]} for i in REGISTRY.values()]


__all__ = ["Domain", "Instrument", "LanguageVersion", "REGISTRY", "get_instrument", "available", "DEFAULT"]
