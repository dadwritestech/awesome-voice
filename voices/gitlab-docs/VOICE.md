---
name: GitLab docs
slug: gitlab-docs
description: Concise, direct product docs written from the reader's task. Plain verbs, no promises about the future, and a precise word list.
basis: published-guide
sources:
  - https://docs.gitlab.com/development/documentation/styleguide/
  - https://docs.gitlab.com/development/documentation/styleguide/word_list/
targets:
  sentence_words: 8-20
  max_sentence_words: 30
  paragraph_sentences: 1-3
  contractions: use
  passive_max: 0.15
  exclamations: 0
  second_person: yes
---

# GitLab docs voice

> Unofficial. A paraphrase of the documentation style guide and word list
> GitLab publishes, listed above. Not endorsed by GitLab.

## Voice in one line

Tell the reader how to reach their goal, in concise, direct and precise sentences.

## Tone rules

- Be concise, direct and precise. Be conversational but brief, and friendly but short.
- Write from the reader's side: their goal, the steps, the result. Not how the feature was built.
- Don't say a task is easy. If the reader finds it hard, you've lost their trust.
- Avoid "we". Say what the reader can do in the product.
- Don't promise future releases. Link to an issue instead.
- Don't restate the title or earlier sections. Each section adds something new.
- Describe only behavior you can confirm. Don't invent commands, parameters or UI names.
- Write for translation: no idioms, no Latin abbreviations, no "since" when you mean "because".

## Banned phrases

- `simply` → (cut it)
- `easily` → (cut it)
- `utilize` → use
- `in order to` → to
- `note that` → (cut it) and state the fact
- `please` → (cut it)
- `click` → select
- `navigate to` → go to
- `enable` → turn on
- `disable` → turn off
- `currently` → (cut it)
- `basically` → (cut it)
- `e.g.` → for example
- `via` → with, through, or by using
- `and above` → and later
- `handy` → (cut it)

## Length

- Aim for 8 to 20 words per sentence. Break up anything over 30.
- Keep paragraphs to 1 to 3 sentences. Use a list or table instead of a long sentence with many parts.
- Break up noun strings: "custom settings for project integrations", not "project integration custom settings".

## Formatting

- Use sentence case for headings.
- Bold UI elements the reader selects: Select **Run pipeline**. Don't add "button" after the name.
- Write versions as "GitLab 17.1 and later" or "and earlier". Never "above", "higher", "newer" or "lower".
- Use "select" for buttons, links, menu items and lists, since it works on any device.
- Spell out abbreviations on first use, except common ones such as CI/CD.

## Terminology

| Use | Not |
|---|---|
| select | click |
| turn on, turn off | enable, disable |
| go to | navigate to |
| sign in | log in, sign on |
| set up (verb), setup (noun) | setup (as a verb) |
| later, earlier (for versions) | above, newer, lower |
| following | below |
| create | create new |

<!-- no-slop off -->

## Before and after

### Procedure

**Before**

> In order to enable the feature, simply navigate to the Settings page and click the Save button below.

**After**

> To turn on the feature, go to **Settings** and select **Save**.

### Version note

**Before**

> Note that this functionality is currently only available in GitLab 16.4 and above, and we are planning to bring it to more tiers soon.

**After**

> In GitLab 16.4 and later, this feature is available on the Premium and Ultimate tiers.

### Feature intro

**Before**

> We built merge trains to basically make it easy for teams to utilize a handy queue for merging, e.g. when many people merge at once.

**After**

> Use merge trains to queue merge requests. Each one is tested with the changes ahead of it, so the target branch stays green when many people merge at once.
