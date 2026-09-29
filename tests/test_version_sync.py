"""check-version-sync.py catches a mismatch and passes on the real manifests."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "check-version-sync.py"

MANIFESTS = [
    Path(".claude-plugin/plugin.json"),
    Path(".claude-plugin/marketplace.json"),
    Path("codex-skills/asm-analysis/.codex-plugin/plugin.json"),
]


def _copy_repo_layout(dst: Path) -> None:
    (dst / "scripts").mkdir(parents=True)
    shutil.copy2(SCRIPT, dst / "scripts" / "check-version-sync.py")
    for rel in MANIFESTS:
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst / rel)


def _run(cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/check-version-sync.py"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_mismatch_is_caught(tmp_path):
    _copy_repo_layout(tmp_path)
    marketplace_path = tmp_path / MANIFESTS[1]
    data = json.loads(marketplace_path.read_text())
    data["plugins"][0]["version"] = "9.9.9"
    marketplace_path.write_text(json.dumps(data, indent=2) + "\n")

    result = _run(tmp_path)
    assert result.returncode != 0
    assert "9.9.9" in result.stdout


def test_real_manifests_pass():
    result = _run(REPO)
    assert result.returncode == 0, result.stdout + result.stderr
