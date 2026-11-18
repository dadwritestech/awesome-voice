"""voicescore: measure whether agent output moves toward a VOICE.md.

Standard library only. Four subcommands:

  check      Lint a text file against one voice. No model needed.
  selftest   Score each VOICE.md's own Before/After examples. Every After
             should beat its Before. No model needed.
  generate   Ask a local OpenAI-compatible server to answer the prompts in
             prompts.json, once with no voice and once per VOICE.md.
             Results are cached in a JSONL file, so reruns only fill gaps.
  report     Score the cached generations and print a Markdown table.

The voice-fit score is the mean of per-target scores (0-100). Each target
comes from the `targets:` block in the VOICE.md frontmatter, so the score
answers "did the agent follow the rules this file states?", not "does it
sound like the real brand?". See README for what that does and doesn't prove.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOICES_DIR = ROOT / "voices"

BASE_SYSTEM = "You are a helpful assistant."
VOICE_SYSTEM = BASE_SYSTEM + "\n\nWrite everything in the voice described in this VOICE.md file.\n\n{voice}"

# Generic AI-writing tells, scored for every voice. One list for the scorer and the
# no-slop plugin: plugin/slop/tells.json, built from evidence/ by evidence/measure.py.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugin" / "slop"))
import slop  # noqa: E402


def ai_tell_hits(text: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for h in slop.scan(text)["hits"]:
        hits[h["id"]] = hits.get(h["id"], 0) + 1
    return hits


# ---------------------------------------------------------------- parsing

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the restricted YAML subset described in FORMAT.md."""
    if not text.startswith("---"):
        return {}, text
    end = text.index("\n---", 3)
    block, body = text[3:end], text[end + 4:]
    data: dict = {}
    key = None
    for raw in block.splitlines():
        line = raw.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            k, _, v = line.partition(":")
            key, v = k.strip(), v.strip()
            data[key] = v if v else None
            continue
        item = line.strip()
        if item.startswith("- "):
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(item[2:].strip())
        else:
            if not isinstance(data.get(key), dict):
                data[key] = {}
            k, _, v = item.partition(":")
            data[key][k.strip()] = v.strip()
    return data, body


def section(body: str, title: str) -> str:
    m = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def banned_phrases(body: str) -> list[str]:
    out = []
    for line in section(body, "Banned phrases").splitlines():
        m = re.match(r"\s*-\s*`([^`]+)`", line)
        if m:
            out.append(m.group(1).strip())
    return out


def replacements(body: str) -> dict[str, str]:
    """Map each banned phrase to the text after its arrow."""
    out = {}
    for line in section(body, "Banned phrases").splitlines():
        m = re.match(r"\s*-\s*`([^`]+)`\s*(?:→|->)\s*(.+)", line)
        if m:
            out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def examples(body: str) -> list[dict]:
    """Return [{label, before, after}] from the Before and after section."""
    out = []
    for chunk in re.split(r"^### ", section(body, "Before and after"), flags=re.M)[1:]:
        label = chunk.splitlines()[0].strip()
        parts = {}
        for which in ("Before", "After"):
            m = re.search(rf"\*\*{which}\*\*\s*\n((?:\s*>.*\n?)+)", chunk)
            if m:
                parts[which.lower()] = " ".join(
                    l.strip()[1:].strip() for l in m.group(1).splitlines() if l.strip().startswith(">")
                )
        if "before" in parts and "after" in parts:
            out.append({"label": label, **parts})
    return out


def load_voice(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    return {
        "slug": meta.get("slug") or path.parent.name,
        "name": meta.get("name") or path.parent.name,
        "meta": meta,
        "targets": meta.get("targets") or {},
        "banned": banned_phrases(body),
        "replacements": replacements(body),
        "examples": examples(body),
        "text": text,
    }


def load_voices(only: list[str] | None = None) -> list[dict]:
    voices = [load_voice(p) for p in sorted(VOICES_DIR.glob("*/VOICE.md"))]
    if only:
        voices = [v for v in voices if v["slug"] in only]
    return voices


# ---------------------------------------------------------------- features

WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’_.-]*")


def strip_markup(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)       # code blocks
    text = re.sub(r"`[^`]*`", "X", text)                     # inline code -> one token
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)   # links
    text = re.sub(r"[*_#>|]+", " ", text)
    return text.replace("’", "'")


