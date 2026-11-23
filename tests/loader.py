"""Run a repo script offline: compiled from its real path (so coverage measures the
source) but executed with ``__file__`` pointing into a temp tree, so every
``Path(__file__).parent / "outputs"`` write lands in tmp_path, never the repo.

``__file__`` deliberately gets a *different basename* from the script: coverage.py
swaps in ``__file__`` for a frame's filename when the basenames match, which would
make it look for the temp path and drop the real source from the report."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel, tmp_path, name="loaded"):
    src = os.path.join(ROOT, rel)
    dst_dir = tmp_path / os.path.dirname(rel)
    dst_dir.mkdir(parents=True, exist_ok=True)
    with open(src, encoding="utf-8") as fh:
        code = compile(fh.read(), src, "exec")
    ns = {"__file__": str(dst_dir / "_script_under_test.py"), "__name__": name}
    exec(code, ns)
    return ns
