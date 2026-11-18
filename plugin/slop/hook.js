#!/usr/bin/env node
// Claude Code PostToolUse hook. After the agent writes prose (Markdown, text,
// docs), scan what it just wrote for AI tells. If it finds any, exit 2 so the
// list goes back to the agent, which rewrites those lines before you read them.
//
// Off switches: NO_SLOP=off in the environment, or a .slopignore file in the
// project root listing tell ids (one per line) or path prefixes ("docs/legal/").
'use strict';
const fs = require('fs');
const path = require('path');
const { scan } = require('./slop.js');

const PROSE = /\.(md|mdx|markdown|txt|rst|adoc|asciidoc)$|(^|[\\/])(COMMIT_EDITMSG|README|CHANGELOG|CONTRIBUTING)$/i;
const SKIP_DIRS = /(^|[\\/])(node_modules|vendor|\.git|dist|build|target)[\\/]/;
const MAX_LISTED = 12;

function readStdin() {
  try { return fs.readFileSync(0, 'utf8'); } catch { return ''; }
}

function writtenText(tool, input) {
  if (tool === 'Write') return input.content || '';
  if (tool === 'Edit') return input.new_string || '';
  if (tool === 'MultiEdit') return (input.edits || []).map((e) => e.new_string || '').join('\n\n');
  return '';
}

function loadIgnore(cwd) {
  try {
    return fs.readFileSync(path.join(cwd, '.slopignore'), 'utf8')
      .split(/\r?\n/).map((l) => l.replace(/#.*/, '').trim()).filter(Boolean);
  } catch { return []; }
}

function main() {
  if (/^(off|0|false)$/i.test(process.env.NO_SLOP || '')) return 0;
  let event;
  try { event = JSON.parse(readStdin() || '{}'); } catch { return 0; }
  const input = event.tool_input || {};
  const file = input.file_path || '';
  if (!file || !PROSE.test(file) || SKIP_DIRS.test(file)) return 0;

  const cwd = event.cwd || process.cwd();
  const rel = path.relative(cwd, file).replace(/\\/g, '/');
  const ignore = loadIgnore(cwd);
  if (ignore.some((p) => p.includes('/') && rel.startsWith(p.replace(/^\.\//, '')))) return 0;

  const text = writtenText(event.tool_name, input);
  const r = scan(text, { ignore });
  if (!r.hits.length) return 0;

  const lines = r.hits.slice(0, MAX_LISTED).map((h) => `- "${h.match.trim()}" [${h.id}] → ${h.fix}`);
  if (r.hits.length > MAX_LISTED) lines.push(`- ...and ${r.hits.length - MAX_LISTED} more`);
  process.stderr.write(
    `no-slop: ${rel} has ${r.hits.length} AI-writing tell(s) in what you just wrote ` +
    `(grade ${r.grade}, ${r.per100} per 100 words).\n${lines.join('\n')}\n` +
    `Rewrite those passages in plain, specific language, then carry on with the task. ` +
    `Keep a flagged phrase only if it is quoted text, a name, or a technical term; to silence a tell for this project, add its id to .slopignore.\n`
  );
  return 2;
}

process.exitCode = main();
