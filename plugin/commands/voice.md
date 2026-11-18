---
description: Add a brand VOICE.md (gov-uk, mailchimp, google-developer, microsoft, stripe-docs, and more) to this project
argument-hint: <voice-slug>
allowed-tools: Bash(curl:*), Read, Edit, Write
---

Install the VOICE.md for the voice "$ARGUMENTS" from https://github.com/dadwritestech/awesome-voice.

1. If no voice was given, list the folders in https://github.com/dadwritestech/awesome-voice/tree/main/voices with their one-line descriptions from the README, and ask which one to use.
2. Download it to the project root: `curl -fsSL -o VOICE.md https://raw.githubusercontent.com/dadwritestech/awesome-voice/main/voices/$ARGUMENTS/VOICE.md`
3. If CLAUDE.md or AGENTS.md exists, add one line to it (do not duplicate it): `When you write any prose (docs, UI text, errors, release notes), follow VOICE.md.`
4. Say which voice is installed and show its "Voice in one line".
