# textile_data/analysis/*.py import pandas and textile_data/research/create_presentation.py
# imports python-pptx at module top; neither was declared, so a `pip install -r
# requirements.txt` environment fails with ModuleNotFoundError on those scripts.
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_requirements_cover_textile_side_scripts():
    req = (ROOT / "requirements.txt").read_text().lower()
    assert "pandas" in req
    assert "python-pptx" in req