def sentences(text: str) -> list[str]:
    """Sentences from prose and list items. Headings and table rows are dropped."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "|", "```")) or re.fullmatch(r"[-=*_ ]{3,}", s):
            continue
        s = re.sub(r"^([-*+]|\d+[.)])\s+", "", s)
        s = strip_markup(s)
        for part in re.split(r"(?<=[.!?])\s+(?=[\"'(\[]?[A-Z0-9])", s):
            if len(WORD.findall(part)) >= 2:
                out.append(part.strip())
    return out


def paragraphs(text: str) -> list[str]:
    """Prose paragraphs only: skip lists, headings, tables, code."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    out = []
    for block in re.split(r"\n\s*\n", text):
        lines = [l for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        first = lines[0].lstrip()
        if first.startswith(("#", "|", "-", "*", "+")) or re.match(r"\d+[.)]\s", first):
            continue
        out.append(" ".join(l.strip().lstrip("> ") for l in lines))
    return out


NEG_CONTRACTED = re.compile(r"\b(can't|don't|doesn't|didn't|won't|isn't|aren't|wasn't|weren't|haven't|hasn't|hadn't|wouldn't|shouldn't|couldn't)\b", re.I)
NEG_EXPANDED = re.compile(r"\b(cannot|can not|do not|does not|did not|will not|is not|are not|was not|were not|have not|has not|had not|would not|should not|could not)\b", re.I)
POS_CONTRACTED = re.compile(r"\b(it's|you're|we're|they're|that's|there's|you'll|we'll|it'll|you've|we've|i'm|let's|what's|here's)\b", re.I)
POS_EXPANDED = re.compile(r"\b(it is|you are|we are|they are|there is|you will|we will|you have|we have|i am|let us|what is|here is)\b", re.I)
COMPLEX_CONTRACTED = re.compile(r"\b\w+(?:'ve|n't've)\b", re.I)

BE = r"(?:is|are|was|were|be|been|being|am)"
IRREGULAR = (
    "made|done|given|taken|sent|shown|known|seen|found|built|kept|held|paid|set|put|"
    "written|chosen|run|sold|told|left|lost|read|brought|bought|caught|thrown|grown|drawn|hidden|"
    "broken|spoken|stolen|frozen|forgotten|begun|withdrawn|met|cut|shut|hit"
)
PASSIVE = re.compile(rf"\b{BE}\s+(?:\w+ly\s+)?(?:\w+ed|{IRREGULAR})\b", re.I)
# Adjectives ending in -ed that are rarely passive in this kind of text.
PASSIVE_FALSE = re.compile(rf"\b{BE}\s+(?:\w+ly\s+)?(?:excited|interested|tired|pleased|thrilled|delighted|required|needed|based|limited|located|supposed|used to|signed in|logged in|allowed)\b", re.I)


def phrase_hits(text: str, phrases: list[str]) -> dict[str, int]:
    low = strip_markup(text).lower()
    hits = {}
    for p in phrases:
        n = len(re.findall(rf"(?<![\w-]){re.escape(p.lower())}(?![\w-])", low))
        if n:
            hits[p] = n
    return hits


def features(text: str, banned: list[str] | None = None) -> dict:
    sents = sentences(text)
    words = WORD.findall(strip_markup(text))
    plain = strip_markup(text)
    lens = [len(WORD.findall(s)) for s in sents] or [0]
    paras = paragraphs(text)
    para_lens = [len(sentences(p)) for p in paras]
    passive = sum(1 for s in sents if PASSIVE.search(s) and not PASSIVE_FALSE.search(s))
    you = len(re.findall(r"\b(you|your|yours|yourself)\b", plain, re.I))
    first = len(re.findall(r"\b(we|us|our|let's|i|me|my)\b", plain, re.I))
    return {
        "words": len(words),
        "sentences": len(sents),
        "mean_sentence_words": statistics.mean(lens),
        "long_sentences": lens,
        "mean_paragraph_sentences": statistics.mean(para_lens) if para_lens else None,
        "neg_contracted": len(NEG_CONTRACTED.findall(plain)),
        "neg_expanded": len(NEG_EXPANDED.findall(plain)),
        "pos_contracted": len(POS_CONTRACTED.findall(plain)),
        "pos_expanded": len(POS_EXPANDED.findall(plain)),
        "complex_contracted": len(COMPLEX_CONTRACTED.findall(plain)),
        "passive_rate": passive / len(sents) if sents else 0.0,
        "exclamations": plain.count("!"),
        "you_words": you,
        "first_person_words": first,
        "banned_hits": phrase_hits(text, banned or []),
        "ai_tell_hits": ai_tell_hits(text),
    }


# ---------------------------------------------------------------- scoring

def _range(v: str) -> tuple[float, float]:
    lo, _, hi = v.partition("-")
    return float(lo), float(hi or lo)


def _in_range(x: float, lo: float, hi: float) -> float:
    if lo <= x <= hi:
        return 1.0
    gap = lo - x if x < lo else x - hi
    return max(0.0, 1.0 - gap / max(lo, 1.0))


def score(text: str, voice: dict) -> dict:
    """Per-target scores in 0..1 plus the mean as `fit` (0-100)."""
    f = features(text, voice["banned"])
    t = voice["targets"]
    s: dict[str, float] = {}

    if "sentence_words" in t:
        s["sentence_length"] = _in_range(f["mean_sentence_words"], *_range(t["sentence_words"]))
    if "max_sentence_words" in t and f["sentences"]:
        cap = float(t["max_sentence_words"])
        s["long_sentences"] = 1.0 - sum(1 for n in f["long_sentences"] if n > cap) / f["sentences"]
    if "paragraph_sentences" in t and f["mean_paragraph_sentences"] is not None:
        s["paragraph_length"] = _in_range(f["mean_paragraph_sentences"], *_range(t["paragraph_sentences"]))
    policy = t.get("contractions")
    if policy:
        nc, ne = f["neg_contracted"], f["neg_expanded"]
        pc, pe = f["pos_contracted"], f["pos_expanded"]
        if policy == "use" and (nc + ne + pc + pe):
            s["contractions"] = (nc + pc) / (nc + ne + pc + pe)
        elif policy == "avoid" and (nc + ne + pc + pe):
            s["contractions"] = (ne + pe) / (nc + ne + pc + pe)
        elif policy == "avoid-negative" and (nc + ne):
            s["contractions"] = ne / (nc + ne)
            if f["complex_contracted"]:
                s["contractions"] *= 0.5
    if "passive_max" in t:
        cap = float(t["passive_max"])
        over = max(0.0, f["passive_rate"] - cap)
        s["passive_voice"] = max(0.0, 1.0 - over / 0.3)
    if "exclamations" in t:
        over = max(0, f["exclamations"] - int(t["exclamations"]))
        s["exclamations"] = max(0.0, 1.0 - 0.5 * over)
    # "You, not we": imperatives with neither pronoun count as second person.
    if t.get("second_person") == "yes" and (f["you_words"] + f["first_person_words"]):
        s["second_person"] = f["you_words"] / (f["you_words"] + f["first_person_words"])
    hits = sum(f["banned_hits"].values())
    s["banned_phrases"] = max(0.0, 1.0 - 0.25 * hits)

    return {
        "fit": 100 * statistics.mean(s.values()),
        "scores": s,
        "features": {k: v for k, v in f.items() if k != "long_sentences"},
    }


# ---------------------------------------------------------------- model client

def chat(base_url: str, model: str, system: str, user: str, *, api_key: str | None,
         max_tokens: int, temperature: float, seed: int, timeout: int = 600) -> str:
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "seed": seed,
        # Thinking models (gemma-4, qwen3) otherwise spend the budget reasoning.
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 **({"Authorization": f"Bearer {api_key}"} if api_key else {})},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    return data["choices"][0]["message"]["content"] or ""


