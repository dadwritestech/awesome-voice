# Make your agent stop writing like AI

<!-- no-slop off -->
"Seamless." "Robust." "Whether you're a beginner or an expert." Readers spot
these phrases in a second and stop trusting the text. This repo finds them,
tells your agent not to write them, and gives it a real voice to write in
instead.
<!-- no-slop on -->

![The slop-score page marking AI tells in a paragraph and stamping it F](docs/demo.gif)

**[Score your own text](https://dadwritestech.github.io/awesome-voice/)**: paste a README or a release note. It runs in your browser and nothing is uploaded.

Every flagged phrase is measured, not guessed. I counted 67 tells in 6,275
words of model output and in 103,666 words of READMEs and release notes that
people wrote before ChatGPT existed. A phrase is flagged only when models use
it far more often than people did. [The evidence](evidence/EVIDENCE.md) lists
every number, including the 13 phrases that didn't make the cut because people
use them too.

| Grade | Human docs, pre-2022 | Model samples |
|---|---:|---:|
| A | 67 | 8 |
| B | 35 | 1 |
| C | 20 | 7 |
| D | 12 | 7 |
| F | 1 | 17 |

One human document in 135 got an F. Seventeen model samples in 40 did.

## Four ways to use it

### 1. Claude Code plugin

```text
/plugin marketplace add dadwritestech/awesome-voice
/plugin install no-slop@awesome-voice
```

A hook checks every Markdown and text file Claude writes. If the file has
tells, Claude sees the list with a fix for each one and rewrites it before you
read it. The plugin also adds a `no-slop` skill, `/slop` to check files on
demand, and `/voice` to pick a brand voice. Details: [plugin/README.md](plugin/README.md).

### 2. Command line

```bash
npx no-slop README.md docs/*.md
npx no-slop --max-grade B CHANGELOG.md   # exit 1 if worse than B
cat draft.txt | npx no-slop -
```

Zero dependencies. Prints each tell with its line and the fix.

### 3. GitHub Action

```yaml
- uses: actions/checkout@v4
- uses: dadwritestech/awesome-voice@main
  with:
    files: "*.md docs/**/*.md"
    max-grade: C
```

### 4. A voice file

Any agent that reads `AGENTS.md` or `CLAUDE.md` can follow a VOICE.md. Copy
one into your project:

```bash
curl -o VOICE.md https://raw.githubusercontent.com/dadwritestech/awesome-voice/main/voices/no-slop/VOICE.md
```

Then add one line to `AGENTS.md` or `CLAUDE.md`:

```markdown
When you write any prose (docs, UI text, errors, release notes), follow VOICE.md.
```

## The voices

`no-slop` is the plain baseline. The rest follow a company's published style
guide, so your docs can sound like theirs instead of like a chatbot.

| Voice | Basis | In one line |
|---|---|---|
| [No slop](voices/no-slop/VOICE.md) | Measured | Plain, specific prose with none of the measured tells. |
| [GOV.UK](voices/gov-uk/VOICE.md) | Published guide | Plain English for public services. Short sentences, `cannot` instead of `can't`. |
| [Mailchimp](voices/mailchimp/VOICE.md) | Published guide | Plainspoken, warm, quietly funny. Never oversells. |
| [Google developer docs](voices/google-developer/VOICE.md) | Published guide | A knowledgeable friend explaining an API. Conversational, not cute. |
| [Microsoft](voices/microsoft/VOICE.md) | Published guide | Warm and relaxed, crisp and clear. Bigger ideas, fewer words. |
| [Stripe docs](voices/stripe-docs/VOICE.md) | Observed | Precise and calm. Names the exact error. |
| [Shopify Polaris](voices/shopify-polaris/VOICE.md) | Published guide | Lean interface copy that starts with the verb. |
| [GitLab docs](voices/gitlab-docs/VOICE.md) | Published guide | Concise task docs with a strict word list: select, not click. |
| [Atlassian](voices/atlassian/VOICE.md) | Published guide | Bold and practical, with a wink only when things go well. |
| [Red Hat docs](voices/red-hat/VOICE.md) | Published guide | Minimalist enterprise docs. No contractions, a check after every task. |

<!-- no-slop off -->
The voices disagree with each other, and that's useful. GOV.UK bans negative
contractions because readers misread them. Google recommends them because
readers miss a lone "not". Atlassian's own guide uses words that the no-slop
list flags, such as "seamless" and "empower". A generic "write clearly" prompt
can't hold all of that. A file per voice can.
<!-- no-slop on -->

## Does a voice file change what the model writes?

Measured on 2026-10-28 with `gemma-4-12b` on llama-server: 4 prompts, 2
samples each, temperature 0.7, with and without the VOICE.md. Fit is 0 to 100
and counts how closely the text follows the measurable rules in the file.
[Full report](results/results.md), [raw outputs](results/generations.jsonl).

| Voice | Fit without | Fit with | Change | Banned-phrase hits |
|---|---:|---:|---:|---|
| Google developer docs | 82 | 96 | +14 | 11 → 0 |
| Stripe docs | 83 | 95 | +12 | 8 → 0 |
| GOV.UK | 87 | 98 | +11 | 7 → 0 |
| Microsoft | 86 | 97 | +11 | 1 → 0 |
| Mailchimp | 88 | 97 | +9 | 0 → 0 |

Half of the baseline samples had an exclamation mark and half had an emoji.
None of the voiced samples did.

<!-- no-slop off -->

"Write the body of a welcome email for a project-management app."

| Without VOICE.md | With Mailchimp VOICE.md |
|---|---|
| Welcome to the team! We're thrilled to have you on board. [App Name] is designed to help you streamline your workflow, track your milestones, and crush your goals without the stress. Whether you're managing a small team or a massive project, we're here to make your life easier. | We're glad you're here. You can now start organizing your projects and keeping your team on track. Most people begin by creating their first project board. It takes about 2 minutes to set up your workspace and invite your coworkers. |

<!-- no-slop on -->

To lint text against a voice's own rules, use the scorer:

```bash
python score/voicescore.py check --voice gov-uk docs/release-notes.md
python score/voicescore.py selftest
```

## What this doesn't prove

- All model samples come from one local model, `gemma-4-12b`. Other models
  have other habits. Samples from more models would make the list fairer, and
  [CONTRIBUTING.md](CONTRIBUTING.md) explains how to add them.
- A clean grade means the text avoids known tells. It doesn't mean a person
  wrote it, and a person can still get a D.
- The voice benchmark checks whether the model followed the rules in the file,
  not whether the output sounds like the real brand to a human reader.
- Sample sizes are small. Treat the numbers as a first measurement.

To skip a passage on purpose, such as a quote or a list of bad examples, wrap
it in `<!-- no-slop off -->` and `<!-- no-slop on -->`. To skip a tell for a
whole project, add its id to `.slopignore`.

## Contributing

New voices and model samples are both welcome. Start with
[CONTRIBUTING.md](CONTRIBUTING.md), [TEMPLATE.md](TEMPLATE.md) and
[FORMAT.md](FORMAT.md). Voices must come from a published guide or public
pages, cite every source, paraphrase, and pass `selftest`. No voices for
individual people.

## Disclaimer

The voice files are unofficial. They describe public writing styles and aren't
affiliated with or endorsed by GDS, Mailchimp, Intuit, Google, Microsoft,
Stripe, Shopify, GitLab, Atlassian or Red Hat. All trademarks belong to their
owners.

## License

Voices and format (`voices/`, `FORMAT.md`, `TEMPLATE.md`): [CC BY 4.0](LICENSE-CONTENT).
Code and tooling: [MIT](LICENSE).
