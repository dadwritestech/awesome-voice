// slop.js: find AI-writing tells in prose. Zero dependencies; runs in Node and in browsers.
// The tells and grade thresholds live in tells.json, measured in evidence/EVIDENCE.md.
// slop.py is the Python twin; tests/test_parity.py checks that both give the same hits.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./tells.json'));
  else root.Slop = factory(root.SLOP_TELLS);
})(typeof self !== 'undefined' ? self : this, function (DATA) {
  'use strict';

  const RULES = DATA.tells.map((t) => ({ ...t, rx: new RegExp(t.pattern, 'gu' + t.flags) }));

  // Replace code, HTML, URLs and image links with spaces of the same length, so
  // offsets still point into the original text (the web page highlights by offset).
  function mask(text) {
    const blank = (m) => m.replace(/[^\n]/g, ' ');
    return text
      .replace(/```[\s\S]*?```/g, blank)
      .replace(/`[^`\n]*`/g, blank)
      // After code, so a marker quoted in backticks doesn't switch checking off.
      .replace(/<!--\s*no-slop off\s*-->[\s\S]*?(?:<!--\s*no-slop on\s*-->|$)/g, blank)
      .replace(/<[^>\n]+>/g, blank)
      .replace(/!\[[^\]\n]*\]\([^)\n]*\)/g, blank)
      .replace(/https?:\/\/\S+/g, blank)
      .replace(/’/g, "'");
  }

  function countWords(text) {
    return (text.match(/[A-Za-z0-9][A-Za-z0-9'_-]*/g) || []).length;
  }

  function lineOf(text, index) {
    let n = 1;
    for (let i = 0; i < index; i++) if (text.charCodeAt(i) === 10) n++;
    return n;
  }

  function grade(per100) {
    for (const [letter, max] of DATA.grades) if (per100 <= max) return letter;
    return 'F';
  }

  // scan(text, {ignore: ['em-dash']}) -> {words, hits, per100, grade}
  function scan(text, opts = {}) {
    const ignore = new Set(opts.ignore || []);
    const prose = mask(String(text));
    const hits = [];
    for (const r of RULES) {
      if (ignore.has(r.id)) continue;
      r.rx.lastIndex = 0;
      let m;
      while ((m = r.rx.exec(prose))) {
        if (m[0] === '') { r.rx.lastIndex++; continue; }
        hits.push({ id: r.id, kind: r.kind, tier: r.tier, start: m.index, end: m.index + m[0].length,
          match: text.slice(m.index, m.index + m[0].length), line: lineOf(prose, m.index), fix: r.fix });
      }
    }
    hits.sort((a, b) => a.start - b.start || a.id.localeCompare(b.id));
    const words = countWords(prose);
    const per100 = words ? (100 * hits.length) / words : 0;
    return { words, hits, per100: Math.round(per100 * 100) / 100, grade: grade(per100) };
  }

  return { scan, mask, grade, tells: DATA.tells, grades: DATA.grades, version: DATA.version };
});
