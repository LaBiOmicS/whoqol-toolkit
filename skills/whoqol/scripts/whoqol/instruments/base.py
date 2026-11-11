"""Generic definition of a WHOQOL instrument.

Every WHOQOL instrument shares the same scoring logic: items on 1-5 scales, some reverse-coded,
domain (or facet) raw score = mean of the valid items x 4 (range 4-20), transformed score
0-100 = (raw - 4) x 100/16, with a minimum number of valid items per domain and per questionnaire.
A new instrument (WHOQOL-OLD, WHOQOL-100, WHOQOL-HIV-BREF, ...) is a new ``Instrument`` instance.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Domain:
    key: str
    items: tuple[str, ...]
    min_valid: int
    labels: dict[str, str]           # {"pt": ..., "en": ..., "es": ...}
    in_measurement_model: bool = True  # False for global facets (e.g. WHOQOL-BREF Q1-Q2)

    def label(self, lang: str) -> str:
        return self.labels.get(lang) or self.labels["en"]


@dataclass(frozen=True)
class LanguageVersion:
    """A validated language version: used to cite the right adaptation in the methods text."""
    code: str                        # "pt-BR", "es-ES", "en"
    language: str                    # "pt", "es", "en"
    citation: str                    # short in-text citation, e.g. "Fleck et al., 2000"
    reference: str                   # full reference
    description: dict[str, str]      # how the version is described in each report language


@dataclass(frozen=True)
class Instrument:
    key: str                          # registry key, e.g. "whoqol-bref"
    name: str                         # display name, e.g. "WHOQOL-BREF"
    items: tuple[str, ...]
    reversed_items: tuple[str, ...]
    domains: dict[str, Domain]        # scored domains/facets, in display order
    min_valid_total: int
    item_text: dict[str, dict[str, str]]       # lang -> item -> full question
    item_short: dict[str, dict[str, str]]      # lang -> item -> short label
    item_patterns: dict[str, list[str]]        # item -> regexes (normalized text, any language)
    versions: tuple[LanguageVersion, ...]
    primary_reference: str
    description: dict[str, str]               # one-sentence description per report language
    references: tuple[str, ...] = field(default_factory=tuple)
    raw_multiplier: int = 4                   # raw score = mean x 4 (4-20)

    # ------------------------------------------------------------ helpers
    @property
    def model_domains(self) -> list[str]:
        """Domains that form the measurement model (reliability, CFA, HTMT, multitrait)."""
        return [k for k, d in self.domains.items() if d.in_measurement_model]

    @property
    def all_domains(self) -> list[str]:
        return list(self.domains)

    def domain(self, key: str) -> Domain:
        return self.domains[key]

    def domain_label(self, key: str, lang: str) -> str:
        if key in self.domains:
            return self.domains[key].label(lang)
        return key

    def item_label(self, item: str, lang: str) -> str:
        return self.item_short.get(lang, self.item_short["en"]).get(item, item)

    def item_domain(self, item: str) -> str | None:
        for k, d in self.domains.items():
            if item in d.items:
                return k
        return None

    def version_for(self, lang: str | None) -> LanguageVersion | None:
        for v in self.versions:
            if v.language == lang:
                return v
        return None

    def raw_range(self) -> tuple[int, int]:
        return (self.raw_multiplier, 5 * self.raw_multiplier)

    def scoring_markdown(self) -> str:
        """Scoring rules as Markdown (source for the 'scoring' guide; never drifts from the code)."""
        lo, hi = self.raw_range()
        rows = ["| Domain | Items | Min. valid |", "|---|---|---|"]
        for d in self.domains.values():
            items = ", ".join(f"{i}*" if i in self.reversed_items else i for i in d.items)
            note = "" if d.in_measurement_model else " (global facet, outside the measurement model)"
            rows.append(f"| {d.label('en')}{note} | {items} | {d.min_valid} of {len(d.items)} |")
        return "\n".join([
            f"# {self.name} scoring rules", "", *rows, "",
            "\\* reverse-coded: value = 6 - response.", "",
            "- Values outside 1-5 are set to missing.",
            f"- A questionnaire is excluded when fewer than {self.min_valid_total} of the "
            f"{len(self.items)} items are valid.",
            f"- Raw domain score = mean of the valid items x {self.raw_multiplier} (range {lo}-{hi}); "
            "this equals person-mean imputation within the domain.",
            f"- Transformed score 0-100 = (raw - {lo}) x 100/{hi - lo}. Higher = better quality of life.",
            f"- Primary reference: {self.primary_reference}",
            "- Validated language versions recognised: "
            + "; ".join(f"{v.code} ({v.citation})" for v in self.versions) + ".",
        ])
