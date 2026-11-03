"""Characterisation of the Phase 2 scripts: stdout and every written file are byte-identical.

The golden hashes in tests/golden/pass2_manifest.json were captured from the scripts as they
were BEFORE the pass-2 split. Each script runs in a throw-away copy of the repo, so the tracked
outputs are never touched. No network access: all inputs are constants or tracked CSVs.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((Path(__file__).parent / "golden" / "pass2_manifest.json").read_text())
_SKIP = shutil.ignore_patterns(".git", ".venv", "node_modules", "graphify-out", "__pycache__", ".pytest_cache", ".ruff_cache")


# statewise_tax_impact.py reads two public PPAC tables from ~/ppac-ready-reckoner-data/...; the tests
# point HOME at a temp dir holding tracked copies so they do not depend on the developer's machine.
PPAC_FIXTURES = Path(__file__).parent / "fixtures" / "ppac_csv"
PPAC_REL = Path("ppac-ready-reckoner-data") / "annual_fy2025-26_h1" / "csv"


@pytest.fixture(scope="module")
def fake_home(tmp_path_factory):
    home = tmp_path_factory.mktemp("home")
    shutil.copytree(PPAC_FIXTURES, home / PPAC_REL)
    return home


@pytest.fixture(scope="module")
def repo_copy(tmp_path_factory):
    dest = tmp_path_factory.mktemp("repo") / "repo"
    shutil.copytree(ROOT, dest, ignore=_SKIP)
    return dest


@pytest.mark.parametrize("script", sorted(MANIFEST))
def test_script_stdout_and_outputs_identical(repo_copy, fake_home, script):
    # Force UTF-8 so the result does not depend on the runner's locale (scripts read/write
    # non-ASCII text such as the rupee sign without an explicit encoding).
    env = {**os.environ, "PYTHONUTF8": "1", "HOME": str(fake_home)}
    r = subprocess.run(
        [sys.executable, script], cwd=repo_copy, capture_output=True, text=True, encoding="utf-8", env=env
    )
    assert r.returncode == 0, r.stderr[-2000:]
    assert hashlib.sha256(r.stdout.encode()).hexdigest() == MANIFEST[script]["stdout_sha256"]
    for rel, digest in MANIFEST[script]["files"].items():
        assert hashlib.sha256((repo_copy / rel).read_bytes()).hexdigest() == digest, rel
