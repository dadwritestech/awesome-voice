// node --test tests/
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const HOOK = path.join(__dirname, '..', 'plugin', 'slop', 'hook.js');
const SLOPPY = "We're thrilled to announce a seamless, robust release — whether you're new or not!";

function run(event, env = {}) {
  const r = spawnSync(process.execPath, [HOOK], {
    input: JSON.stringify(event), encoding: 'utf8', env: { ...process.env, NO_SLOP: '', ...env },
  });
  return { code: r.status, err: r.stderr };
}

function tmp() { return fs.mkdtempSync(path.join(os.tmpdir(), 'noslop-')); }

test('Write of a sloppy Markdown file exits 2 and lists the tells', () => {
  const cwd = tmp();
  const r = run({ tool_name: 'Write', cwd, tool_input: { file_path: path.join(cwd, 'README.md'), content: SLOPPY } });
  assert.strictEqual(r.code, 2);
  assert.match(r.err, /\[seamless\]/);
  assert.match(r.err, /\[em-dash\]/);
  assert.match(r.err, /README\.md/);
});

test('clean prose passes', () => {
  const cwd = tmp();
  const r = run({ tool_name: 'Write', cwd, tool_input: { file_path: path.join(cwd, 'README.md'), content: 'dupefind finds duplicate files and reports the space you would get back.' } });
  assert.strictEqual(r.code, 0);
  assert.strictEqual(r.err, '');
});

test('code files are never checked', () => {
  const cwd = tmp();
  const r = run({ tool_name: 'Write', cwd, tool_input: { file_path: path.join(cwd, 'app.js'), content: SLOPPY } });
  assert.strictEqual(r.code, 0);
});

test('Edit checks only new_string; MultiEdit checks every edit', () => {
  const cwd = tmp();
  const f = path.join(cwd, 'docs', 'guide.md');
  assert.strictEqual(run({ tool_name: 'Edit', cwd, tool_input: { file_path: f, old_string: SLOPPY, new_string: 'Plain text.' } }).code, 0);
  const m = run({ tool_name: 'MultiEdit', cwd, tool_input: { file_path: f, edits: [{ new_string: 'fine' }, { new_string: 'a seamless flow' }] } });
  assert.strictEqual(m.code, 2);
  assert.match(m.err, /\[seamless\]/);
});

test('NO_SLOP=off and node_modules skip the check', () => {
  const cwd = tmp();
  const ev = { tool_name: 'Write', cwd, tool_input: { file_path: path.join(cwd, 'README.md'), content: SLOPPY } };
  assert.strictEqual(run(ev, { NO_SLOP: 'off' }).code, 0);
  ev.tool_input.file_path = path.join(cwd, 'node_modules', 'x', 'README.md');
  assert.strictEqual(run(ev).code, 0);
});

test('.slopignore silences tell ids and path prefixes', () => {
  const cwd = tmp();
  fs.writeFileSync(path.join(cwd, '.slopignore'), 'seamless  # we sell seamless gutters\nlegal/\n');
  const only = run({ tool_name: 'Write', cwd, tool_input: { file_path: path.join(cwd, 'a.md'), content: 'A seamless gutter.' } });
  assert.strictEqual(only.code, 0);
  const legal = run({ tool_name: 'Write', cwd, tool_input: { file_path: path.join(cwd, 'legal', 'terms.md'), content: SLOPPY } });
  assert.strictEqual(legal.code, 0);
});

test('bad stdin never blocks the agent', () => {
  const r = spawnSync(process.execPath, [HOOK], { input: 'not json', encoding: 'utf8' });
  assert.strictEqual(r.status, 0);
});
