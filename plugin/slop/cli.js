#!/usr/bin/env node
// slop: find AI-writing tells in prose files.
//
//   npx no-slop README.md docs/*.md
//   npx no-slop --max-grade B CHANGELOG.md     # exit 1 if any file is worse than B (for CI)
//   cat draft.txt | npx no-slop -
'use strict';
const fs = require('fs');
const { scan, grades } = require('./slop.js');

const ORDER = 'ABCDF';
const args = process.argv.slice(2);
const files = [], ignore = [];
let maxGrade = 'F', json = false;
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--max-grade') maxGrade = String(args[++i] || 'F').toUpperCase();
  else if (a === '--ignore') ignore.push(args[++i]);
  else if (a === '--json') json = true;
  else if (a === '-h' || a === '--help') {
    console.log('usage: no-slop [--max-grade A-F] [--ignore id] [--json] file... (or - for stdin)\n' +
      'Grades are tells per 100 words: ' + grades.map(([g, v]) => `${g} <= ${v}`).join(', ') + ', F above.');
    process.exit(0);
  } else files.push(a);
}
if (!files.length) { console.error('no-slop: give one or more files, or - for stdin'); process.exit(2); }
if (!ORDER.includes(maxGrade)) { console.error('no-slop: --max-grade takes A, B, C, D or F'); process.exit(2); }

let failed = false;
const out = {};
for (const f of files) {
  let text;
  try { text = f === '-' ? fs.readFileSync(0, 'utf8') : fs.readFileSync(f, 'utf8'); }
  catch (e) { console.error(`no-slop: cannot read ${f}: ${e.message}`); process.exitCode = 2; continue; }
  const r = scan(text, { ignore });
  out[f] = r;
  if (ORDER.indexOf(r.grade) > ORDER.indexOf(maxGrade)) failed = true;
  if (json) continue;
  console.log(`${f}: grade ${r.grade} (${r.hits.length} tells in ${r.words} words, ${r.per100.toFixed(2)} per 100)`);
  for (const h of r.hits) console.log(`  line ${h.line}: "${h.match.trim()}" [${h.id}] -> ${h.fix}`);
}
if (json) console.log(JSON.stringify(out, null, 1));
if (failed && !process.exitCode) process.exitCode = 1;
