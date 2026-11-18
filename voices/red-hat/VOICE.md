---
name: Red Hat docs
slug: red-hat
description: Minimalist, task-focused enterprise documentation. No contractions, no fluff, a verification step after every task.
basis: published-guide
sources:
  - https://redhat-documentation.github.io/supplementary-style-guide/
targets:
  sentence_words: 10-22
  max_sentence_words: 32
  paragraph_sentences: 1-3
  contractions: avoid
  passive_max: 0.2
  exclamations: 0
  second_person: yes
---

# Red Hat docs voice

> Unofficial. A paraphrase of the Red Hat supplementary style guide for product
> documentation, listed above, which builds on the IBM Style guide. Not
> endorsed by Red Hat.

## Voice in one line

Give the reader the task they came for, in plain and exact sentences, and show them how to check that it worked.

## Tone rules

- Follow minimalism. Know what readers are trying to do, and cut everything that keeps them from real work.
- Keep concepts and background apart from procedures. A procedure is steps, not explanation.
- Cut fluff: no long introductions, no context the reader does not need to act.
- Avoid contractions in product documentation. They are harder to translate. Quick starts with a conversational tone are the exception.
- Use a less conversational tone in most documentation, and the least conversational tone for API references.
- Give a direct instruction instead of a suggestion: "Back up your data disk", not "We suggest that you back up your data disk".
- Expect mistakes. Include verification, error recovery and troubleshooting steps with each task.
- Write so that a search engine and a skimming reader both find the answer: short paragraphs, clear headings, lists where they help.

## Banned phrases

- `we suggest` → give the instruction
- `essentially` → (cut it)
- `basically` → (cut it)
- `totally` → (cut it)
- `as expected` → correctly
- `interesting` → say why it matters
- `it is interesting to note` → use a note admonition
- `lots of` → many
- `skill set` → skills
- `snippet` → piece, excerpt
- `bimonthly` → twice a month, or every two months
- `biweekly` → twice a week, or every two weeks

## Length

- Aim for 10 to 22 words per sentence. Shorten anything that runs past 32.
- Keep paragraphs to 1 to 3 sentences.
- Keep titles and headings between 3 and 11 words, with familiar keywords.

## Formatting

- Put one command in each code block, one code block per procedure step.
- Explain every variable a command uses, right after the code block.
- Mark values the reader replaces, and say what to replace them with.
- Use admonitions such as Note and Important for side information instead of phrases such as "it is interesting to note".
- Do not use exclamation points at the end of sentences.
- Write out "operating system" and "regular expression" instead of "OS" and "regex".

## Terminology

| Use | Not |
|---|---|
| operating system | OS |
| regular expression | regex |
| network interface controller | network interface card |
| node | minion |
| correctly | as expected |
| many | lots of, bunches of |
| skills | skill set |

<!-- no-slop off -->

## Before and after

### Procedure intro

**Before**

> In this section, we'll basically walk you through lots of interesting background on how the service works before we suggest that you configure it.

**After**

> Configure the service to start at boot. For background on how the service starts, see the architecture overview.

### Instruction

**Before**

> We suggest that you might want to make a backup of your data disk, since things don't always go as expected during an upgrade!

**After**

> Back up your data disk before you upgrade. If the upgrade fails, you can restore the disk from the backup.

### Verification

**Before**

> That's it, you're totally done! The regex should essentially be working now on your OS.

**After**

> Verify that the regular expression matches the test input by running the following command. The output lists one line for each match.
