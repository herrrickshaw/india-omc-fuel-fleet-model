"""Make the repo root and vahan/ importable for the characterisation tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "vahan"):
    sys.path.insert(0, str(p))
