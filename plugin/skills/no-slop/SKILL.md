---
name: no-slop
description: Use whenever you write prose a person will read, such as a README, docs, release notes, a PR description, a commit message, an email, UI text or an error message. Removes the habits that make text read as AI-written.
---

# Write like a person, not like a model

Readers now spot AI-written text in a sentence or two, and they stop trusting
it. The habits below give it away. Each one was measured: models write them
far more often than people did in open-source READMEs and release notes from
before ChatGPT. See the evidence at
https://github.com/dadwritestech/awesome-voice/blob/main/evidence/EVIDENCE.md

## The rules

The quoted phrases below are the bad examples, so the checker skips this part.

<!-- no-slop off -->
1. Say the specific thing. Replace every adjective you cannot prove with
   the fact behind it. "Fast" becomes "parses 1 GB in 2 seconds". "Seamless"
   becomes "syncs in the background; you don't press anything".
2. Start with the content. No "Here's a...", no "Great question", no
   "We're excited to announce". The first sentence carries information.
3. Stop when you're done. No summary paragraph, no "In conclusion", no
   "Let me know if you have questions", no "Happy coding".
4. Write plain lists. Don't open every bullet with a bold label and a
   colon. If the items need labels, use a table or headings.
5. Use full stops. Not em dashes, not exclamation marks. A comma or a
   colon does the job an em dash was doing.
6. Talk to one reader. Not "whether you're a beginner or an expert". Pick
   the reader and write for them.
7. Say what it is, once. Not "it's not just a tool, it's a platform".
8. Never leave placeholders. No `[Your Name]` or `[Company]`. Ask for the
   value, or write around it.
9. Sentence case for headings. "Install the CLI", not "Install The CLI".

## Words and phrases to replace

Write the plain word. If no plain word fits, the sentence probably said
nothing; cut it.

| Instead of | Write |
|---|---|
| seamless, seamlessly | say what doesn't break |
| ensure | make sure, or say how |
| robust, powerful, blazing fast | the number that proves it |
| leverage, utilize, harness | use |
| streamline, enhance, elevate | say what got shorter, faster or better |
| empower, unlock, unleash | lets you |
| comprehensive | say what it covers |
| crucial, vital, pivotal | say why it matters |
| delve, dive into, deep dive | (cut it) and start |
| whether you're... | (name one reader) |
| it's worth noting, it's important to note | (cut it) and state the fact |
| we're excited / thrilled to announce | (cut it) and say what shipped |
| designed to help you | say what it does |
| in today's fast-paced world | (cut it) |
| a testament to, tapestry, realm, landscape | say what you mean |
| feel free to, don't hesitate to, reach out | (cut it), or give one contact route |
| best practices, out of the box | name the practice; name what it works with |

## Before and after

**Release note**

> We're thrilled to announce v2.4! 🚀 This release brings **seamless offline sync**, a **blazing fast** search index, and crucial stability enhancements to elevate your note-taking experience.

> v2.4 works offline. Notes you edit without a connection sync when you're back online. Search is about 4x faster on large notebooks, and pasting an image no longer crashes the app.

**README intro**

> Whether you're a seasoned developer or just getting started, dupefind is a powerful, intuitive tool designed to help you streamline your disk cleanup — effortlessly.

> dupefind finds duplicate files on your disk and tells you how much space you'd get back. It compares file sizes first and hashes only the files that match, so a 500 GB drive takes about a minute.

**PR description**

> ## Overview
> - **Retry Logic:** Implements robust retry logic to ensure reliable uploads.
> - **Exponential Backoff:** Leverages exponential backoff for optimal performance.

> Uploads now retry up to 5 times on a timeout or a 5xx response, waiting 1, 2, 4, 8 and 16 seconds between tries. A 4xx still fails at once, since retrying won't fix a bad request.

<!-- no-slop on -->

## Check your own text

If this skill came with the no-slop plugin, a hook checks every Markdown or
text file you write and lists the tells it finds. Fix them before you move on.
You can also run the checker yourself:

```bash
node "${CLAUDE_PLUGIN_ROOT}/slop/cli.js" README.md
npx no-slop README.md
```

A flagged phrase can stay when it is quoted text, a product name, or a
technical term (`ensure` in a quoted API name, `robust` in
`robust statistics`). Everything else gets rewritten.
