# Awesome VOICE.md

**Make your agent write like GOV.UK, Mailchimp, Google, Microsoft, or Stripe docs.**

Copy a VOICE.md into your project, and your coding or writing agent stops
sounding like every other agent. Each file distills a brand's published style
guide into rules an agent can follow: tone, banned phrases, sentence length,
formatting, terminology, and before/after rewrites.

> **+9 to +14 voice fit for every voice · banned phrases 27 → 0 · "!", emoji and "please" in 0 of 40 samples**
>
> Benchmarked on local `gemma-4-12b`, same model with and without VOICE.md:
> 5 voices, 4 prompts, 2 samples each. [Full results](#does-it-work)

Every voice is measured. This repo ships a scoring script that generates text
with and without each VOICE.md and checks whether the output actually moves
toward the voice. The results are below, including where it didn't.

- **146 deterministic checks, no LLM needed.** `voicescore.py check` lints any
  text against a voice: 35 measurable targets, 85 banned phrases with their
  replacements, and 26 generic AI tells. Standard library only, no API key, and
  it exits non-zero below a fit threshold, so it works in CI.
- **Five voices from published sources.** Each rule cites the public page it
  came from.

## What is VOICE.md?

It's a Markdown file that tells an AI agent how to write. No tooling, no schema
beyond a few lines of frontmatter. Drop it next to the files your agent already
reads.

| File | Who reads it | What it defines |
|---|---|---|
| `AGENTS.md` / `CLAUDE.md` | Coding agents | How to build the project |
| `DESIGN.md` | Design agents | How the project should look |
| `VOICE.md` | Any agent that writes | How the project should sound |

Use it for docs, error messages, release notes, onboarding emails, UI copy,
READMEs, and commit messages.

**Works with impeccable.** [impeccable](https://github.com/pbakaus/impeccable)'s
`PRODUCT.md` records a product's voice as one fact among many, next to
audience, purpose, and constraints, for its design commands to use.
VOICE.md is the full writing guide behind that fact: tone rules, banned phrases,
terminology, and rewrites. Use `PRODUCT.md` and `DESIGN.md` for the interface,
and VOICE.md for the words.

The format is specified in [FORMAT.md](FORMAT.md).

## Install

Copy a file into your project root:

```bash
curl -o VOICE.md https://raw.githubusercontent.com/dadwritestech/awesome-voice/main/voices/gov-uk/VOICE.md
```

Then point your agent at it. In `CLAUDE.md` or `AGENTS.md`, add:

```markdown
When you write any prose (docs, UI text, errors, release notes), follow VOICE.md.
```

Coming later: a Claude Code plugin, a skills.sh package, and Cursor rules.

## Collection

| Voice | Basis | In one line |
|---|---|---|
| [**GOV.UK**](voices/gov-uk/VOICE.md) | Published style guide | Plain English for public services. Short sentences, no jargon, `cannot` instead of `can't`. |
| [**Mailchimp**](voices/mailchimp/VOICE.md) | Published style guide | Plainspoken, warm, quietly funny. A business partner who never oversells. |
| [**Google developer docs**](voices/google-developer/VOICE.md) | Published style guide | A knowledgeable friend explaining an API. Conversational, not cute. |
| [**Microsoft**](voices/microsoft/VOICE.md) | Published style guide | Warm and relaxed, crisp and clear. Bigger ideas, fewer words. |
| [**Stripe docs**](voices/stripe-docs/VOICE.md) | Observed from public docs | Precise and calm. Says what the thing does and names the exact error. |

The voices disagree with each other, and that's the point. GOV.UK bans negative
contractions because readers misread them. Google recommends them because
readers miss a lone "not". A generic "write clearly" prompt can't hold both.

## Does it work?

Measured on 2026-10-28 with `gemma-4-12b` running locally on llama-server.
4 prompts (a failed-payment help article, a release note, API key rotation, a
welcome email), 2 samples each, temperature 0.7. "Without" is the same model
with a plain system prompt. Full report: [results/results.md](results/results.md).
Raw outputs: [results/generations.jsonl](results/generations.jsonl).

| Voice | Fit without VOICE.md | Fit with VOICE.md | Change | Banned-phrase hits |
|---|---:|---:|---:|---|
| Google developer docs | 82 | 96 | +14 | 11 → 0 |
| Stripe docs | 83 | 95 | +12 | 8 → 0 |
| GOV.UK | 87 | 98 | +11 | 7 → 0 |
| Microsoft | 86 | 97 | +11 | 1 → 0 |
| Mailchimp | 88 | 97 | +9 | 0 → 0 |

Fit is 0 to 100: how closely the text follows the measurable rules in that
voice's file. Every voice moved toward its targets. The biggest gains came from
contractions, exclamation marks, and banned phrases: half of the 8
baseline samples had an exclamation mark, half had an emoji, and two used
"please" in instructions. None of the voiced samples did any of that. Generic
AI tells ("thrilled to", "whether you're", "streamline") dropped from 6 in the
baseline to 0 to 2 per voice.

Sentence length barely moved, because this model already writes short
sentences (11 words on average). The embedding check, which tests whether the
output lands closer to a voice's After examples than its Before examples,
moved toward the After side for all five voices. For Google it was still on
the Before side afterward (−0.042 → −0.023).

### Same prompt, same model

"Write the body of a welcome email for a project-management app."

| Without VOICE.md | With Mailchimp VOICE.md |
|---|---|
| Welcome to the team! We're thrilled to have you on board. [App Name] is designed to help you streamline your workflow, track your milestones, and crush your goals without the stress. Whether you're managing a small team or a massive project, we're here to make your life easier. | We're glad you're here. You can now start organizing your projects and keeping your team on track. Most people begin by creating their first project board. It takes about 2 minutes to set up your workspace and invite your coworkers. |

"Write a release note: exports now support CSV, and large exports are emailed."

| Without VOICE.md | With GOV.UK VOICE.md |
|---|---|
| **New Update: Improved Data Exports** 🚀 We've updated our data export functionality to give you more flexibility and a smoother experience. … These updates ensure that even your biggest datasets are handled quickly and reliably. Update your app now to try them out! | You can now export your data as a CSV file. We have changed how large files work. You will no longer download large exports in your browser. Instead, we will email you a link when your file is ready. |

## How the scoring works

`score/voicescore.py` uses only the Python standard library.

1. **Generate.** For each prompt in [`score/prompts.json`](score/prompts.json),
   ask a local model twice: once with a plain system prompt, once with the
   VOICE.md added to it. Same prompts, same seeds.
2. **Score.** Measure each output against the `targets` in that voice's
   frontmatter: mean sentence length, share of sentences over the length cap,
   paragraph length, contraction policy, passive-voice rate, exclamation marks,
   "you" versus "we", and hits from the voice's banned-phrase list. Each target
   scores 0 to 1. The voice-fit score is the mean, times 100.
3. **Self-test.** Score each VOICE.md's own Before/After examples. Every After
   must beat its Before, or the targets are wrong.

```bash
python score/voicescore.py selftest
export LLAMA_API_KEY=...   # only if your server uses --api-key
python score/voicescore.py generate --samples 2
python score/voicescore.py report --write results/results.md
```

It talks to any OpenAI-compatible server (`--base-url`, default
`http://localhost:8080`). Generations are cached in
`results/generations.jsonl`, so you can rescore without regenerating.

### Lint your own text, no model needed

```bash
python score/voicescore.py check --voice gov-uk docs/release-notes.md
cat draft.txt | python score/voicescore.py check --voice mailchimp -
python score/voicescore.py check --voice stripe-docs --min-fit 90 README.md   # exit 1 below 90
```

It prints the fit score, each target's result, and every banned phrase it
found with the replacement the voice suggests.

### What the score does and doesn't prove

- It measures whether the agent **followed the rules in the file**. It
  doesn't measure whether the output sounds like the real brand to a human.
  That needs human raters, which this repo doesn't have yet.
- The features are crude. Passive voice is a regex. Sentence splitting is a
  regex. They're consistent across conditions, which is what a before/after
  comparison needs, but don't read a single score as a grade.
- The Before/After examples and the scorer were written together, so the
  self-test is a sanity check, not validation.
- Samples are small: one local model, a handful of prompts. Treat the numbers
  as a first measurement, not a benchmark.

## Contributing

Read [FORMAT.md](FORMAT.md). New voices must come from a published style guide
or the organization's public pages, cite every source URL, paraphrase instead of
copying, and pass `selftest`. No voices for individual people.

## Disclaimer

These files are unofficial. They describe public writing styles and aren't
affiliated with or endorsed by GDS, Mailchimp, Intuit, Google, Microsoft, or
Stripe. All trademarks belong to their owners.

## License

- **Voices and format** (`voices/`, `FORMAT.md`): [CC BY 4.0](LICENSE-CONTENT). Copy them anywhere; keep a credit line.
- **Scorer and tooling:** [MIT](LICENSE).
