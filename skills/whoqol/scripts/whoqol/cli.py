"""Command line: whoqol {instruments,inspect,template,score,analyze,guide}."""

from __future__ import annotations

import argparse
import sys

from . import __version__, service


def _sheet(v):
    return int(v) if v is not None and str(v).isdigit() else v


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="whoqol", description="Scoring and analysis of WHOQOL questionnaires")
    p.add_argument("--version", action="version", version=f"whoqol-toolkit {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("instruments", help="list supported instruments")

    def common(sp):
        sp.add_argument("path")
        sp.add_argument("-i", "--instrument", default="whoqol-bref")
        sp.add_argument("--sheet")

    i = sub.add_parser("inspect", help="detect item columns, language version and other variables")
    common(i)
    i.add_argument("--metadata")

    tp = sub.add_parser("template", help="create a pre-filled data dictionary")
    common(tp)
    tp.add_argument("-o", "--output")
    tp.add_argument("--lang", choices=["pt", "en", "es"], default="en")

    s = sub.add_parser("score", help="score only and save a spreadsheet")
    common(s)
    s.add_argument("-o", "--output")
    s.add_argument("--mapping", help='JSON or .json file {"Q1": "column", ...}')
    s.add_argument("--include-total", action="store_true")

    a = sub.add_parser("analyze", help="full analysis for publication")
    common(a)
    a.add_argument("-o", "--output-dir")
    a.add_argument("--mapping")
    a.add_argument("--id-column")
    a.add_argument("-g", "--group", action="append", default=[], help="grouping variable (repeatable)")
    a.add_argument("-c", "--continuous", action="append", default=[], help="continuous variable (repeatable)")
    a.add_argument("--covariate", action="append", default=[], help="regression covariate (repeatable)")
    a.add_argument("--reference", help="JSON or .json file with reference means per domain")
    a.add_argument("--method", choices=["auto", "parametric", "nonparametric"], default="auto")
    a.add_argument("--cutoff", type=float)
    a.add_argument("--include-total", action="store_true")
    a.add_argument("--no-cfa", action="store_true")
    a.add_argument("--lang", choices=["auto", "pt", "en", "es"], default="auto", help="report language")
    a.add_argument("--instrument-version", choices=["auto", "pt", "en", "es", "other"], default="auto")
    a.add_argument("--metadata", help="data dictionary (.xlsx/.json)")

    gd = sub.add_parser("guide", help="show a methodological guide")
    gd.add_argument("topic", nargs="?", default="workflow", choices=service.GUIDE_TOPICS)
    gd.add_argument("-i", "--instrument", default="whoqol-bref")

    args = p.parse_args(argv)
    if args.cmd == "instruments":
        out = service.instruments()
    elif args.cmd == "inspect":
        out = service.inspect(args.path, args.instrument, _sheet(args.sheet), args.metadata)
    elif args.cmd == "template":
        out = service.template(args.path, args.output, args.instrument, _sheet(args.sheet), args.lang)
    elif args.cmd == "score":
        out = service.score_only(args.path, args.output, args.instrument, _sheet(args.sheet), args.mapping,
                                 args.include_total)
    elif args.cmd == "analyze":
        out = service.analyze(args.path, args.instrument, args.output_dir, _sheet(args.sheet), args.mapping,
                              args.id_column, args.group, args.continuous, args.covariate, args.reference, args.method,
                              args.cutoff, args.include_total, not args.no_cfa, args.lang, args.instrument_version,
                              args.metadata)
    else:
        print(service.guide(args.topic, args.instrument))
        return 0
    print(service.to_json(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
