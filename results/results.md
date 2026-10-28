Model: `gemma-4-12b`. 8 baseline sample(s); each voice scored on the same prompts with its VOICE.md in the system prompt.

| Voice | Fit without VOICE.md | Fit with VOICE.md | Change | Banned-phrase hits (without → with) | Mean sentence words (without → with) | Target | Embedding: closer to After examples (without → with) |
|---|---:|---:|---:|---|---|---|---|
| Google developer documentation | 82 | 96 | +14 | 11 → 0 | 11.0 → 10.4 | 10-22 | -0.042 → -0.023 |
| GOV.UK | 87 | 98 | +11 | 7 → 0 | 11.0 → 8.7 | 8-18 | -0.034 → +0.003 |
| Mailchimp | 88 | 97 | +9 | 0 → 0 | 11.0 → 10.6 | 8-18 | -0.012 → +0.006 |
| Microsoft | 86 | 97 | +11 | 1 → 0 | 11.0 → 8.3 | 6-16 | -0.010 → +0.016 |
| Stripe docs | 83 | 95 | +12 | 8 → 0 | 11.0 → 10.4 | 10-22 | -0.001 → +0.040 |

Per-target scores (0-1, without → with):

| Voice | sentence_length | long_sentences | paragraph_length | contractions | passive_voice | exclamations | second_person | banned_phrases |
|---|---|---|---|---|---|---|---|---|
| google-developer | 0.93 → 0.92 | 1.00 → 1.00 | 1.00 → 1.00 | 0.57 → 0.82 | 0.93 → 1.00 | 0.62 → 1.00 | 0.78 → 0.92 | 0.66 → 1.00 |
| gov-uk | 0.97 → 0.97 | 0.96 → 1.00 | 1.00 → 1.00 | 1.00 → 1.00 | 0.93 → 1.00 | 0.62 → 1.00 | 0.78 → 0.86 | 0.78 → 1.00 |
| mailchimp | 0.97 → 1.00 | 1.00 → 1.00 | 1.00 → 1.00 | 0.57 → 0.93 | 0.93 → 1.00 | 0.75 → 1.00 | 0.78 → 0.83 | 1.00 → 1.00 |
| microsoft | 1.00 → 1.00 | 0.96 → 1.00 | 1.00 → 1.00 | 0.57 → 0.86 | 0.93 → 1.00 | 0.62 → 1.00 | 0.78 → 0.86 | 0.97 → 1.00 |
| stripe-docs | 0.93 → 0.97 | 1.00 → 1.00 | 1.00 → 1.00 | 0.57 → 0.75 | 0.96 → 1.00 | 0.62 → 1.00 | 0.78 → 0.91 | 0.75 → 1.00 |

Generic AI-tell phrases in baseline output: 6 across 8 sample(s).
- with Google developer documentation: 1 across 8 sample(s)
- with GOV.UK: 0 across 8 sample(s)
- with Mailchimp: 0 across 8 sample(s)
- with Microsoft: 2 across 8 sample(s)
- with Stripe docs: 0 across 8 sample(s)
