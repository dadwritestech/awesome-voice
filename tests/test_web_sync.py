"""The web page must run the same checker and tells as the plugin."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_web  # noqa: E402


def test_docs_slop_js_matches_plugin():
    assert (ROOT / "docs" / "slop.js").read_bytes() == (ROOT / "plugin" / "slop" / "slop.js").read_bytes(), \
        "run python scripts/build_web.py"


def test_docs_tells_js_matches_tells_json():
    assert (ROOT / "docs" / "tells.js").read_text(encoding="utf-8") == build_web.tells_js(), \
        "run python scripts/build_web.py"
