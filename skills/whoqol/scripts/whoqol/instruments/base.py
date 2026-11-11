"""Generic definition of a WHOQOL instrument.

All WHOQOL instruments share one scoring grammar, taken from the WHO manuals:

* items are answered on 1-k scales (k = 5, or 3 in the intellectual-disability forms) and some are reverse-coded
  (value = k + 1 - answer);
* an item-based score is ``mean of the valid items x multiplier``. With ``multiplier = 4`` this is the familiar
  4-20 WHOQOL domain/facet score; with ``multiplier = number of items`` it is the sum score of the WHOQOL-OLD,
  WHOQOL-DIS and EUROHIS-QOL manuals (``MEAN.n x k`` in SPSS = sum with person-mean imputation);
* a composite score (WHOQOL-100 / WHOQOL-HIV domains) is the mean of facet scores, some facets reversed
  (``24 - facet`` = low + high - facet);
* every score is also linearly transformed to 0-100 = (raw - low) x 100 / (high - low);
* each score has a minimum number of valid items (or facets), and the questionnaire a minimum number of valid items.

A new instrument is a new ``Instrument`` instance registered in ``instruments/__init__.py``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

ROLES = ("domain", "facet", "global", "total")


@dataclass(frozen=True)
class Domain:
    key: str
    items: tuple[str, ...]
    min_valid: int
    labels: dict[str, str]           # {"pt": ..., "en": ..., "es": ...}; missing languages fall back to English
    role: str = "domain"             # domain | facet (secondary score) | global (overall items) | total
    multiplier: int = 4              # item-based raw score = mean of valid items x multiplier
    facets: tuple[str, ...] = ()     # composite score: mean of these facet scores (``items`` is then empty)
    reversed_facets: tuple[str, ...] = ()

    def __post_init__(self):
        if self.role not in ROLES:
            raise ValueError(f"{self.key}: unknown role {self.role!r}")
        if bool(self.items) == bool(self.facets):
            raise ValueError(f"{self.key}: a score has either items or facets")

    def label(self, lang: str) -> str:
        return self.labels.get(lang) or self.labels["en"]

    @property
    def composite(self) -> bool:
        return bool(self.facets)

    @property
    def in_measurement_model(self) -> bool:
        """Item-based domains/facets enter reliability, multitrait scaling, HTMT and CFA."""
        return self.role in ("domain", "facet") and not self.composite


@dataclass(frozen=True)
class LanguageVersion:
    """A validated language version: used to cite the right adaptation in the methods text."""
    code: str                        # "pt-BR", "es-ES", "en"
    language: str                    # "pt", "es", "en"
    citation: str                    # short in-text citation, e.g. "Fleck et al., 2000"
    reference: str                   # full reference
    description: dict[str, str]      # how the version is described in each report language


def code_key(s: str) -> str:
    """Canonical form of an item code for header matching: 'F1_1' / 'f1.1' -> 'f1.1'; 'old_01' -> 'old.1'."""
    s = re.sub(r"\s+", "", str(s).strip().lower()).replace("_", ".").replace("-", ".")
    s = re.sub(r"(?<=[a-z])\.?0*(\d)", r".\1", s, count=1)          # 'old01' / 'old.01' -> 'old.1'
    return re.sub(r"\.0+(\d)", r".\1", s)


@dataclass(frozen=True)
class Instrument:
    key: str                          # registry key, e.g. "whoqol-bref"
    name: str                         # display name, e.g. "WHOQOL-BREF"
    items: tuple[str, ...]
    reversed_items: tuple[str, ...]
    domains: dict[str, Domain]        # all scores, facets before the composites that use them, in display order
    min_valid_total: int
    item_text: dict[str, dict[str, str]]       # lang -> item -> full question
    item_short: dict[str, dict[str, str]]      # lang -> item -> short label
    item_patterns: dict[str, list[str]]        # item -> regexes (normalized text, any language)
    versions: tuple[LanguageVersion, ...]
    primary_reference: str
    description: dict[str, str]               # one-sentence description per report language
    references: tuple[str, ...] = field(default_factory=tuple)
    scale_max: int = 5                         # answers 1..scale_max
    item_scale: dict[str, int] = field(default_factory=dict)   # per-item exceptions to scale_max
    number_map: dict[int, str] | None = None   # questionnaire number -> item (default: position in ``items``)
    number_note: str = ""                      # caveat shown when items were matched by number
    item_codes: dict[str, tuple[str, ...]] = field(default_factory=dict)  # item -> extra header codes
    derived_from: tuple[str, dict[str, str]] | None = None   # (instrument key, {item: item of that instrument})
    scoring_source: str = ""                   # where the scoring rules come from (shown in the scoring guide)
    notes: tuple[str, ...] = field(default_factory=tuple)    # source discrepancies and conventions adopted
    methods_note: dict[str, str] = field(default_factory=dict)  # convention sentence appended to the methods text

    def __post_init__(self):
        seen: set[str] = set()
        for k, d in self.domains.items():
            if k != d.key:
                raise ValueError(f"domain key mismatch: {k} != {d.key}")
            unknown = [i for i in d.items if i not in self.items] + [f for f in d.facets if f not in seen]
            if unknown:
                raise ValueError(f"{self.key}/{k}: unknown items or facets not defined earlier: {unknown}")
            if d.items and len({self.item_max(i) for i in d.items}) != 1:
                raise ValueError(f"{self.key}/{k}: items on different response scales")
            if d.composite and len({self.domain_range(f) for f in d.facets}) != 1:
                raise ValueError(f"{self.key}/{k}: facets with different ranges")
            seen.add(k)
        if bad := [i for i in self.reversed_items if i not in self.items]:
            raise ValueError(f"{self.key}: unknown reversed items {bad}")

    # ------------------------------------------------------------ structure
    @property
    def model_domains(self) -> list[str]:
        """Item-based scores forming the measurement model (reliability, CFA, HTMT, multitrait)."""
        return [k for k, d in self.domains.items() if d.in_measurement_model]

    @property
    def primary_domains(self) -> list[str]:
        """Main domain scores (regression, convergent validity, results text)."""
        return [k for k, d in self.domains.items() if d.role == "domain"]

    @property
    def reported_domains(self) -> list[str]:
        """Scores in the descriptive/comparison tables: domains, overall items and official totals (not facets of
        hierarchical instruments, which are exported in the scores file)."""
        return [k for k, d in self.domains.items() if d.role != "facet"]

    @property
    def all_domains(self) -> list[str]:
        return list(self.domains)

    @property
    def hierarchical(self) -> bool:
        return any(d.composite for d in self.domains.values())

    def domain(self, key: str) -> Domain:
        return self.domains[key]

    def domain_label(self, key: str, lang: str) -> str:
        if key in self.domains:
            return self.domains[key].label(lang)
        return key

    def item_label(self, item: str, lang: str) -> str:
        short = self.item_short.get(lang) or {}
        if item in short:
            return short[item]
        en = self.item_short.get("en") or {}
        if item in en:
            return en[item]
        dom = self.item_domain(item)
        return self.domain_label(dom, lang) if dom else item

    def item_domain(self, item: str) -> str | None:
        """First score that uses the item (its facet in hierarchical instruments)."""
        for k, d in self.domains.items():
            if item in d.items and d.role != "total":
                return k
        return None

    def version_for(self, lang: str | None) -> LanguageVersion | None:
        for v in self.versions:
            if v.language == lang:
                return v
        return None

    # --------------------------------------------------------------- scales
    def item_max(self, item: str) -> int:
        return self.item_scale.get(item, self.scale_max)

    def domain_range(self, key: str) -> tuple[float, float]:
        d = self.domains[key]
        if d.composite:
            return self.domain_range(d.facets[0])
        return (d.multiplier * 1, d.multiplier * self.item_max(d.items[0]))

    def raw_range(self) -> tuple[float, float]:
        """Range of the first main domain (kept for single-range instruments such as the WHOQOL-BREF)."""
        return self.domain_range((self.primary_domains or self.all_domains)[0])

    @property
    def single_range(self) -> bool:
        return len({self.domain_range(k) for k in self.reported_domains}) == 1

    @property
    def psychometric_reversed(self) -> tuple[str, ...]:
        """Items to reverse so that every item points to better QoL: the reversed items, flipped again for items of
        facets that are reversed at domain level (WHOQOL-100 pain, negative feelings, ...)."""
        flip = {f for d in self.domains.values() for f in d.reversed_facets}
        in_flip = {i for f in flip for i in self.domains[f].items}
        return tuple(i for i in self.items if (i in self.reversed_items) != (i in in_flip))

    def numbering(self) -> dict[int, str]:
        return self.number_map if self.number_map is not None else {n: it for n, it in enumerate(self.items, 1)}

    def header_codes(self) -> dict[str, str]:
        """Canonical header code -> item (item ids themselves and the declared aliases)."""
        out = {code_key(it): it for it in self.items}
        for it, codes in self.item_codes.items():
            for c in codes:
                out[code_key(c)] = it
        return out

    # ------------------------------------------------------------- docs
    def scoring_markdown(self) -> str:
        """Scoring rules as Markdown (source for the 'scoring' guide; never drifts from the code)."""
        rows = ["| Score | Role | Items / facets | Min. valid | Raw score | Raw range |", "|---|---|---|---|---|---|"]
        for k, d in self.domains.items():
            lo, hi = self.domain_range(k)
            if d.composite:
                parts = ", ".join(f"{f}*" if f in d.reversed_facets else f for f in d.facets)
                rule = "mean of facet scores"
                minv = f"{d.min_valid} of {len(d.facets)} facets"
            else:
                parts = ", ".join(f"{i}*" if i in self.reversed_items else i for i in d.items)
                rule = (f"sum of items (mean x {d.multiplier})" if d.multiplier == len(d.items) and len(d.items) > 1
                        else f"mean x {d.multiplier}")
                minv = f"{d.min_valid} of {len(d.items)}"
            rows.append(f"| {d.label('en')} (`{k}`) | {d.role} | {parts} | {minv} | {rule} | {lo:g}-{hi:g} |")
        scales = f"1-{self.scale_max}"
        if self.item_scale:
            other = sorted(set(self.item_scale.values()))
            scales += "; " + "; ".join(f"1-{m} for " + ", ".join(i for i, v in self.item_scale.items() if v == m)
                                       for m in other)
        lines = [f"# {self.name} scoring rules", ""]
        if self.scoring_source:
            lines += [f"Source: {self.scoring_source}", ""]
        lines += [*rows, "",
                  "\\* item reverse-coded (value = scale maximum + 1 - answer) or, for facets inside a composite "
                  "score, facet reversed (value = low + high - facet, i.e. 24 - facet).", "",
                  f"- Response scales: {scales}. Values outside the scale are set to missing.",
                  f"- A questionnaire is excluded when fewer than {self.min_valid_total} of the "
                  f"{len(self.items)} items are valid.",
                  "- Item-based scores use person-mean imputation within the score (SPSS `MEAN.n`).",
                  "- Transformed score 0-100 = (raw - low) x 100/(high - low). Higher = better quality of life.",
                  f"- Primary reference: {self.primary_reference}"]
        if self.versions:
            lines.append("- Validated language versions recognised: "
                         + "; ".join(f"{v.code} ({v.citation})" for v in self.versions) + ".")
        if self.number_note:
            lines.append(f"- Numbered headers (Q1, item 1, ...): {self.number_note}")
        if self.derived_from:
            lines.append(f"- Can be scored from a {self.derived_from[0]} spreadsheet: "
                         + ", ".join(f"{a} = {b}" for a, b in self.derived_from[1].items()) + ".")
        if self.notes:
            lines += ["", "## Notes on the sources", "", *[f"- {n}" for n in self.notes]]
        return "\n".join(lines)
