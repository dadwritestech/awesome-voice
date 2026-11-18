# The VOICE.md format

A VOICE.md file tells an AI agent how to write. It's plain Markdown with a small
block of frontmatter. Agents read the prose; the scoring script reads the
frontmatter, the banned-phrase list, and the before/after examples.

Keep a VOICE.md under about 200 lines. It sits in the agent's context on every
request, so every line costs tokens.

## File layout

```
voices/<slug>/VOICE.md
```

Use a lowercase, hyphenated slug: `gov-uk`, `google-developer`.

## Frontmatter

```yaml
---
name: GOV.UK
slug: gov-uk
description: Plain English for public services. Short sentences, no jargon, no negative contractions.
basis: published-guide
sources:
  - https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style
targets:
  sentence_words: 8-18
  max_sentence_words: 25
  paragraph_sentences: 1-3
  contractions: avoid-negative
  passive_max: 0.10
  exclamations: 0
  second_person: yes
---
```

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Display name of the voice. |
| `slug` | yes | Matches the folder name. |
| `description` | yes | One sentence. Shown in the README table. |
| `basis` | yes | `published-guide` if the rules come from a style guide the organization publishes. `observed` if they're inferred from the organization's public pages because no guide is published. `measured` if they come from counting text, as in `evidence/`. |
| `sources` | yes | Public URLs the rules came from. Every rule in the file must trace back to one of these. |
| `targets` | yes | Measurable targets the scorer checks. See below. |

The frontmatter parser is deliberately small: `key: value` pairs, one level of
nested maps, and lists of `- item`. Don't use other YAML features.

### Targets

| Target | Value | What the scorer checks |
|---|---|---|
| `sentence_words` | `min-max` | Mean words per sentence falls in the range. |
| `max_sentence_words` | number | Share of sentences longer than this. |
| `paragraph_sentences` | `min-max` | Mean sentences per prose paragraph falls in the range. |
| `contractions` | `use`, `avoid`, or `avoid-negative` | Share of contractible phrases that are contracted (`you're` vs `you are`). `avoid-negative` only counts `can't`, `don't`, `won't` and similar. |
| `passive_max` | 0–1 | Share of sentences that look passive stays under this. |
| `exclamations` | number | Maximum exclamation marks per text. |
| `second_person` | `yes` or `no` | Whether the text addresses the reader as "you". |

Leave a target out if the source guide says nothing about it. Don't invent a
rule just to fill the table.

## Sections

Use these H2 headings, in this order. The scorer depends on the exact names of
**Banned phrases** and **Before and after**.

### `## Voice in one line`

One sentence an agent can hold in mind while writing.

### `## Tone rules`

A short list of rules, each one an instruction. Paraphrase the source; don't
copy it. Link to the source page when a rule needs more context.

### `## Banned phrases`

One phrase per bullet. Put the replacement after an arrow:

```markdown
- `utilise` → use
- `in order to` → to
- `please note` → (cut it)
```

The scorer matches the backticked text, case-insensitively, on word
boundaries. Only list phrases the source guide names, or that clearly break one
of its stated rules.

### `## Length`

Sentence and paragraph lengths in words and sentences. Keep the numbers in
step with `targets`.

### `## Formatting`

Headings, lists, capitalization, numbers, dates, code, UI labels.

### `## Terminology`

A two-column table: use this, not that.

### `## Before and after`

Three to five rewrites. Each one is an H3 with a label, then a **Before** quote
and an **After** quote:

```markdown
### Error message

**Before**

> An error has occurred. Please try again later.

**After**

> We couldn't save your changes. Check your connection and try again.
```

Write the **Before** in generic assistant prose. Write the **After** in the
voice. The scorer runs on both as a self-test: every **After** should score
higher than its **Before**. If it doesn't, the targets or the example are wrong.

## Rules for contributors

- Source rules from the organization's published style guide or its public
  pages. Cite every page in `sources`.
- Paraphrase. Quote at most a few words from a source.
- Don't write a voice file for an individual person.
- Mark the file as unofficial. These files describe a public style; they aren't
  endorsed by the organizations named.
