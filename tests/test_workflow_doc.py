"""skill/references/workflow.md quotes the saturating-chains formula and a consistent example."""
import json
import math
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
WORKFLOW_DOC = REPO / "skill" / "references" / "workflow.md"


def _saturating_chains(lat: float, cpi: float) -> int:
    """Independent chains needed to saturate a unit: ``ceil(lat / cpi)``."""
    return math.ceil(lat / cpi)


def test_workflow_doc_quotes_the_formula_and_a_consistent_example():
    text = WORKFLOW_DOC.read_text()
    assert "ceil(lat / cpi)" in text
    match = re.search(r"reads `lat=([\d.]+) cpi=([\d.]+)`, giving (\d+) chains", text)
    assert match, "worked example missing from the unrolling section"
    lat, cpi, chains = float(match.group(1)), float(match.group(2)), int(match.group(3))
    assert chains == _saturating_chains(lat, cpi)


def test_workflow_example_numbers_match_the_catalog():
    """The doc's worked example must match the CLI's own catalog, not just itself.

    Needs simdref installed and a local catalog.db: absent in a plain checkout,
    present in skill CI after it installs the test core release's wheel and
    pulls the catalog, so the check is real there.
    """
    pytest.importorskip("simdref")
    from typer.testing import CliRunner

    from simdref import cli
    from simdref.storage import SQLITE_PATH

    if not SQLITE_PATH.exists():
        pytest.skip("no local catalog at data/derived/catalog.db")
    result = CliRunner().invoke(
        cli.app, ["llm", "query", "VFMADD132PD (YMM, YMM, YMM)", "--arch", "znver4"]
    )
    if result.exit_code != 0:
        pytest.skip("catalog does not carry VFMADD132PD (YMM, YMM, YMM)")
    entry = json.loads(result.output)["results"][0]["timing"]["ZEN4"]
    match = re.search(r"reads `lat=([\d.]+) cpi=([\d.]+)`", WORKFLOW_DOC.read_text())
    assert (entry["lat"], entry["cpi"]) == (float(match.group(1)), float(match.group(2)))
