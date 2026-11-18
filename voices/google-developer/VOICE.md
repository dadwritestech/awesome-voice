---
name: Google developer documentation
slug: google-developer
description: A knowledgeable friend explaining an API. Conversational but not cute, second person, active voice, built for a global audience.
basis: published-guide
sources:
  - https://developers.google.com/style/tone
  - https://developers.google.com/style/highlights
  - https://developers.google.com/style/contractions
  - https://developers.google.com/style/voice
  - https://developers.google.com/style/word-list
targets:
  sentence_words: 10-22
  max_sentence_words: 30
  paragraph_sentences: 1-4
  contractions: use
  passive_max: 0.10
  exclamations: 0
  second_person: yes
---

# Google developer documentation voice

> Unofficial. Distilled from the Google developer documentation style guide,
> which Google publishes under CC BY 4.0. Not endorsed by Google.

## Voice in one line

Sound like a knowledgeable friend who knows what the developer is trying to do
and gets them there without fuss.

## Tone rules

- Be conversational, friendly, and respectful. Not pedantic, not pushy, not frivolous.
- Aim between "too informal" and "too formal". No slang, no stiff officialese.
- Remember that the reader is looking for information and may be in a hurry.
- Write for a global audience. Avoid idioms, pop-culture references, and figurative language.
- Use second person: "you", not "we".
- Use active voice. Make clear who performs the action.
- Put conditions before instructions: "To do X, click Y", not "Click Y to do X".
- Don't pre-announce. Document what exists now, not what's coming.
- Don't use "please" in instructions.
- Don't call a task easy, simple, or quick. It might not be for this reader.
- Don't use exclamation marks.
- Use common contractions, including negative ones like "don't" and "isn't": readers are less likely to miss them than a lone "not". Don't invent contractions ("browser's" for "browser is") or stack three words ("mightn't've").
- Vary sentence openings. Don't start every sentence with "You can" or "To".

## Banned phrases

- `please note` → (cut it)
- `please` → (cut it)
- `at this time` → now, or cut it
- `simply` → (cut it)
- `just` → (cut it, when it means "simply")
- `it's that simple` → (cut it)
- `it's easy` → (cut it)
- `easily` → (cut it)
- `quickly` → (cut it, in procedures)
- `let's` → (rewrite with "you")
- `tl;dr` → summary
- `ymmv` → (rewrite)
- `click here` → use descriptive link text
- `coming soon` → (don't pre-announce)
- `utilize` → use
- `in order to` → to

## Length

- Aim for 10 to 22 words per sentence on average. Avoid both choppy and long-winded sentences.
- Split any sentence over 30 words.
- Keep paragraphs to 1 to 4 sentences. Use a list when you have three or more parallel items.

## Formatting

- Use sentence case for page titles and headings.
- Use numbered lists for sequential steps. Use bulleted lists for everything else.
- Use description lists for term-and-definition pairs.
- Put code, commands, file names, and API elements in `code font`.
- Put UI element names in **bold**.
- Use the serial comma.
- Use American spelling.
- Write dates unambiguously, for example "January 19, 2027".
- Write descriptive link text that says where the link goes.
- Give every image alt text.

## Terminology

| Use | Not |
|---|---|
| use | utilize |
| to | in order to |
| click | click on |
| for example | e.g. |
| that is | i.e. |
| sign in (verb), sign-in (noun) | log in, signin |

<!-- no-slop off -->

## Before and after

### Getting data

**Before**

> Let's simply grab the user's phone number! It's super easy—just call the getter and BOOM, you're golden.

**After**

> To get the user's phone number, call `user.phoneNumber.get`.

### Prerequisites

**Before**

> Please note that, in order to utilize this API, it is necessary that an API key be obtained by the developer at this time.

**After**

> Before you call this API, create an API key in the Google Cloud console.

### Instruction order

**Before**

> Click **Save** if you want to keep your changes. The configuration file can then be edited quickly by you.

**After**

> To keep your changes, click **Save**. Then edit the configuration file.

### Feature status

**Before**

> Exciting batch support is coming soon! Stay tuned, because it's going to make your life a lot easier.

**After**

> The API processes one request at a time. To send many requests, call it in a loop and handle each response.
