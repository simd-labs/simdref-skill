#!/usr/bin/env python3
"""Fail loudly if the three plugin manifests disagree on version.

This repo has no pyproject.toml: it ships markdown skill docs and plugin
manifests only, no Python package. The single source of truth here is
``.claude-plugin/plugin.json:.version``. ``.claude-plugin/marketplace.json``
(``.plugins[0].version``) and
``codex-skills/asm-analysis/.codex-plugin/plugin.json`` (``.version``) must
match it, otherwise users installing via ``/plugin marketplace add`` or the
Codex plugin path see a stale version string.

Usage::

    python scripts/check-version-sync.py          # verify
    python scripts/check-version-sync.py --fix    # rewrite the other two to match plugin.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_PLUGIN = ROOT / "codex-skills" / "asm-analysis" / ".codex-plugin" / "plugin.json"


def _marketplace_version(data: dict) -> str:
    plugins = data.get("plugins") or []
    if not plugins:
        raise RuntimeError("marketplace.json has no plugins")
    return plugins[0].get("version", "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="rewrite the other two files to match plugin.json")
    args = parser.parse_args(argv)

    plugin = json.loads(PLUGIN.read_text())
    marketplace = json.loads(MARKETPLACE.read_text())
    codex_plugin = json.loads(CODEX_PLUGIN.read_text())

    canonical = plugin.get("version", "")
    mv = _marketplace_version(marketplace)
    cv = codex_plugin.get("version", "")

    mismatched: list[tuple[str, str, str]] = []
    if mv != canonical:
        mismatched.append((str(MARKETPLACE.relative_to(ROOT)), mv, canonical))
    if cv != canonical:
        mismatched.append((str(CODEX_PLUGIN.relative_to(ROOT)), cv, canonical))

    if not mismatched:
        print(f"version sync OK: {canonical}")
        return 0

    if not args.fix:
        print(f"{PLUGIN.relative_to(ROOT)} version is {canonical!r}; out of sync:")
        for path, found, expected in mismatched:
            print(f"  {path}: {found!r} != {expected!r}")
        print("re-run with --fix to rewrite the other manifests in place.")
        return 1

    marketplace["plugins"][0]["version"] = canonical
    MARKETPLACE.write_text(json.dumps(marketplace, indent=2) + "\n")
    codex_plugin["version"] = canonical
    CODEX_PLUGIN.write_text(json.dumps(codex_plugin, indent=2) + "\n")
    print(f"rewrote plugin metadata to version {canonical}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
