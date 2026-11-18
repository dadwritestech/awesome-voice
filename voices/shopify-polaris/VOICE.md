---
name: Shopify Polaris
slug: shopify-polaris
description: Lean, action-first interface copy that sounds like a merchant talking. Start with the verb, say only what the person needs to act, and skip the punctuation.
basis: published-guide
sources:
  - https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/content/fundamentals.mdx
  - https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/content/grammar-and-mechanics.mdx
  - https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/content/error-messages.mdx
targets:
  sentence_words: 5-14
  max_sentence_words: 22
  paragraph_sentences: 1-2
  contractions: use
  passive_max: 0.1
  exclamations: 0
  second_person: yes
---

# Shopify Polaris voice

> Unofficial. A paraphrase of the content guidelines Shopify publishes for its
> Polaris design system, listed above. Not endorsed by Shopify.

## Voice in one line

Tell the merchant the one thing to do next, in the fewest plain words that still make sense.

## Tone rules

- Weigh every word. Add text only when the interface isn't clear without it.
- Focus on the one thing the person needs to know or do next. Move everything else to a later step.
- Start sentences with a verb so they read as instructions: "Add a product", not "You can add a product".
- Write like the people who use the product talk. Use their jargon, not the company's.
- Aim for a 7th grade reading level. Read the text out loud; if it sounds like a person, ship it.
- Use contractions: "don't", "you'll", "can't".
- In errors, say what went wrong and what to do about it. Be specific, with the person's own data where you have it.
- Don't apologize at length, and don't bring "we" into an error unless the company caused it.
- Don't explain what happened behind the scenes unless it helps the person or there's no fix to offer.

## Banned phrases

- `invalid` → say what to enter: "Enter a title"
- `click here` → link the words that describe the destination
- `you can` → start with the verb
- `please` → (cut it)
- `oops` → say what happened
- `simply` → (cut it)
- `easily` → (cut it)
- `we're sorry for any inconvenience` → say what's wrong and how to fix it
- `in order to` → to

## Length

- Keep sentences short: 5 to 14 words on average, and 22 at most.
- Keep body text to 1 or 2 sentences. Break multi-part tasks into steps.
- Ask whether a word could be an icon, and whether a heading, subcopy and button could be just a button.

## Formatting

- Use sentence case for headings, buttons, card titles and email subject lines.
- Capitalize product names unique to the company. Don't capitalize generic features: "blogs", "navigation", "admin".
- Keep headings to one phrase with no closing punctuation. Prefer a conversational heading that names the task: "Secure your account with two-step authentication".
- Skip the period on single-sentence fragments, labels and list items. Punctuate when text has two or more sentences.
- Introduce a bulleted list with a colon or a heading. Never end list items with commas or semicolons.
- Use numerals for numbers: "You have 5 orders to fulfill".
- Use at most one "Learn more" link per screen, and keep punctuation outside the link.

## Terminology

| Use | Not |
|---|---|
| merchant | user (for the business owner) |
| Enter title | Invalid title |
| Add weight | Weight must be a number value greater than 0.1 lb |
| set up (verb), setup (noun) | setup (as a verb) |

<!-- no-slop off -->

## Before and after

### Empty state

**Before**

> Oops! It looks like you don't have any products yet. You can easily add your first product by clicking the button below!

**After**

> Add your first product. Products you add here show up in your online store.

### Form error

**Before**

> Invalid input. The value entered in the weight field must be a number that is greater than 0.1 lb in order to be accepted by the system.

**After**

> Enter a weight of at least 0.1 lb

### Outage banner

**Before**

> We're very sorry for any inconvenience, but we are currently experiencing some technical difficulties with our payments infrastructure, and our engineers are working hard on it.

**After**

> Payments are delayed. Orders still come in, and we'll process their payments when the problem is fixed.
