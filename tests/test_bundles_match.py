"""skill/ regenerates the committed per-agent trees byte-for-byte."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import build_skill_bundles as bsb  # noqa: E402


def test_committed_trees_match_fresh_build():
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "build_skill_bundles.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_check_reports_drift_on_a_corrupted_tree():
    """Positive control: diff_trees must fail on a tree it did not build."""
    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "claude"
        bsb.stamp("claude", staging, bsb.TARGETS["claude"]["extras"])
        corrupted = Path(tmp) / "corrupted"
        shutil.copytree(staging, corrupted)
        (corrupted / "SKILL.md").write_text("corrupted\n")
        assert bsb.diff_trees(staging, corrupted)
