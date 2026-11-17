import os
import runpy
import shutil

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def run_copy(tmp_path):
    """Run a script from a temp copy so its `outputs/` writes never touch the repo."""
    def _run(rel, call_main=False):
        dst = tmp_path / os.path.basename(rel)
        shutil.copy(os.path.join(ROOT, rel), dst)
        ns = runpy.run_path(str(dst), run_name="__main__" if call_main else "loaded")
        return ns, tmp_path
    return _run
