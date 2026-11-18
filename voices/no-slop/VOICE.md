---
name: No slop
slug: no-slop
description: Plain, specific writing with none of the habits that make text read as AI-written. Works on its own or under any other voice.
basis: measured
sources:
  - https://github.com/dadwritestech/awesome-voice/blob/main/evidence/EVIDENCE.md
  - https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
targets:
  sentence_words: 8-20
  max_sentence_words: 30
  paragraph_sentences: 1-4
  contractions: use
  passive_max: 0.15
  exclamations: 0
  second_person: yes
---

# No slop voice

> Built from measurement, not from a brand. Every banned phrase and habit here
> shows up far more often in model output than in open-source READMEs and
> release notes written before ChatGPT. The numbers are in
> evidence/EVIDENCE.md. Use this voice alone, or stack it under a brand voice.

## Voice in one line

Say the specific thing in plain words, once, and stop.

## Tone rules

- Start with the content. The first sentence of any document carries a fact the reader needs.
- Replace each adjective you cannot prove with the fact behind it: a number, a name, a step count, a before and after.
- Write for one reader. Pick who they are and what they're trying to do, and leave everyone else out.
- Say what a thing is once. Don't define it by what it isn't.
- Stop when the information stops. No recap paragraph, no sign-off, no offer of more help.
- Stay level. No excitement, no reassurance, no exclamation marks. Good news reads as good news without them.
- Never leave a placeholder in brackets. Ask for the value or write around it.
- Use contractions. They read as a person talking.
- Keep a technical term when it is the right term, even if it appears in the banned list below as a filler word.

## Banned phrases

Each of these appears at least 3 times as often in model output as in human writing, or humans almost never write it at all.

- `seamless` → say what doesn't break
- `whether you're` → name one reader
- `effortless` → say how few steps it takes
- `we're excited to announce` → (cut it) and say what shipped
- `robust` → say what it survives
- `ensure` → make sure, or say how
- `powerful` → give the number
- `blazing fast` → give the number
- `journey` → (cut it), or name the steps
- `best practices` → name the practice
- `delve` → look at, cover, explain
- `leverage` → use
- `harness` → use
- `streamline` → say what got shorter
- `elevate` → improve, or say what changes
- `empower` → lets, helps
- `unlock` → lets you
- `crucial` → say why it matters
- `game-changer` → say what changed and by how much
- `cutting-edge` → new, or name the technique
- `designed to help` → say what it does
- `in today's` → (cut it)
- `in conclusion` → (cut it), or end on the last fact
- `hope this helps` → (cut it)
- `happy coding` → (cut it)
- `great question` → (cut it) and answer
- `don't worry` → (cut it) and give the answer
- `look no further` → (cut it)

## Length

- Aim for 8 to 20 words per sentence on average. Split anything longer than 30 words.
- Keep paragraphs to 1 to 4 sentences.
- A short document is fine. Cut every sentence that a reader would skip.

## Formatting

- Use sentence case for headings: "Install the CLI", not "Install The CLI".
- Write list items as plain sentences. Don't open each bullet with a bold label and a colon; if items need labels, use a table or headings.
- Use full stops and commas, not em dashes.
- No emoji in headings, bullets or release notes.
- Put commands, file names, flags and values in `code font`.

## Terminology

<!-- no-slop off -->

| Use | Not |
|---|---|
| use | leverage, utilize, harness |
| lets you | empowers you to, unlocks |
| make sure | ensure |
| new | cutting-edge, next-generation |
| shows | showcases, underscores |
| start | embark on |
| has | boasts |

<!-- no-slop on -->

## Before and after

<!-- no-slop off -->

### Release note

**Before**

> We're thrilled to announce version 2.4! This release brings seamless offline sync, a blazing fast search index, and crucial stability enhancements to elevate your note-taking journey.

**After**

> Version 2.4 works offline. Notes you edit without a connection sync when you're back online. Search is about four times faster on large notebooks, and pasting an image no longer crashes the app.

### README intro

**Before**

> Whether you're a seasoned developer or just getting started, dupefind is a powerful, intuitive tool designed to help you streamline your disk cleanup effortlessly.

**After**

> dupefind finds duplicate files on your disk and tells you how much space you'd get back. It compares sizes first and hashes only files that match, so a 500 GB drive takes about a minute.

### Pull request

**Before**

> This PR implements robust retry logic to ensure reliable uploads, leveraging exponential backoff in line with industry best practices for optimal performance.

**After**

> Uploads now retry up to five times on a timeout or a server error. The wait doubles each time, from 1 second to 16. A bad request still fails at once, since retrying won't fix it.

### Support reply

**Before**

> Great question! Don't worry, resetting your password is effortless. Simply click the link in your inbox and you'll be all set. Hope this helps, and happy browsing!

**After**

> Open the email we sent you and click Reset password. The link works for one hour. If it has expired, request a new one from the sign-in page.

<!-- no-slop on -->
