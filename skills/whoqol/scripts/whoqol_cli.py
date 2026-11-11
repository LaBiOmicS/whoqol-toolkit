# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pandas>=2.1",
#     "numpy>=1.26",
#     "scipy>=1.11",
#     "openpyxl>=3.1",
#     "matplotlib>=3.8",
#     "python-docx>=1.1",
#     "semopy>=2.3",
#     "statsmodels>=0.14",
# ]
# ///
"""whoqol-toolkit entry point for the skill: `uv run whoqol_cli.py {instruments,inspect,template,score,analyze,guide}`.

The analysis code lives in the `whoqol` package next to this file; `uv run` installs the dependencies declared above.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from whoqol.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
