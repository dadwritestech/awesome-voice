"""slop.py and slop.js must report the same hits on every document in the evidence corpus."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "slop"))
import slop  # noqa: E402

JS = """
const { scan } = require(process.argv[1]);
const texts = JSON.parse(require('fs').readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(texts.map((t) => {
  const r = scan(t);
  // JS offsets are UTF-16 units (an emoji counts 2); Python's are code points.
  const cp = (i) => [...t.slice(0, i)].length;
  return { words: r.words, grade: r.grade, hits: r.hits.map((h) => [h.id, cp(h.start), cp(h.end), h.line]) };
})));
"""

EXTRA = [
    "Whether you're new or not — it's seamless!\n\n- **Fast:** yes\n",
    "<!-- no-slop off -->\nseamless robust\n<!-- no-slop on -->\nseamless",
    "Use `ensure()` and see https://example.com/seamless for more.",
    "It’s not just a tool, it's a platform. Here's a quick guide. Happy coding! 🚀",
    "",
    "Wrap it in `<!-- no-slop off -->` to skip it.\nThis is seamless.",
]


def corpus():
    texts = list(EXTRA)
    for name in ("human.jsonl", "models.jsonl"):
        for line in (ROOT / "evidence" / name).open(encoding="utf-8"):
            texts.append(json.loads(line)["text"])
    return texts


def js_scan(texts):
    out = subprocess.run(["node", "-e", JS, str(ROOT / "plugin" / "slop" / "slop.js")],
                         input=json.dumps(texts), capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(out.stdout)


def test_python_and_js_agree():
    texts = corpus()
    js = js_scan(texts)
    assert len(js) == len(texts)
    total = 0
    for i, (t, j) in enumerate(zip(texts, js)):
        p = slop.scan(t)
        ph = [[h["id"], h["start"], h["end"], h["line"]] for h in p["hits"]]
        jh = sorted(j["hits"], key=lambda h: (h[1], h[0]))
        assert ph == jh, f"doc {i}: python {ph[:5]} vs js {jh[:5]}"
        assert p["words"] == j["words"], f"doc {i}: word counts differ"
        assert p["grade"] == j["grade"], f"doc {i}: grades differ"
        total += len(ph)
    assert total > 100  # the corpus really exercises the rules


def test_off_region_is_skipped():
    r = slop.scan(EXTRA[1])
    assert [h["line"] for h in r["hits"]] == [4]


def test_marker_in_backticks_does_not_switch_off():
    r = slop.scan(EXTRA[5])
    assert [h["id"] for h in r["hits"]] == ["seamless"]
