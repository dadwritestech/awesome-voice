"""slop.py: find AI-writing tells in prose. Standard library only.

Python twin of slop.js; both read tells.json and must report the same hits
(tests/test_parity.py checks this). Use it as a module or a CLI:

    python slop.py README.md docs/*.md
    python slop.py --max-grade B CHANGELOG.md   # exit 1 if any file is worse than B
    cat draft.txt | python slop.py -
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parent / "tells.json").read_text(encoding="utf-8"))


def _compile(t):
    flags = re.A  # \w and \b mean ASCII, as in JavaScript
    if "i" in t["flags"]:
        flags |= re.I
    if "m" in t["flags"]:
        flags |= re.M
    return re.compile(t["pattern"], flags)


RULES = [(t, _compile(t)) for t in DATA["tells"]]
GRADES = DATA["grades"]


def mask(text: str) -> str:
    """Blank out code, HTML, URLs and images, keeping every offset in place."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"```.*?```", blank, text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", blank, text)
    # After code, so a marker quoted in backticks doesn't switch checking off.
    text = re.sub(r"<!--\s*no-slop off\s*-->.*?(?:<!--\s*no-slop on\s*-->|\Z)", blank, text, flags=re.S)
    text = re.sub(r"<[^>\n]+>", blank, text)
    text = re.sub(r"!\[[^\]\n]*\]\([^)\n]*\)", blank, text)
    text = re.sub(r"https?://\S+", blank, text)
    return text.replace("’", "'")


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'_-]*", text))


def grade(per100: float) -> str:
    for letter, top in GRADES:
        if per100 <= top:
            return letter
    return "F"


def scan(text: str, ignore=()) -> dict:
    prose = mask(text)
    hits = []
    for t, rx in RULES:
        if t["id"] in ignore:
            continue
        for m in rx.finditer(prose):
            if not m.group(0):
                continue
            hits.append({"id": t["id"], "kind": t["kind"], "tier": t.get("tier"), "start": m.start(), "end": m.end(),
                         "match": text[m.start():m.end()], "line": prose.count("\n", 0, m.start()) + 1, "fix": t["fix"]})
    hits.sort(key=lambda h: (h["start"], h["id"]))
    words = count_words(prose)
    per100 = 100 * len(hits) / words if words else 0.0
    return {"words": words, "hits": hits, "per100": round(per100, 2), "grade": grade(per100)}


def format_report(name: str, r: dict) -> str:
    out = [f"{name}: grade {r['grade']} ({len(r['hits'])} tells in {r['words']} words, {r['per100']:.2f} per 100)"]
    for h in r["hits"]:
        out.append(f"  line {h['line']}: {h['match'].strip()!r} [{h['id']}] -> {h['fix']}")
    return "\n".join(out)


def main(argv=None) -> int:
    import argparse
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Find AI-writing tells in prose.")
    p.add_argument("files", nargs="+", help="files to check, or - for stdin")
    p.add_argument("--max-grade", default="F", help="exit 1 if any file grades worse than this (A-F)")
    p.add_argument("--ignore", action="append", default=[], help="tell id to skip (repeatable)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    worst_ok = "ABCDF".index(a.max_grade.upper())
    failed = False
    results = {}
    for f in a.files:
        text = sys.stdin.read() if f == "-" else Path(f).read_text(encoding="utf-8")
        r = scan(text, a.ignore)
        results[f] = r
        failed |= "ABCDF".index(r["grade"]) > worst_ok
        if not a.json:
            print(format_report(f, r))
    if a.json:
        print(json.dumps(results, indent=1, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
