---
name: Stripe docs
slug: stripe-docs
description: Precise, calm developer docs. Lead with what the thing does, state conditions plainly, and name the exact object or error.
basis: observed
sources:
  - https://docs.stripe.com/keys
  - https://docs.stripe.com/error-handling
  - https://docs.stripe.com/api/errors
  - https://docs.stripe.com/payments/quickstart
  - https://stripe.com/blog/markdoc
targets:
  sentence_words: 10-22
  max_sentence_words: 32
  paragraph_sentences: 1-3
  contractions: use
  passive_max: 0.15
  exclamations: 0
  second_person: yes
---

# Stripe docs voice

> Unofficial. Stripe doesn't publish a writing style guide. This file describes
> patterns observed on Stripe's public documentation pages listed above. Not
> endorsed by Stripe.

## Voice in one line

State what the thing does and what the reader should do about it, with the
exact names, in calm and precise sentences.

## Tone rules

- Open every page with one sentence that says what the feature does for the reader's integration.
- Follow it with the decision the reader has to make: "Choose the key type that matches where your code runs."
- Be precise. Name the exact object, parameter, error type, or key prefix. Don't say "the relevant credential" when you mean `sk_live_`.
- Describe behavior as cause and effect: "If a request includes an expired key, Stripe returns an authentication error."
- Refer to the company as "Stripe" when describing what the system does. Use "we" for recommendations: "We recommend…".
- Address the reader as "you" and their code as "your integration".
- Write for someone building real money flows. Stay calm and neutral. No hype, no jokes, no exclamation marks.
- Explain why a recommendation matters in terms of risk to the reader's business, not abstract best practice.
- Use contractions in prose: "you're", "doesn't", "can't".
- Split guidance by reader situation: "If you're new to Stripe", "When you're ready to accept real payments".

## Banned phrases

These are absent from the observed pages and conflict with the patterns above.

- `simply` → (cut it)
- `just` → (cut it, when it means "simply")
- `easily` → (cut it)
- `seamless` → say what happens
- `powerful` → say what it does
- `robust` → say what it handles
- `best-in-class` → (cut it)
- `effortless` → (cut it)
- `magic` → say what happens
- `unlock` → use, enable
- `leverage` → use
- `utilize` → use
- `please` → (cut it)
- `it should be noted` → (cut it)

## Length

- Aim for 10 to 22 words per sentence on average.
- A sentence can carry one condition and one result. Split anything longer than 32 words.
- Keep paragraphs to 1 to 3 sentences. Use a table when you compare three or more options on the same attributes.

## Formatting

- Use sentence case for titles and headings. Make headings task-shaped: "Handle errors", "Rotate a key".
- Put object names, parameters, values, key prefixes, and error codes in `code font`: `PaymentIntent`, `idempotency_key`, `card_declined`.
- Capitalize Stripe product and object names as Stripe does: Dashboard, Checkout, PaymentIntent.
- Use a bold label followed by a colon to lead a situational bullet: **Build and test**: Create a sandbox…
- Use tables for comparisons: type, whether it's safe to expose, description.
- Show code for every step a developer must run. Keep prose before the code to one or two sentences.

## Terminology

| Use | Not |
|---|---|
| your integration | your app, your system (when talking about Stripe calls) |
| sandbox, test keys | dev mode, fake keys |
| live mode | production mode |
| secret key, publishable key, restricted key | private key, public key, limited key |
| customer | user (for the person paying) |
| Dashboard | dashboard, admin panel |

## Before and after

### Page opening

**Before**

> Welcome to our powerful API key system! API keys are a super important part of security, and in this guide we'll walk you through everything you need to know about them.

**After**

> Stripe uses API keys to authenticate requests from your integration. Choose the key type that matches where your code runs.

### Error behavior

**Before**

> Sometimes things can go wrong with your request, and an error might be returned. It should be noted that errors can be handled easily with our SDKs.

**After**

> If a request doesn't include a valid key, Stripe returns an `invalid_request_error`. If the key has expired, Stripe returns an `authentication_error`.

### Recommendation

**Before**

> It is generally considered a best practice to simply use restricted keys wherever possible for more robust security.

**After**

> We recommend restricted keys for new integrations. If someone gets your key, it can only do what you allowed it to do.

### Retry guidance

**Before**

> If there's a network problem, just try again and everything should work seamlessly!

**After**

> If the connection fails, retry the request with the same idempotency key and parameters. Stripe won't create a second charge.
