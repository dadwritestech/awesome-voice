"""Measure every candidate tell in model output and in pre-ChatGPT human writing.

  python evidence/measure.py            # print the table, write evidence/EVIDENCE.md
  python evidence/measure.py --write    # also write plugin/slop/tells.json

Tiers:
  measured  models use it at least 3x as often as humans (per 10k words), in at least 3 model samples
  classic   not measured here, but humans almost never write it (<= 0.3 per 10k words)
  dropped   humans use it too often to flag it
"""
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from candidates import CANDIDATES  # noqa: E402

KEEP_RATIO, KEEP_MIN_SAMPLES = 3.0, 3
CLASSIC_HUMAN_MAX = 0.3  # per 10k words: rare enough in human text that flagging it costs nothing


def clean(text):
    """Same masking as plugin/slop/slop.py: blank out code, HTML, URLs and images."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"```.*?```", blank, text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", blank, text)
    text = re.sub(r"<!--\s*no-slop off\s*-->.*?(?:<!--\s*no-slop on\s*-->|\Z)", blank, text, flags=re.S)
    text = re.sub(r"<[^>\n]+>", blank, text)
    text = re.sub(r"!\[[^\]\n]*\]\([^)\n]*\)", blank, text)
    text = re.sub(r"https?://\S+", blank, text)
    return text.replace("’", "'")


def to_rule(c):
    """Candidate -> the JSON rule both engines read."""
    if "words" in c:
        alts = "|".join(re.escape(w).replace("\\ ", " ").replace("\\-", "-").replace("\\'", "'") for w in sorted(c["words"], key=len, reverse=True))
        pattern, flags = rf"(?<![\w'-])(?:{alts})(?![\w'-])", "i"
    else:
        pattern, flags = c["regex"], ""
        if pattern.startswith("(?m)"):
            pattern, flags = pattern[4:], "m"
        if c["kind"] != "structure":
            flags += "i"
    return {"id": c["id"], "kind": c["kind"], "pattern": pattern, "flags": flags, "fix": c["fix"]}


def compile_rule(r):
    f = re.A  # ASCII \w, as in JavaScript
    if "i" in r["flags"]:
        f |= re.I
    if "m" in r["flags"]:
        f |= re.M
    return re.compile(r["pattern"], f)


def words(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'_-]*", text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    models = defaultdict(list)
    for line in (HERE / "models.jsonl").open(encoding="utf-8"):
        row = json.loads(line)
        models[row["model"]].append(clean(row["text"]))
    human = [clean(json.loads(l)["text"]) for l in (HERE / "human.jsonl").open(encoding="utf-8")]
    human = [h for h in human if words(h) >= 30]
    model_all = [t for ts in models.values() for t in ts]

    def rate(rx, texts):
        hits = [len(rx.findall(t)) for t in texts]
        w = sum(words(t) for t in texts) or 1
        return 1e4 * sum(hits) / w, sum(1 for h in hits if h)

    rows, kept = [], []
    for c in CANDIDATES:
        rule = to_rule(c)
        rx = compile_rule(rule)
        m_rate, m_docs = rate(rx, model_all)
        h_rate, h_docs = rate(rx, human)
        per_model = {name: rate(rx, ts)[0] for name, ts in models.items()}
        ratio = m_rate / h_rate if h_rate else float("inf") if m_rate else 0.0
        if m_docs >= KEEP_MIN_SAMPLES and ratio >= KEEP_RATIO:
            tier = "measured"
        elif h_rate <= CLASSIC_HUMAN_MAX:
            tier = "classic"
        else:
            tier = None
        keep = tier is not None
        rule["tier"] = tier
        rule["evidence"] = {"model_per_10k": round(m_rate, 1), "human_per_10k": round(h_rate, 1),
                            "model_samples": m_docs, "ratio": None if ratio == float("inf") else round(ratio, 1)}
        rows.append((c["id"], c["kind"], m_rate, h_rate, ratio, m_docs, h_docs, per_model, tier or "dropped"))
        if keep:
            kept.append(rule)

    # Grades: tells per 100 words, cut at the human documents' own distribution.
    def density(t):
        w = words(t)
        return 100 * sum(len(compile_rule(r).findall(t)) for r in kept) / w if w else 0.0
    hd = sorted(density(t) for t in human)
    q = lambda p: round(hd[min(len(hd) - 1, int(p * len(hd)))], 2)
    grades = [["A", q(0.50)], ["B", q(0.75)], ["C", q(0.90)], ["D", round(2 * q(0.90), 2)]]
    md = [density(t) for t in model_all]
    dist = lambda xs, g: sum(1 for x in xs if (g == "F" and x > grades[-1][1]) or
                             (g != "F" and x <= dict(grades)[g] and (g == "A" or x > dict(grades)["ABCD"["ABCD".index(g) - 1]])))

    names = sorted(models)
    mw = sum(words(t) for t in model_all)
    hw = sum(words(t) for t in human)
    n_prompts = len(set(json.loads(l)["prompt_id"] for l in (HERE / "models.jsonl").open(encoding="utf-8")))
    counts = {t: sum(1 for r in rows if r[8] == t) for t in ("measured", "classic", "dropped")}
    lines = [
        "# Evidence for each tell",
        "",
        "Generated by [measure.py](measure.py). Rerun it after adding samples.",
        "",
        f"- **Model text:** {len(model_all)} samples, {mw:,} words, from {', '.join(f'`{n}`' for n in names)}, "
        f"answering the {n_prompts} everyday writing prompts in [prompts.json](prompts.json) (READMEs, release notes, "
        "PR descriptions, docs, emails, error messages) with a plain system prompt. Raw output: [models.jsonl](models.jsonl).",
        f"- **Human text:** {len(human)} READMEs and release notes, {hw:,} words, from 85 well-known open-source repos, "
        "each as it was before 1 June 2022, months before ChatGPT. Built by [fetch_human.py](fetch_human.py). "
        "Code, HTML and URLs are blanked out of both before counting.",
        "",
        "## Tiers",
        "",
        f"- **measured** ({counts['measured']}): models write it at least {KEEP_RATIO:g}x as often as humans, per 10,000 words, "
        f"in at least {KEEP_MIN_SAMPLES} model samples.",
        f"- **classic** ({counts['classic']}): too rare in these samples to measure, but humans almost never write it "
        f"(at most {CLASSIC_HUMAN_MAX} per 10,000 words), so flagging it costs nothing. Most of the famous \"delve\" list is here.",
        f"- **dropped** ({counts['dropped']}): humans write it too, so flagging it would nag people for normal writing.",
        "",
        "## Grades",
        "",
        "A grade is tells per 100 words, cut at the human documents' own distribution: "
        f"A is at or under the human median ({grades[0][1]}), B under the 75th percentile ({grades[1][1]}), "
        f"C under the 90th ({grades[2][1]}), D under twice that ({grades[3][1]}), F above.",
        "",
        "| Grade | Human documents | Model samples |",
        "|---|---:|---:|",
    ]
    for g in "ABCDF":
        lines.append(f"| {g} | {dist(hd, g)} | {dist(md, g)} |")
    lines += [
        "",
        "## Every candidate",
        "",
        "| Tell | Kind | Models /10k words | Humans /10k words | Ratio | Model samples | " + " | ".join(f"`{n}`" for n in names) + " | Tier |",
        "|---|---|---:|---:|---:|---:|" + "---:|" * len(names) + "---|",
    ]
    order = {"measured": 0, "classic": 1, "dropped": 2}
    for (i, kind, m, h, ratio, mdocs, hdocs, pm, tier) in sorted(rows, key=lambda r: (order[r[8]], -(r[4] if r[4] != float("inf") else 1e9), -r[2])):
        rs = "only models" if ratio == float("inf") else ("-" if not m else f"{ratio:.1f}x")
        lines.append(f"| `{i}` | {kind} | {m:.1f} | {h:.1f} | {rs} | {mdocs} | " +
                     " | ".join(f"{pm[n]:.1f}" for n in names) + f" | {tier} |")
    report = "\n".join(lines) + "\n"
    (HERE / "EVIDENCE.md").write_text(report, encoding="utf-8")
    print(report)

    if args.write:
        out = ROOT / "plugin" / "slop" / "tells.json"
        data = {"version": 1, "evidence": "https://github.com/dadwritestech/awesome-voice/blob/main/evidence/EVIDENCE.md",
                "grades": grades, "tells": kept}
        out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {out}: {len(kept)} tells", file=sys.stderr)


if __name__ == "__main__":
    main()