def embed(base_url: str, model: str, texts: list[str], api_key: str | None) -> list[list[float]]:
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/embeddings",
        data=json.dumps({"model": model, "input": texts}).encode(),
        headers={"Content-Type": "application/json",
                 **({"Authorization": f"Bearer {api_key}"} if api_key else {})},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
    return [d["embedding"] for d in sorted(data["data"], key=lambda d: d["index"])]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) or 1.0)


def centroid(vecs: list[list[float]]) -> list[float]:
    return [sum(c) / len(vecs) for c in zip(*vecs)]


# ---------------------------------------------------------------- commands

def cmd_selftest(args) -> int:
    failures = 0
    print("| Voice | Example | Before | After |\n|---|---|---:|---:|")
    for v in load_voices(args.voice):
        if not v["examples"]:
            print(f"| {v['name']} | (no examples parsed) | | |")
            failures += 1
        for ex in v["examples"]:
            b, a = score(ex["before"], v)["fit"], score(ex["after"], v)["fit"]
            mark = "" if a > b else " FAIL"
            failures += a <= b
            print(f"| {v['name']} | {ex['label']} | {b:.0f} | {a:.0f}{mark} |")
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


def cmd_check(args) -> int:
    """Lint text against one voice. Deterministic: no model, no network."""
    if not args.voice or len(args.voice) != 1:
        print("check needs exactly one --voice, for example --voice gov-uk", file=sys.stderr)
        return 2
    voices = load_voices(args.voice)
    if not voices:
        print(f"No voice called {args.voice[0]!r}. Try: " +
              ", ".join(v["slug"] for v in load_voices()), file=sys.stderr)
        return 2
    v = voices[0]
    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    r = score(text, v)
    f = r["features"]
    print(f"{v['name']} voice fit: {r['fit']:.0f}/100")
    for k, val in r["scores"].items():
        print(f"  {'ok ' if val >= 0.999 else 'fix'} {k:<17} {val:.2f}")
    print(f"  mean sentence: {f['mean_sentence_words']:.1f} words (target {v['targets'].get('sentence_words', 'none')}), "
          f"passive: {f['passive_rate']:.0%}, exclamations: {f['exclamations']}")
    for phrase, n in f["banned_hits"].items():
        print(f"  banned: {phrase!r} x{n} -> {v['replacements'].get(phrase.lower(), '(rewrite)')}")
    for phrase, n in f["ai_tell_hits"].items():
        print(f"  ai tell: {phrase!r} x{n}")
    return 0 if r["fit"] >= args.min_fit else 1


