# no-slop

Finds the habits that make writing read as AI-written, and makes your coding
agent fix them before you read the text.

Every rule was measured. Models write each of these tells at least 3 times as
often as people did in open-source READMEs and release notes from before
ChatGPT, or people almost never write it at all. See the
[evidence](https://github.com/dadwritestech/awesome-voice/blob/main/evidence/EVIDENCE.md).

## Claude Code

```
/plugin marketplace add dadwritestech/awesome-voice
/plugin install no-slop@awesome-voice
```

You get three things:

- A hook. After the agent writes or edits a Markdown or text file, the hook scans what it wrote. If it finds tells, it sends the list back and the agent rewrites those lines. Code files are never checked.
- A skill with the writing rules, so the agent avoids the tells in the first place.
- `/slop <file>` to check a file by hand, and `/voice <name>` to add a brand voice from this repo to your project.

To turn the hook off for a session, set `NO_SLOP=off`. To silence one tell or
one folder for a project, list it in a `.slopignore` file:

```
seamless      # we sell seamless gutters
docs/legal/
```

To keep quoted bad examples in a document, wrap them:
`<!-- no-slop off -->` ... `<!-- no-slop on -->`.

## Command line

```bash
npx no-slop README.md docs/*.md
npx no-slop --max-grade B CHANGELOG.md
cat draft.txt | npx no-slop -
```

`--max-grade B` exits 1 if any file grades worse than B, for CI. `--json`
prints every hit with its offsets.

## Grades

A grade is tells per 100 words, cut at the distribution of the human documents:
A is the human median or better, B the 75th percentile, C the 90th, D twice
that, F above. Most human READMEs get A or B. Most raw model output gets D or F.

## Other agents

Codex, Cursor and other agents read `AGENTS.md` or rules files. Copy
[SKILL.md](skills/no-slop/SKILL.md) into one of them, and run
`npx no-slop` in CI to check the result.

MIT licensed.
