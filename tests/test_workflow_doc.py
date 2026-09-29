"""skill/references/workflow.md quotes the saturating-chains formula and a consistent example."""
import math
import re
from pathlib import Path

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
