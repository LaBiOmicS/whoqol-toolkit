from pathlib import Path

import pytest

EXAMPLES = Path(__file__).parents[1] / "examples"


@pytest.fixture(scope="session")
def examples() -> Path:
    if not (EXAMPLES / "sample_numeric.csv").exists():
        import runpy
        runpy.run_path(str(EXAMPLES / "generate_examples.py"))
    return EXAMPLES
