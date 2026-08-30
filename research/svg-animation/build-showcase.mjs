#!/usr/bin/env node
// build-showcase.mjs — generates showcase.html from the versioned prototypes.
//
// The published showcase must be a VIEW of what is in this repository, never a second
// implementation. It is therefore generated: `scenes/scenes.js` is read from disk and inlined
// verbatim, and the measured numbers are read from the same table the report cites. If the page
// and this directory ever disagree, the page was not rebuilt — the repository is the source.
//
// Usage: node build-showcase.mjs   ->  writes showcase.html

import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const read = (p) => readFileSync(resolve(HERE, p), 'utf8')

const scenesSource = read('scenes/scenes.js')

// The headline comparison, quoted from measurements.md. Kept here as data so the page renders it
// as a table rather than an image of one.
const layoutTable = [
  ['<code>cx</code> attribute, by JS', '60.2', false],
  ['<code>transform</code>, by JS', '60.2', false],
  ['<code>transform</code>, CSS keyframes on <code>&lt;circle&gt;</code>', '37.0', false],
  ['<code>transform</code>, by SMIL', '60.2', false],
  ['<code>transform</code>, by Web Animations API', '37.0', false],
  ['<code>transform</code>, same CSS on <code>&lt;div&gt;</code>', '0', true],
]

const comparisons = [
  {
    question: 'Where does a moving layer belong?',
    a: { label: '<code>&lt;g&gt;</code> layers inside one SVG', value: '37.4', unit: 'layout/s' },
    b: { label: 'sibling <code>&lt;svg&gt;</code> elements', value: '0', unit: 'layout/s', win: true },
    verdict: 'Promote anything that moves as a unit to its own <code>&lt;svg&gt;</code>. Same picture, free channel.',
  },
  {
    question: 'Does <code>&lt;use&gt;</code> make a scene lighter?',
    a: { label: '1500 full <code>&lt;path&gt;</code> nodes', value: '1513', unit: 'layout objects', win: true },
    b: { label: '1500 <code>&lt;use&gt;</code> of one symbol', value: '3012', unit: 'layout objects' },
    verdict: 'No — each <code>&lt;use&gt;</code> instantiates a shadow subtree. Use it for file size and authoring, not speed.',
  },
  {
    question: 'When do particles have to leave SVG?',
    a: { label: '2000 particles as SVG circles', value: '466', unit: 'ms/s main thread' },
    b: { label: 'the same 2000 on a canvas', value: '125', unit: 'ms/s main thread', win: true },
    verdict: '3.7×, and the SVG version was the only prototype that dropped below 60 composited fps.',
  },
  {
    question: 'What does it cost to add motion to a screen that already works?',
    a: { label: 'the added layers, written the obvious way', value: '37', unit: 'layout/s' },
    b: { label: 'the same layers, each mark promoted to its own element', value: '0', unit: 'layout/s', win: true },
    verdict: 'Same picture, same motion. Promoting the container is not enough — the animation has to land on the box, not on a shape inside it. Adding motion at all took the screen from 3.1 to 13.0 ms/s of main thread, with no layout.',
  },
  {
    question: 'Rebuild the wave, or translate a tile?',
    a: { label: 'rebuild <code>d</code> every frame', value: '17.9', unit: 'ms/s' },
    b: { label: 'seamless tile, translated', value: '7.1', unit: 'ms/s', win: true },
    verdict: 'The tile is 2.5× cheaper and off the layout path. It buys that with a period; the rebuild never repeats.',
  },
]

