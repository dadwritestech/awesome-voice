---
description: Check files for AI-writing tells and rewrite what it finds
argument-hint: [files...]
allowed-tools: Bash(node:*), Read, Edit
---

Run the slop checker on these files (if none were given, use the Markdown files changed in `git status`, or README.md):

!`node "${CLAUDE_PLUGIN_ROOT}/slop/cli.js" $ARGUMENTS 2>&1 || true`

For each tell listed, rewrite the passage in plain, specific language, following the no-slop skill. Keep a flagged phrase only if it is quoted text, a product name, or a technical term. Then run the checker again and report the grade before and after.
