/**
 * Threaded Pantry — the ingredient-reuse braid, as plain SVG.
 *
 * Draws one strand per ingredient across the days of a plan:
 *   - the strand opens on the first day the ingredient is cooked and ends on the last;
 *   - a hollow knot marks every day it is actually cooked;
 *   - an amber tail + bead marks what is left over (bead radius = how much);
 *   - dashed strands are ingredients that were already at home.
 *
 * No dependencies. Usage:
 *   renderBraid(document.getElementById('reuse-map'), strands, { days: 5, labels: true, dayCosts: [7.12, 6.98, 7.60, 8.44, 6.66] });
 *
 * strand = { name, uses: [0, 2, 4], weight: 0..1, leftover: 0..1, home: bool }
 *   uses     days (0-based) on which the ingredient is cooked
 *   weight   share of the basket (drives stroke width)
 *   leftover fraction of the bought package left at the end (0 = used up)
 *   home     true if it was already in the pantry (not bought)
 *
 * All colours come from CSS variables so light/dark mode just works:
 *   --green, --amber, --paper, --ink, --muted   (fallbacks below)
 */
(function (global) {
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const MONO = 'ui-monospace, "IBM Plex Mono", Menlo, monospace';
  const SANS = 'inherit';

  function el(tag, attrs, text) {
    const n = document.createElementNS(SVG_NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    return n;
  }
  const r1 = (v) => Math.round(v * 10) / 10;

  function renderBraid(container, strands, opts = {}) {
    const D = opts.days || 5;
    const labels = !!opts.labels;
    const W = opts.width || (labels ? 760 : 760);
    const H = opts.height || (labels ? 40 + strands.length * 34 + 120 : 320);
    const dayCosts = opts.dayCosts || null;
    const dayWord = opts.dayWord || 'DAY';
    const costWord = opts.costWord || 'COST OF WHAT IS OPENED EACH DAY';
    const scale = opts.scale || 1;
    const fmt = opts.formatMoney || ((v) => v.toFixed(2));

    const MX = labels ? 150 : 40, MR = 60, MT = 22;
    let MB = 46 + (dayCosts ? 74 : 0);
    const top = MT, bottom = H - MB, usable = bottom - top;
    const green = 'var(--green, #1e5a3a)', amber = 'var(--amber, #b8791a)',
          paper = 'var(--paper, #f4eddf)', ink = 'var(--ink, #1f1c16)', muted = 'var(--muted, #5f594e)';

    // normalise strands
    const S = strands.map((s, i) => {
      const uses = [...new Set(s.uses)].sort((a, b) => a - b);
      return { ...s, id: i, uses, open: uses[0], last: uses[uses.length - 1] };
    });
    if (!labels) S.sort((a, b) => a.open - b.open || b.weight - a.weight);
    S.forEach((s, i) => (s.id = i));

    const dayX = (d) => MX + (W - MX - MR) * (D === 1 ? 0.5 : d / (D - 1));

    // lanes: fixed rows when labelled, weighted braid otherwise
    const lanes = [];
    for (let d = 0; d < D; d++) {
      const m = {};
      if (labels) {
        const rowH = usable / Math.max(S.length, 1);
        S.forEach((s, i) => (m[s.id] = top + (i + 0.5) * rowH));
      } else {
        const alive = S.filter((s) => s.open <= d && d <= s.last);
        const tw = alive.reduce((a, s) => a + s.weight, 0) || 1;
        let y = top;
        alive.forEach((s) => {
          const h = usable * (0.35 / Math.max(alive.length, 1) + 0.65 * s.weight / tw);
          m[s.id] = y + h / 2; y += h;
        });
        const shift = (usable - (y - top)) / 2;
        for (const k in m) m[k] += shift;
      }
      lanes.push(m);
    }
    const sw = (s) => {
      const base = (2.2 + Math.pow(s.weight, 1.2) * 13) * scale;
      return labels ? Math.min(base, (usable / Math.max(S.length, 1)) * 0.55) : base;
    };

    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img', 'aria-label': opts.ariaLabel || 'Ingredient reuse map' });
    svg.style.display = 'block'; svg.style.width = '100%'; svg.style.height = 'auto';

    // day rules + labels
    for (let d = 0; d < D; d++) {
      const x = r1(dayX(d));
      svg.appendChild(el('line', { x1: x, y1: top - 10, x2: x, y2: bottom + 10, stroke: green, 'stroke-opacity': 0.35, 'stroke-width': 1, 'stroke-dasharray': '1 7', 'stroke-linecap': 'round' }));
      svg.appendChild(el('text', { x, y: bottom + 30, 'text-anchor': 'middle', 'font-family': MONO, 'font-size': 11, 'letter-spacing': 1, fill: green, 'fill-opacity': 0.8 }, `${dayWord} ${d + 1}`));
    }

    for (const s of S) {
      const pts = [];
      for (let d = s.open; d <= s.last; d++) pts.push([dayX(d), lanes[d][s.id]]);
      const w = sw(s), op = 0.72 + s.weight * 0.26;

      if (s.home && !labels) {
        svg.appendChild(el('line', { x1: 12, y1: r1(pts[0][1]), x2: r1(pts[0][0] - 8), y2: r1(pts[0][1]), stroke: green, 'stroke-opacity': 0.45, 'stroke-width': r1(Math.max(1.5, w * 0.5)), 'stroke-dasharray': '7 7', 'stroke-linecap': 'round' }));
      }
      if (pts.length > 1) {
        let d = `M ${r1(pts[0][0])} ${r1(pts[0][1])}`;
        for (let i = 0; i < pts.length - 1; i++) {
          const [ax, ay] = pts[i], [bx, by] = pts[i + 1], dx = (bx - ax) * 0.42;
          d += ` C ${r1(ax + dx)} ${r1(ay)}, ${r1(bx - dx)} ${r1(by)}, ${r1(bx)} ${r1(by)}`;
        }
        const attrs = { d, fill: 'none', stroke: green, 'stroke-opacity': op.toFixed(2), 'stroke-width': r1(w), 'stroke-linecap': 'round' };
        if (s.home && labels) attrs['stroke-dasharray'] = '7 7';
        svg.appendChild(el('path', attrs));
      }
      const [ex, ey] = pts[pts.length - 1];
      if (s.leftover > 0) {
        const ln = 24 + s.leftover * 46, dr = 12 + s.leftover * 30;
        svg.appendChild(el('path', { d: `M ${r1(ex)} ${r1(ey)} C ${r1(ex + ln * 0.55)} ${r1(ey)}, ${r1(ex + ln * 0.7)} ${r1(ey + dr * 0.7)}, ${r1(ex + ln)} ${r1(ey + dr)}`, fill: 'none', stroke: amber, 'stroke-opacity': 0.9, 'stroke-width': r1(Math.max(1.6, w * 0.45)), 'stroke-linecap': 'round' }));
        svg.appendChild(el('circle', { cx: r1(ex + ln), cy: r1(ey + dr), r: r1((2.5 + s.leftover * 8) * scale), fill: amber }));
      } else if (!s.home) {
        svg.appendChild(el('circle', { cx: r1(ex), cy: r1(ey), r: r1(w * 0.55), fill: green, 'fill-opacity': op.toFixed(2) }));
      }
      for (const d of s.uses) {
        svg.appendChild(el('circle', { cx: r1(dayX(d)), cy: r1(lanes[d][s.id]), r: r1(Math.max(3, w * 0.48)), fill: paper, stroke: green, 'stroke-opacity': op.toFixed(2), 'stroke-width': r1(Math.max(1.5, w * 0.28)) }));
      }
      if (labels) {
        svg.appendChild(el('text', { x: MX - 14, y: r1(lanes[0][s.id] + 4), 'text-anchor': 'end', 'font-family': SANS, 'font-size': 13, fill: ink }, s.name));
      }
    }

    if (dayCosts) {
      const mx = Math.max(...dayCosts), bh = 44, by = H - 22;
      dayCosts.forEach((c, d) => {
        const x = dayX(d), h = bh * c / mx;
        svg.appendChild(el('rect', { x: r1(x - 16), y: r1(by - h), width: 32, height: r1(h), rx: 3, fill: green, 'fill-opacity': 0.85 }));
        svg.appendChild(el('text', { x: r1(x), y: r1(by - h - 6), 'text-anchor': 'middle', 'font-family': MONO, 'font-size': 11, fill: ink }, fmt(c)));
      });
      svg.appendChild(el('text', { x: labels ? MX : 40, y: by + 14, 'font-family': MONO, 'font-size': 10, 'letter-spacing': 1, fill: muted }, costWord));
    }

    container.replaceChildren(svg);
    return svg;
  }

  /** Seeded random strands for the empty-state hero (mulberry32). */
  function randomStrands(seed, n = 14, D = 5, reuse = 0.65, leftover = 0.55, pantry = 0.15) {
    let a = seed >>> 0;
    const rnd = () => { a += 0x6D2B79F5; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    const out = [];
    for (let i = 0; i < n; i++) {
      const weight = 0.22 + Math.pow(rnd(), 1.5) * 0.78;
      const home = rnd() < pantry;
      const open = home ? 0 : Math.floor(Math.pow(rnd(), 1.3) * D);
      const maxSpan = D - open;
      let span = 1 + Math.floor(Math.pow(rnd(), 1.7 - reuse * 1.3) * maxSpan);
      if (home) span = Math.max(span, Math.min(D, 2 + Math.floor(rnd() * D)));
      span = Math.min(span, maxSpan);
      const last = open + span - 1;
      const uses = [open, last];
      for (let d = open + 1; d < last; d++) if (rnd() < reuse * 0.8) uses.push(d);
      const lo = rnd() < leftover ? 0.12 + rnd() * 0.6 : 0;
      out.push({ name: '', uses, weight, leftover: home ? lo * 0.5 : lo, home });
    }
    return out;
  }

  /**
   * Build strands from a computed plan. Expects the shape produced by the maths layer:
   *   plan.days[d].meals[].ingredients[] = { name, ... }
   *   plan.shopping[] = { name, needed, bought, leftover, price, atHome }   (leftover/bought as numbers in the same unit)
   *   plan.total = number
   */
  function strandsFromPlan(plan) {
    const byName = new Map();
    plan.days.forEach((day, d) => {
      day.meals.forEach((meal) => (meal.ingredients || []).forEach((ing) => {
        const key = ing.name.toLowerCase();
        if (!byName.has(key)) byName.set(key, { name: ing.name, uses: new Set(), weight: 0, leftover: 0, home: false });
        byName.get(key).uses.add(d);
      }));
    });
    for (const item of plan.shopping || []) {
      const s = byName.get(item.name.toLowerCase());
      if (!s) continue;
      s.home = !!item.atHome;
      s.weight = plan.total ? Math.min(1, 0.2 + (item.price / plan.total) * 4) : 0.5;
      s.leftover = item.bought ? Math.max(0, Math.min(1, item.leftover / item.bought)) : 0;
    }
    return [...byName.values()].map((s) => ({ ...s, uses: [...s.uses] }));
  }

  global.ThreadedPantry = { renderBraid, randomStrands, strandsFromPlan };
})(window);
