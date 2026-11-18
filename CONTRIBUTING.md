# Contributing

Two kinds of contribution help most: new voices, and model samples for the
evidence.

## Add a voice

1. Copy `TEMPLATE.md` to `voices/<slug>/VOICE.md`.
2. Fill it in from the organization's published style guide. Cite every page
   in `sources`, paraphrase, and keep the "Unofficial" line.
3. Run the checks:

   ```bash
   python score/voicescore.py selftest
   node plugin/slop/cli.js voices/<slug>/VOICE.md
   python -m pytest -q score/ tests/
   ```

   Every **After** must beat its **Before** in the selftest, and the file
   should grade A or B. Wrap quoted bad examples (the Terminology table and
   the Before and after section) in `<!-- no-slop off -->` so the checker
   skips them.
4. Open a pull request with the selftest table in the description.

`FORMAT.md` explains every field and section.

## Add model samples

The tell list in `plugin/slop/tells.json` is measured, not guessed. Right now
the model side comes from one local model, so samples from other models make
it more honest.

1. Run the 20 prompts in `evidence/prompts.json` through a model, twice each,
   with no system prompt beyond "You are a helpful assistant."
2. Append one JSON line per answer to `evidence/models.jsonl`, in the same
   shape as the existing lines, with the model name in `model`.
3. Run `python evidence/measure.py --write` and include the changed
   `EVIDENCE.md` in your pull request.

## Add or drop a tell

Open an issue with the phrase, a few real examples, and where they came from.
A tell joins the list only when the numbers in `evidence/` support it.