def load_cache(path: Path) -> dict:
    cache = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                cache[(row["model"], row["condition"], row["prompt_id"], row["sample"])] = row
    return cache


def cmd_generate(args) -> int:
    prompts = json.loads(Path(args.prompts).read_text(encoding="utf-8"))
    voices = load_voices(args.voice)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cache = load_cache(out)
    conditions = [("baseline", BASE_SYSTEM)] + [
        (v["slug"], VOICE_SYSTEM.format(voice=v["text"])) for v in voices
    ]
    jobs = [(c, sysmsg, p, i) for c, sysmsg in conditions for p in prompts for i in range(args.samples)
            if (args.model, c, p["id"], i) not in cache]
    print(f"{len(jobs)} generation(s) to run ({len(cache)} cached) on {args.model}", file=sys.stderr)
    with out.open("a", encoding="utf-8") as fh:
        for n, (cond, sysmsg, p, i) in enumerate(jobs, 1):
            t0 = time.time()
            text = chat(args.base_url, args.model, sysmsg, p["prompt"], api_key=args.api_key,
                        max_tokens=args.max_tokens, temperature=args.temperature, seed=1000 + i)
            row = {"model": args.model, "condition": cond, "prompt_id": p["id"], "sample": i,
                   "temperature": args.temperature, "max_tokens": args.max_tokens,
                   "seconds": round(time.time() - t0, 1), "text": text}
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"[{n}/{len(jobs)}] {cond} / {p['id']} / {i}: {row['seconds']}s, {len(text.split())} words",
                  file=sys.stderr)
    return 0