const page = `<title>SVG Motion Field Guide</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
  /* Light is the complete palette; the two blocks after it redefine tokens only, so the page
     resolves correctly in all three viewer states (stamped light, stamped dark, unstamped). */
  :root {
    --ink:        #10151d;
    --ground:     #f4f6f9;
    --surface:    #ffffff;
    --line:       #dbe1ea;
    --text:       #1b2430;
    --muted:      #5c6b80;
    --accent:     #a2662a;
    --good:       #2e7d5b;
    --warn:       #b04a2f;
    --plate-edge: #c9d2de;

    --serif: "Newsreader", ui-serif, Georgia, serif;
    --sans:  "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
    --mono:  "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;

    --measure: 68ch;
    --plate:   1080px;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --ink:        #e6ecf6;
      --ground:     #0b0f17;
      --surface:    #141a26;
      --line:       #232d3d;
      --text:       #dde5f2;
      --muted:      #8494ac;
      --accent:     #e0a758;
      --good:       #6fcf97;
      --warn:       #e07a5f;
      --plate-edge: #232d3d;
    }
  }
  :root[data-theme="dark"] {
    --ink:        #e6ecf6;
    --ground:     #0b0f17;
    --surface:    #141a26;
    --line:       #232d3d;
    --text:       #dde5f2;
    --muted:      #8494ac;
    --accent:     #e0a758;
    --good:       #6fcf97;
    --warn:       #e07a5f;
    --plate-edge: #232d3d;
  }

  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--ground);
    color: var(--text);
    font-family: var(--sans);
    font-size: 16px;
    line-height: 1.62;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: var(--plate); margin: 0 auto; padding: 0 24px; }
  .prose { max-width: var(--measure); }

  h1, h2, h3 { font-family: var(--serif); font-weight: 600; text-wrap: balance; margin: 0; }
  h1 { font-size: clamp(2.1rem, 4.6vw, 3.3rem); line-height: 1.06; letter-spacing: -0.02em; }
  h2 { font-size: clamp(1.5rem, 2.6vw, 2rem); line-height: 1.14; letter-spacing: -0.012em; }
  h3 { font-size: 1.16rem; line-height: 1.3; }
  p { margin: 0; }
  a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }
  code { font-family: var(--mono); font-size: 0.88em; }
  strong { font-weight: 600; color: var(--ink); }

  .eyebrow {
    font-family: var(--mono); font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 0.14em; color: var(--muted);
  }

  /* ── masthead ───────────────────────────────────────────── */
  header.masthead { padding: 72px 0 40px; border-bottom: 1px solid var(--line); }
  .masthead .lede {
    font-family: var(--serif); font-size: 1.32rem; line-height: 1.5; color: var(--muted);
    margin-top: 18px; max-width: 54ch;
  }
  .masthead .lede em { font-style: italic; color: var(--ink); }
  .method {
    display: flex; flex-wrap: wrap; gap: 8px 26px; margin-top: 30px;
    font-family: var(--mono); font-size: 0.78rem; color: var(--muted);
  }
  .method b { color: var(--ink); font-weight: 500; }

  section { padding: 56px 0; border-bottom: 1px solid var(--line); }
  section > .wrap > .eyebrow { display: block; margin-bottom: 10px; }
  .stack { display: flex; flex-direction: column; gap: 18px; }

  /* ── the finding ────────────────────────────────────────── */
  table.finding {
    width: 100%; border-collapse: collapse; margin-top: 26px;
    font-size: 0.94rem;
  }
  table.finding th {
    text-align: left; font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted);
    padding: 0 14px 10px 0; border-bottom: 1px solid var(--line);
  }
  table.finding td {
    padding: 11px 14px 11px 0; border-bottom: 1px solid var(--line);
    vertical-align: baseline;
  }
  table.finding td.num {
    font-family: var(--mono); font-variant-numeric: tabular-nums; text-align: right;
    width: 9ch; color: var(--warn);
  }
  table.finding tr.control td { background: color-mix(in srgb, var(--good) 9%, transparent); }
  table.finding tr.control td.num { color: var(--good); font-weight: 500; }
  table.finding tr.control td:first-child::after {
    content: "control"; font-family: var(--mono); font-size: 0.68rem; color: var(--good);
    text-transform: uppercase; letter-spacing: 0.1em; margin-left: 10px;
  }

  /* ── plates ─────────────────────────────────────────────── */
  .plates { display: flex; flex-direction: column; gap: 52px; }
  figure.plate { margin: 0; }
  .stage {
    aspect-ratio: 16 / 7; width: 100%; border: 1px solid var(--plate-edge);
    border-radius: 3px; overflow: hidden; background: var(--surface);
  }
  figcaption { margin-top: 14px; display: grid; grid-template-columns: 1fr; gap: 10px; }
  @media (min-width: 860px) {
    figcaption { grid-template-columns: 1fr 1.35fr; gap: 34px; }
  }
  .plate-id {
    display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;
  }
  .plate-id h3 { font-family: var(--serif); }
  .recipe {
    font-family: var(--mono); font-size: 0.8rem; color: var(--accent);
    margin-top: 6px; line-height: 1.5;
  }
  .cost {
    font-family: var(--mono); font-size: 0.76rem; color: var(--muted); margin-top: 6px;
  }
  .cost b { color: var(--good); font-weight: 500; }
  .plate-note { color: var(--muted); font-size: 0.95rem; }

  /* ── comparisons ────────────────────────────────────────── */
  .compare { display: flex; flex-direction: column; gap: 28px; margin-top: 28px; }
  .cmp { border-top: 1px solid var(--line); padding-top: 18px; }
  .cmp h3 { font-family: var(--sans); font-size: 1rem; font-weight: 600; }
  .bars { display: grid; gap: 8px; margin: 14px 0 10px; }
  .bar { display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 14px; }
  .bar .label { font-size: 0.9rem; color: var(--muted); }
  .bar .value {
    font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 0.9rem;
    color: var(--warn); white-space: nowrap;
  }
  .bar.win .label { color: var(--text); }
  .bar.win .value { color: var(--good); font-weight: 500; }
  .cmp .verdict { font-size: 0.92rem; color: var(--muted); }

  /* ── motion switch ──────────────────────────────────────── */
  .switch {
    display: inline-flex; align-items: center; gap: 10px; margin-top: 18px;
    font-family: var(--mono); font-size: 0.8rem; color: var(--muted);
    background: var(--surface); border: 1px solid var(--line); border-radius: 3px;
    padding: 9px 14px; cursor: pointer;
  }
  .switch:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .switch .dot {
    width: 9px; height: 9px; border-radius: 50%; background: var(--muted);
  }
  :root[data-motion="reduced"] .switch .dot { background: var(--good); }
  :root[data-motion="reduced"] .switch .state::after { content: "on"; color: var(--good); }
  :root:not([data-motion="reduced"]) .switch .state::after { content: "off"; }

  /* ── bestiary ───────────────────────────────────────────── */
  .creatures { display: flex; flex-direction: column; gap: 1px; background: var(--line);
    border: 1px solid var(--line); border-radius: 3px; overflow: hidden; }
  .creature { background: var(--surface); padding: 16px 18px 14px; }
  .creature .box { height: 190px; }
  .creature .box svg { width: 100%; height: 100%; display: block; }
  .creature .id { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; margin-top: 6px; }
  .creature .id b { font-family: var(--serif); font-size: 1.1rem; font-weight: 600; color: var(--ink); }
  .creature .id i { font-family: var(--serif); font-style: italic; color: var(--muted); font-size: 0.9rem; }
  .creature .mech { font-family: var(--mono); font-size: 0.76rem; color: var(--accent); margin-top: 5px; }
  .creature .view { font-family: var(--mono); font-size: 0.74rem; color: var(--muted); margin-top: 3px; }

  /* ── primitive strip ────────────────────────────────────── */
  .primitives {
    display: grid; gap: 1px; background: var(--line);
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    border: 1px solid var(--line); border-radius: 3px; overflow: hidden;
  }
  .prim { background: var(--surface); padding: 14px 14px 12px; }
  .prim .box {
    height: 62px; color: var(--accent); overflow: hidden; display: block;
  }
  .prim .name {
    font-family: var(--mono); font-size: 0.82rem; color: var(--ink); margin-top: 8px;
  }
  .prim .chan {
    font-family: var(--mono); font-size: 0.68rem; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;
  }

  ul.plain { margin: 0; padding-left: 1.1em; color: var(--muted); }
  ul.plain li { margin-bottom: 8px; }
  ul.plain li strong { color: var(--ink); }

  footer { padding: 48px 0 72px; color: var(--muted); font-size: 0.9rem; }
  footer .prose { display: flex; flex-direction: column; gap: 14px; }

  @media (prefers-reduced-motion: reduce) {
    * { scroll-behavior: auto !important; }
  }

  __SCENE_CSS__
</style>

<header class="masthead">
  <div class="wrap">
    <span class="eyebrow">Measured in Chrome 151 · 19 prototypes · 2026-08-30</span>
    <h1>SVG Motion Field Guide</h1>
    <p class="lede">Eight scenes, each one a composition of a small vocabulary of behaviours — and
      the measurements that decided how every one of them is built. <em>Everything here runs; nothing
      here is a screenshot.</em></p>
    <div class="method">
      <span><b>Browser</b> Chrome for Testing 151.0.7922.34</span>
      <span><b>Mode</b> headless, software raster</span>
      <span><b>Sample</b> 5 s per prototype</span>
    </div>
  </div>
</header>

<section>
  <div class="wrap">
    <span class="eyebrow">The finding everything else follows from</span>
    <div class="prose stack">
      <h2>It is the element type, not the property</h2>
      <p>The advice everywhere is: animate <code>transform</code>, never geometry, because transform
        is composited. For HTML that is true. Imported into SVG it does not hold — and one control
        row is all it takes to see that.</p>
      <p>The same 300 circles, the same motion, five mechanisms, plus the identical CSS run against
        <code>&lt;div&gt;</code>s instead:</p>
    </div>
    <div style="overflow-x:auto">
      <table class="finding">
        <thead><tr><th>What animates</th><th style="text-align:right">Layout / s</th></tr></thead>
        <tbody>__LAYOUT_ROWS__</tbody>
      </table>
    </div>
    <div class="prose stack" style="margin-top:26px">
      <p><strong>Moving an SVG child by <code>transform</code> costs layout every frame. Moving an
        HTML box by the same declaration costs none.</strong> So the rule is not about which property
        you pick — it is about where you put the boundary.</p>
      <p style="color:var(--muted)">Stated precisely: this measures layout, not compositing. It does
        not prove SVG children are never composited; it proves the main thread does layout work for
        them every frame and none for an HTML box doing the same thing.</p>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <span class="eyebrow">Plates</span>
    <div class="prose stack" style="margin-bottom:34px">
      <h2>Eight scenes, one vocabulary</h2>
      <p>No scene below uses a technique the others do not. They differ in how a handful of
        behaviours — drift, sway, orbit, flicker, draw, wave — are combined and layered. Each plate
        names its recipe and what it measured.</p>
      <p>The last two plates are the ones that matter most. <strong>Ferdinand</strong> is not an
        invented subject but a real project — an out-of-band Kubernetes node watchdog named after the
        South Pacific Coastwatchers. It is here because a vocabulary that only produces pretty
        weather has not proved anything. That scene animates a <em>dead man's switch</em>: the alert
        is the post that stops transmitting, so the dramatic beat is an absence.</p>
      <p><strong>Feldt</strong> goes further, and is the more useful of the two, because it starts
        from code that is <em>already right</em>. That project's world screen draws its archipelago
        on a canvas with a camera — and this research says keep it, because a world with pan and zoom
        is exactly where SVG loses. What the doctrine adds sits in layers above the canvas, never
        touching it. Use the switch on that plate to see what is added, and the fifth comparison
        below for what it cost.</p>
      <button class="switch" id="motionSwitch" type="button" aria-pressed="false">
        <span class="dot"></span>
        <span>Simulate <code>prefers-reduced-motion</code> · <span class="state"></span></span>
      </button>
      <p style="font-size:0.9rem;color:var(--muted)">Reduce is not an off switch. Travel, parallax
        and rotation stop; the scenes keep breathing, because deleting motion that carried meaning
        makes an interface worse, not kinder.</p>
    </div>
    <div class="plates" id="plates"></div>
  </div>
</section>

<section>
  <div class="wrap">
    <span class="eyebrow">Bestiary — mechanics, isolated</span>
    <div class="prose stack" style="margin-bottom:28px">
      <h2>The view is chosen by the mechanism</h2>
      <p>Each animal alone and large, because a mechanism cannot be judged at forty pixels inside a
        landscape. And they are here to make one comparison possible.</p>
      <p>A dolphin and a shark both "swim with the tail", and their mechanics are <strong>opposites</strong>.
        Cetaceans descend from land mammals whose spines flex up and down, so their flukes are
        <strong>horizontal</strong> and they oscillate dorsoventrally. Sharks descend from fish whose
        spines flex side to side, so the caudal fin is <strong>vertical</strong> and they undulate
        laterally.</p>
      <p>So the dolphin and the whale are drawn in profile and the shark <strong>from above</strong>.
        Draw them all from the side and the shark's entire stroke happens in the plane you cannot
        see — a lie that costs nothing to make and everything to keep. Choosing the view is part of
        the research, not a styling decision.</p>
    </div>
    <div class="creatures" id="creatures"></div>
  </div>
</section>

<section>
  <div class="wrap">
    <span class="eyebrow">The vocabulary</span>
    <div class="prose stack" style="margin-bottom:30px">
      <h2>Twelve behaviours the scenes are made of</h2>
      <p>Each one running on its own. Watch <code>sway</code> next to <code>oscillate</code> and the
        difference stops being a definition: one pivots about an anchored base, the other slides.</p>
    </div>
    <div class="primitives" id="primitives"></div>
  </div>
</section>

<section>
  <div class="wrap">
    <span class="eyebrow">Four questions, settled by measurement</span>
    <div class="prose"><h2>What the prototypes decided</h2></div>
    <div class="compare" id="compare"></div>
  </div>
</section>

<section>
  <div class="wrap prose stack">
    <span class="eyebrow">The correction that mattered most</span>
    <h2>A technique catalogue is not enough</h2>
    <p>The first version of the birds plate obeyed every performance rule on this page — path
      following, facing rotation, a wing oscillation, per-bird stagger — and it was two mirrored arcs
      turning on one sine at constant span. A <em>symbol</em> of a bird. Told so plainly, and it was
      the right call.</p>
    <p>What fixed it was not a better easing curve. It was reading how a wing works before drawing
      one again:</p>
    <ul class="plain">
      <li>The cycle has <strong>four phases</strong>, not two.</li>
      <li>The <strong>downstroke</strong> is the power stroke — down <em>and forward</em>, fully
        extended.</li>
      <li>The <strong>upstroke</strong> recovers: up, back, and the wing <strong>folds</strong>, so
        the <strong>span changes through the cycle</strong>. That one fact is what separates a bird
        from a paper cutout, and no easing substitutes for it.</li>
      <li>The two halves are <strong>asymmetric in time</strong>, and cruising flight beats
        <strong>shallow</strong>.</li>
    </ul>
    <p>So the wing is now built the way the animal is built: an arm hinged at the shoulder and a
      hand hinged at the elbow, the hand lagging by about an eighth of a cycle. Folding shortens the
      span as a <em>consequence</em> of the anatomy rather than as a second tween pretending to be
      one — and the whip through the wingtip comes free with the lag.</p>
    <p><strong>Research the subject before animating it.</strong> Mechanism, phases, geometry,
      materials, scale relations, and the detail a viewer actually recognises it by. A catalogue of
      primitives applied without that step produces animation that is fast, cheap and wrong.</p>
  </div>
</section>

<section>
  <div class="wrap prose stack">
    <span class="eyebrow">Two traps</span>
    <h2>Found by looking, not by reading</h2>
    <ul class="plain">
      <li><strong>SVG's <code>transform-origin</code> starts at <code>0 0</code>, not the centre.</strong>
        A <code>scale()</code> on a <code>&lt;circle&gt;</code> moves it as well as swelling it — which
        is how the sun's halo ended up offset from the sun in the first render of the solar system.
        Fix with <code>transform-box: fill-box</code>.</li>
      <li><strong>…but <code>fill-box</code> re-resolves coordinates inside a <code>transform</code>
        attribute.</strong> A <code>rotate(30 400 250)</code> written in user space is re-read against
        the element's own box, and every leaf in the tree scene was flung out of the canopy the moment
        that rule was added. Rotate about a point in the scene? <code>view-box</code> and an explicit
        origin instead.</li>
    </ul>
    <p style="color:var(--muted)">Neither appears in the performance advice that dominates search
      results for this subject.</p>
  </div>
</section>

<footer>
  <div class="wrap prose">
    <p>Every number on this page comes from <code>measurements.md</code> in the research directory,
      taken with a dependency-free CDP harness against Chrome for Testing 151.0.7922.34, headless,
      software rasterisation, on one machine.</p>
    <p><strong>What that does not cover:</strong> absolute frame times do not transfer to a device
      with a GPU or to a phone; the relative ordering of two techniques measured in the same run
      does. Nothing here says anything about Firefox or Safari. The measurements are evidence dated
      2026-08-30, not a maintained test suite.</p>
    <p>This page is generated from the same <code>scenes.js</code> the repository holds. If the two
      ever disagree, the repository is right and the page was not rebuilt.</p>
  </div>
</footer>

<script>__SCENES_SOURCE__</script>
<script>
  const { scenes, primitives, creatures, reducedMotionCss } = window.SvgScenes

  const reduced = document.createElement('style')
  reduced.textContent = reducedMotionCss
  document.head.appendChild(reduced)

  // Scene notes discuss markup and contain literal <svg> and <g>; inserted as HTML they would be
  // parsed as tags and swallow the rest of the sentence.
  const escapeHtml = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]))

  const plates = document.getElementById('plates')
  for (const s of scenes) {
    const fig = document.createElement('figure')
    fig.className = 'plate'
    const stage = document.createElement('div')
    stage.className = 'stage'
    fig.appendChild(stage)
    const cap = document.createElement('figcaption')
    cap.innerHTML = \`
      <div>
        <div class="plate-id"><h3>\${escapeHtml(s.title)}</h3></div>
        <div class="recipe">\${escapeHtml(s.recipe)}</div>
        <div class="cost">\${escapeHtml(s.cost)}</div>
      </div>
      <p class="plate-note">\${escapeHtml(s.note)}</p>\`
    fig.appendChild(cap)
    plates.appendChild(fig)
    s.build(stage)
  }

  const bestiary = document.getElementById('creatures')
  for (const c of creatures) {
    const cell = document.createElement('div')
    cell.className = 'creature stage'
    const box = document.createElement('div')
    box.className = 'box'
    cell.appendChild(box)
    cell.insertAdjacentHTML('beforeend',
      \`<div class="id"><b>\${escapeHtml(c.title)}</b><i>\${escapeHtml(c.latin)}</i></div>
       <div class="mech">\${escapeHtml(c.mechanism)}</div>
       <div class="view">view: \${escapeHtml(c.view)}</div>\`)
    bestiary.appendChild(cell)
    c.build(box)
  }

  const strip = document.getElementById('primitives')
  for (const prim of primitives) {
    const cell = document.createElement('div')
    cell.className = 'prim'
    const box = document.createElement('div')
    box.className = 'box stage'
    cell.appendChild(box)
    cell.insertAdjacentHTML('beforeend',
      \`<div class="name">\${prim.id}</div><div class="chan">\${prim.channel}</div>\`)
    strip.appendChild(cell)
    prim.build(box)
  }

  const compare = document.getElementById('compare')
  compare.innerHTML = __COMPARISONS__.map((c) => {
    const bar = (side) => \`
      <div class="bar \${side.win ? 'win' : ''}">
        <span class="label">\${side.label}</span>
        <span class="value">\${side.value} \${side.unit}</span>
      </div>\`
    return \`<div class="cmp">
      <h3>\${c.question}</h3>
      <div class="bars">\${bar(c.a)}\${bar(c.b)}</div>
      <p class="verdict">\${c.verdict}</p>
    </div>\`
  }).join('')

  const button = document.getElementById('motionSwitch')
  button.addEventListener('click', () => {
    const on = document.documentElement.getAttribute('data-motion') === 'reduced'
    document.documentElement.setAttribute('data-motion', on ? 'full' : 'reduced')
    button.setAttribute('aria-pressed', String(!on))
  })
</script>
`

const rows = layoutTable
  .map(([what, value, control]) =>
    `<tr class="${control ? 'control' : ''}"><td>${what}</td><td class="num">${value}</td></tr>`)
  .join('\n          ')

const out = page
  .replace('__SCENE_CSS__', read('scenes/scenes.js').match(/const sceneCss = `([\s\S]*?)`\n/)[1])
  .replace('__LAYOUT_ROWS__', rows)
  .replace('__SCENES_SOURCE__', scenesSource)
  .replace('__COMPARISONS__', JSON.stringify(comparisons))

writeFileSync(resolve(HERE, 'showcase.html'), out)
console.log(`showcase.html written — ${(out.length / 1024).toFixed(1)} kB`)
