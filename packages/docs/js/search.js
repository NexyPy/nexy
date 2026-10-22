/**
 * Nexy docs - fuzzy search.
 *
 * Tolerant to typos: "roate" still finds "route" (Damerau–Levenshtein distance <= 2)
 * plus prefix/contains scoring and bigram similarity. Suggests "did you mean" chips.
 *
 * Exposes: window.NexySearch.query(q, locale) -> { results, dym }
 */
(function () {
  "use strict";

  const MAX_DIST = 2;

  function damerau(a, b) {
    const m = a.length, n = b.length;
    if (m === 0) return n;
    if (n === 0) return m;
    const d = Array.from({ length: m + 1 }, () => new Array(n + 1));
    for (let i = 0; i <= m; i++) d[i][0] = i;
    for (let j = 0; j <= n; j++) d[0][j] = j;
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost);
        if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
          d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + cost);
        }
      }
    }
    return d[m][n];
  }

  function bigrams(s) {
    const out = new Set();
    for (let i = 0; i < s.length - 1; i++) out.add(s.slice(i, i + 2));
    return out;
  }

  function bigramSimilarity(a, b) {
    if (!a || !b) return 0;
    const A = bigrams(a), B = bigrams(b);
    let inter = 0;
    for (const g of A) if (B.has(g)) inter++;
    const union = A.size + B.size - inter;
    return union === 0 ? 0 : inter / union;
  }

  function tokenize(text) {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9à-ÿæœéèêëïîôûüç]+/g, " ")
      .split(" ")
      .filter((t) => t.length > 1);
  }

  function buildLocale(locale) {
    const entries = (window.NEXY_SEARCH_INDEX || {})[locale] || [];
    return entries.map((e) => ({
      u: e.u,
      title: e.t,
      section: e.s,
      titleTokens: tokenize(e.t),
      kwTokens: (e.k || []).flatMap((k) => tokenize(k)),
      sectionTokens: tokenize(e.s),
      bodyTokens: tokenize(e.b),
      body: e.b,
    }));
  }

  /** Tokens that appear in titles or keywords - used to filter "did you mean" suggestions. */
  function buildProminentTokens(entries) {
    const set = new Set();
    for (const e of entries) {
      for (const tok of e.titleTokens) set.add(tok);
      for (const tok of e.kwTokens) set.add(tok);
    }
    return set;
  }

  function allowedDist(word) {
    return word.length < 5 ? 1 : MAX_DIST;
  }

  function matchToken(queryTok, entry) {
    // returns { score, dist } or null
    let best = null;
    const check = (tok, weight) => {
      if (!tok) return;
      const q = queryTok;
      if (tok === q) {
        if (!best || 10 * weight > best.score) best = { score: 10 * weight, dist: 0, tok };
        return;
      }
      if (tok.startsWith(q)) {
        const s = 8 * weight;
        if (!best || s > best.score) best = { score: s, dist: 0, tok };
        return;
      }
      if (tok.includes(q)) {
        const s = 6 * weight;
        if (!best || s > best.score) best = { score: s, dist: 0, tok };
        return;
      }
      const d = damerau(q, tok);
      if (d <= allowedDist(q)) {
        const s = (5 - d) * weight;
        if (!best || s > best.score) best = { score: s, dist: d, tok };
        return;
      }
      // bigram similarity as a fallback boost for longer words
      if (q.length >= 4) {
        const bs = bigramSimilarity(q, tok);
        if (bs >= 0.5) {
          const s = Math.round(bs * 4 * weight);
          if (!best || s > best.score) best = { score: s, dist: 1, tok };
        }
      }
    };
    entry.titleTokens.forEach((tok) => check(tok, 3));
    entry.kwTokens.forEach((tok) => check(tok, 2));
    entry.sectionTokens.forEach((tok) => check(tok, 2));
    entry.bodyTokens.forEach((tok) => check(tok, 1));
    return best;
  }

  function makeSnippet(entry, q) {
    const idx = entry.body.toLowerCase().indexOf(q);
    if (idx < 0) return "";
    const start = Math.max(0, idx - 60);
    const end = Math.min(entry.body.length, idx + q.length + 80);
    let snip = entry.body.slice(start, end).replace(/\s+/g, " ").trim();
    if (start > 0) snip = "…" + snip;
    if (end < entry.body.length) snip += "…";
    const i = snip.toLowerCase().indexOf(q);
    if (i >= 0) snip = snip.slice(0, i) + "<mark>" + snip.slice(i, i + q.length) + "</mark>" + snip.slice(i + q.length);
    return snip;
  }

  const INDEX = { en: null, fr: null };
  const PROMINENT = { en: null, fr: null };

  function query(raw, locale) {
    if (!INDEX[locale]) {
      INDEX[locale] = buildLocale(locale);
      PROMINENT[locale] = buildProminentTokens(INDEX[locale]);
    }
    const entries = INDEX[locale];
    const prominent = PROMINENT[locale];
    const q = raw.trim().toLowerCase();
    if (!q) return { results: [], dym: [] };

    const tokens = tokenize(q);
    const phrase = q;
    const scored = [];
    const corrections = new Map(); // qToken -> {tok, dist, freq}

    for (const entry of entries) {
      let score = 0;
      let matched = 0;
      for (const tok of tokens) {
        const m = matchToken(tok, entry);
        if (m) {
          score += m.score;
          matched++;
          if (m.dist > 0) {
            const cur = corrections.get(tok);
            if (!cur || m.dist < cur.dist) corrections.set(tok, { tok: m.tok, dist: m.dist, freq: 1 });
            else if (m.tok === cur.tok) cur.freq++;
          }
        }
      }
      if (matched === 0) continue;
      // phrase bonus
      const inTitle = entry.title.toLowerCase();
      const inBody = entry.body.toLowerCase();
      if (inTitle.includes(phrase)) score += 12;
      else if (inBody.includes(phrase)) score += 6;
      score += matched; // prefer entries where every token matched something
      scored.push({ entry, score, matched });
    }

    scored.sort((a, b) => b.score - a.score || b.matched - a.matched);

    const results = scored.slice(0, 10).map(({ entry }) => ({
      href: entry.u,
      title: entry.title,
      section: entry.section,
      snippet: makeSnippet(entry, tokens[0]),
    }));

    const dym = [...corrections.values()]
      .filter((c) => c.tok !== tokens[0] && prominent.has(c.tok))
      .sort((a, b) => a.dist - b.dist)
      .slice(0, 3)
      .map((c) => c.tok);

    return { results, dym };
  }

  window.NexySearch = { query };
})();