def cmd_report(args) -> int:
    rows = [r for r in load_cache(Path(args.out)).values() if r["model"] == args.model]
    if not rows:
        print(f"No generations for {args.model} in {args.out}. Run `generate` first.", file=sys.stderr)
        return 1
    voices = load_voices(args.voice)
    baseline = [r for r in rows if r["condition"] == "baseline"]
    emb_model = args.embed_model if args.embed else None

    def mean(xs):
        return statistics.mean(xs) if xs else float("nan")

    lines = [
        f"Model: `{args.model}`. {len(baseline)} baseline sample(s); "
        f"each voice scored on the same prompts with its VOICE.md in the system prompt.",
        "",
        "| Voice | Fit without VOICE.md | Fit with VOICE.md | Change | Banned-phrase hits (without → with) "
        "| Mean sentence words (without → with) | Target |" + (" Embedding: closer to After examples (without → with) |" if emb_model else ""),
        "|---|---:|---:|---:|---|---|---|" + ("---|" if emb_model else ""),
    ]
    detail = {}
    for v in voices:
        voiced = [r for r in rows if r["condition"] == v["slug"]]
        if not voiced:
            continue
        sb = [score(r["text"], v) for r in baseline]
        sv = [score(r["text"], v) for r in voiced]
        fb, fv = mean([s["fit"] for s in sb]), mean([s["fit"] for s in sv])
        hb = sum(sum(s["features"]["banned_hits"].values()) for s in sb)
        hv = sum(sum(s["features"]["banned_hits"].values()) for s in sv)
        lb = mean([s["features"]["mean_sentence_words"] for s in sb])
        lv = mean([s["features"]["mean_sentence_words"] for s in sv])
        row = (f"| {v['name']} | {fb:.0f} | {fv:.0f} | {fv - fb:+.0f} | {hb} → {hv} | "
               f"{lb:.1f} → {lv:.1f} | {v['targets'].get('sentence_words', '')} |")
        if emb_model:
            after = embed(args.base_url, emb_model, [ex["after"] for ex in v["examples"]], args.api_key)
            before = embed(args.base_url, emb_model, [ex["before"] for ex in v["examples"]], args.api_key)
            ca, cb = centroid(after), centroid(before)

            def margin(texts):
                vecs = embed(args.base_url, emb_model, texts, args.api_key)
                return mean([cosine(x, ca) - cosine(x, cb) for x in vecs])
            row += f" {margin([r['text'] for r in baseline]):+.3f} → {margin([r['text'] for r in voiced]):+.3f} |"
        lines.append(row)
        detail[v["slug"]] = {
            "without": {k: mean([s["scores"].get(k) for s in sb if k in s["scores"]]) for k in sv[0]["scores"]},
            "with": {k: mean([s["scores"].get(k) for s in sv if k in s["scores"]]) for k in sv[0]["scores"]},
        }

    lines += ["", "Per-target scores (0-1, without → with):", "",
              "| Voice | " + " | ".join(["sentence_length", "long_sentences", "paragraph_length", "contractions",
                                         "passive_voice", "exclamations", "second_person", "banned_phrases"]) + " |",
              "|---|" + "---|" * 8]
    for slug, d in detail.items():
        cells = []
        for k in ["sentence_length", "long_sentences", "paragraph_length", "contractions",
                  "passive_voice", "exclamations", "second_person", "banned_phrases"]:
            if k in d["with"]:
                cells.append(f"{d['without'][k]:.2f} → {d['with'][k]:.2f}")
            else:
                cells.append("n/a")
        lines.append(f"| {slug} | " + " | ".join(cells) + " |")

    tb = sum(sum(features(r["text"])["ai_tell_hits"].values()) for r in baseline)
    lines += ["", f"Generic AI-tell phrases in baseline output: {tb} across {len(baseline)} sample(s)."]
    for v in voices:
        voiced = [r for r in rows if r["condition"] == v["slug"]]
        if voiced:
            tv = sum(sum(features(r["text"])["ai_tell_hits"].values()) for r in voiced)
            lines.append(f"- with {v['name']}: {tv} across {len(voiced)} sample(s)")

    report = "\n".join(lines) + "\n"
    print(report)
    if args.write:
        Path(args.write).write_text(report, encoding="utf-8")
    return 0


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--voice", action="append", help="limit to a voice slug (repeatable)")
    common.add_argument("--base-url", default=os.environ.get("LLAMA_BASE_URL", "http://localhost:8080"))
    common.add_argument("--api-key", default=os.environ.get("LLAMA_API_KEY"))
    common.add_argument("--model", default=os.environ.get("VOICE_MODEL", "gemma-4-12b"))
    common.add_argument("--out", default=str(ROOT / "results" / "generations.jsonl"))
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("selftest", parents=[common])
    c = sub.add_parser("check", parents=[common], help="lint a file against one voice, no model needed")
    c.add_argument("file", help="text or Markdown file, or - for stdin")
    c.add_argument("--min-fit", type=float, default=0, help="exit 1 if fit is below this (for CI)")
    g = sub.add_parser("generate", parents=[common])
    g.add_argument("--prompts", default=str(ROOT / "score" / "prompts.json"))
    g.add_argument("--samples", type=int, default=2)
    g.add_argument("--max-tokens", type=int, default=400)
    g.add_argument("--temperature", type=float, default=0.7)
    r = sub.add_parser("report", parents=[common])
    r.add_argument("--embed", action="store_true", help="add embedding similarity to the After examples")
    r.add_argument("--embed-model", default="nomic-embed-text-v1.5.q4-k-m")
    r.add_argument("--write", help="also write the Markdown report to this file")

    args = p.parse_args(argv)
    try:
        return {"selftest": cmd_selftest, "check": cmd_check, "generate": cmd_generate, "report": cmd_report}[args.cmd](args)
    except urllib.error.HTTPError as e:
        print(f"Server returned {e.code}: {e.read().decode(errors='replace')[:300]}", file=sys.stderr)
        if e.code == 401:
            print("Set LLAMA_API_KEY to the key your llama-server was started with.", file=sys.stderr)
        return 2
    except urllib.error.URLError as e:
        print(f"Can't reach {args.base_url}: {e.reason}. Is llama-server running?", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
