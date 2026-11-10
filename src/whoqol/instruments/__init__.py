"""Registry of WHOQOL instruments. Add a new instrument by defining an ``Instrument`` and registering it here."""

from __future__ import annotations

from .base import Domain, Instrument, LanguageVersion
from .whoqol_bref import WHOQOL_BREF

REGISTRY: dict[str, Instrument] = {
    WHOQOL_BREF.key: WHOQOL_BREF,
}
ALIASES = {"bref": "whoqol-bref", "whoqol bref": "whoqol-bref", "whoqol_bref": "whoqol-bref"}
DEFAULT = "whoqol-bref"


def get_instrument(key: str | Instrument | None = None) -> Instrument:
    if isinstance(key, Instrument):
        return key
    k = (key or DEFAULT).strip().lower()
    k = ALIASES.get(k, k)
    if k not in REGISTRY:
        raise ValueError(f"Unknown instrument {key!r}. Available: {', '.join(REGISTRY)}")
    return REGISTRY[k]


def available() -> list[dict]:
    return [{"key": i.key, "name": i.name, "items": len(i.items),
             "domains": [d.label("en") for d in i.domains.values()],
             "versions": [v.code for v in i.versions]} for i in REGISTRY.values()]


__all__ = ["Domain", "Instrument", "LanguageVersion", "REGISTRY", "get_instrument", "available", "DEFAULT"]
