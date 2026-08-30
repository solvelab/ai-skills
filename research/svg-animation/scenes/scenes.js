// scenes.js — the model scenes, each one a composition of the primitives in ../primitives.md.
//
// This file is the single source for both `index.html` (open it locally, see them all run) and the
// published showcase, which is generated from this file by ../build-showcase.mjs. There is no
// second implementation: if the page and this file ever disagree, the page was not rebuilt.
//
// Every scene follows the rule the measurements produced: anything that moves as a unit is its own
// <svg> element, animated as an HTML box. Layers are never <g> children being transformed, because
// that costs layout every frame (measurements.md, prototypes 07 vs 08).
//
// Deliberately a CLASSIC script, not an ES module: Chrome blocks module imports over file:// as a
// cross-origin request, and these prototypes must run by opening a file with no server. It exports
// through one global instead.

window.SvgScenes = (() => {
const SVG_NAMESPACE = 'http://www.w3.org/2000/svg'

/** Deterministic generator: the same scene every run, so a visual regression is a real change. */
function seeded(seed) {
  let s = seed
  return () => (s = (s * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff
}

/** A layer is an <svg> element absolutely covering the stage — the free-to-move unit. */
function layer(stage, { viewBox = '0 0 1200 640', width = '100%', className = '' } = {}) {
  const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
  svg.setAttribute('viewBox', viewBox)
  svg.setAttribute('preserveAspectRatio', 'xMidYMid slice')
  svg.setAttribute('class', `layer ${className}`)
  svg.style.width = width
  stage.appendChild(svg)
  return svg
}

const el = (parent, name, attributes = {}) => {
  const n = document.createElementNS(SVG_NAMESPACE, name)
  for (const [k, v] of Object.entries(attributes)) n.setAttribute(k, v)
  parent.appendChild(n)
  return n
}

// ─────────────────────────────────────────────────────────────────────────────
const scenes = []
const scene = (def) => { scenes.push(def); return def }

// ── 1. Starfield ────────────────────────────────────────────────────────────
scene({
  id: 'starfield',
  title: 'Night sky',
  recipe: 'scatter + flicker + parallax',
  cost: 'free — 5 layers, 0 layout/s',
  note:
    'Depth is three rates, not three shades. Each depth is its own <svg>, so the drift is on the ' +
    'free channel. The twinkle is a staggered opacity animation with a per-star duration, never a ' +
    'shared one — synchronised twinkling reads as a fault, not a sky.',
  build(stage) {
    stage.style.background = 'linear-gradient(#04060f 0%, #0a1230 60%, #16204a 100%)'
    const rand = seeded(20260830)
    for (let d = 0; d < 4; d++) {
      const svg = layer(stage, { width: '200%' })
      svg.style.animation = `drift ${90 - d * 18}s linear infinite`
      const count = 150 - d * 16
      for (let i = 0; i < count; i++) {
        const r = 0.5 + d * 0.42 + rand() * 0.5
        const star = el(svg, 'circle', {
          cx: rand() * 2400, cy: rand() * 620, r,
          fill: '#e8f0ff', opacity: 0.25 + d * 0.16,
        })
        // Irregular, per-star period: the decorrelation is the whole effect.
        star.style.animation = `twinkle ${2.2 + rand() * 5}s ease-in-out ${-rand() * 6}s infinite`
      }
    }
    // The moon sits still: one anchored element gives the drifting layers something to be measured
    // against, which is what makes the parallax legible.
    const front = layer(stage)
    const moonGlow = el(front, 'circle', { cx: 980, cy: 130, r: 74, fill: 'url(#moonGlow)' })
    moonGlow.style.animation = 'breathe 9s ease-in-out infinite'
    el(front, 'circle', { cx: 980, cy: 130, r: 34, fill: '#f4f1e4' })
    el(front, 'circle', { cx: 996, cy: 121, r: 30, fill: '#0a1230', opacity: 0.92 })
    const defs = el(front, 'defs')
    const g = el(defs, 'radialGradient', { id: 'moonGlow' })
    el(g, 'stop', { offset: '0%', 'stop-color': '#fff8dc', 'stop-opacity': '0.55' })
    el(g, 'stop', { offset: '100%', 'stop-color': '#fff8dc', 'stop-opacity': '0' })
  },
})

// ── 2. Ocean ────────────────────────────────────────────────────────────────
scene({
  id: 'ocean',
  title: 'Ocean',
  recipe: 'wave (seamless tile) + parallax + gradient depth + ripple',
  cost: 'free — 7.12 ms/s, 0 layout/s (prototype 18)',
  note:
    'Each band is a double-width path built from integer harmonics — 3, 7 and 13 cycles across the ' +
    'tile — so translating it by exactly 50% returns to an identical picture and the loop has no ' +
    'seam. Rebuilding the path every frame instead would never repeat, and cost 2.5x more.',
  build(stage) {
    stage.style.background = 'linear-gradient(#0d2b4a 0%, #11406b 45%, #072033 100%)'
    const W = 2400
    for (let d = 0; d < 5; d++) {
      const svg = layer(stage, { viewBox: `0 0 ${W} 640`, width: '200%' })
      svg.setAttribute('preserveAspectRatio', 'none')
      svg.style.animation = `roll ${11 + d * 6}s linear infinite`
      const base = 250 + d * 62
      const amp = 30 - d * 4
      let d2 = `M0 640 L0 ${base}`
      for (let i = 0; i <= 200; i++) {
        const x = (i / 200) * W
        const u = (x / W) * Math.PI * 2
        const y = base
          + Math.sin(u * 3 + d) * amp
          + Math.sin(u * 7 - d * 0.6) * amp * 0.4
          + Math.sin(u * 13 + d * 1.3) * amp * 0.18
        d2 += ` L${x.toFixed(1)} ${y.toFixed(2)}`
      }
      el(svg, 'path', {
        d: `${d2} L${W} 640 Z`,
        fill: `hsl(${203 + d * 3} ${62 - d * 5}% ${14 + d * 8}%)`,
        opacity: 0.62 + d * 0.09,
      })
    }
    // Sun glitter: ripples on the free channel, staggered so they never pulse together.
    const front = layer(stage)
    const rand = seeded(77)
    for (let i = 0; i < 16; i++) {
      const r = el(front, 'ellipse', {
        cx: 400 + rand() * 420, cy: 250 + rand() * 150,
        rx: 10 + rand() * 26, ry: 1.6, fill: '#ffe9b0', opacity: 0.5,
      })
      r.style.animation = `glint ${2 + rand() * 3}s ease-in-out ${-rand() * 4}s infinite`
    }
  },
})

// ── 3. Tree in wind ─────────────────────────────────────────────────────────
scene({
  id: 'tree',
  title: 'Tree in wind',
  recipe: 'sway about each joint + stagger down the hierarchy + noise-driven gusts',
  cost: 'layout — ~40 animated nodes, well inside budget',
  note:
    'A branch bends about its base: the transform is a rotation with transform-origin at the joint, ' +
    'never a translation. Children inherit the parent\'s sway and add their own, so the motion ' +
    'accumulates outward exactly as a real tree does. Gust amplitude comes from summed sines with ' +
    'unrelated periods, so no two gusts land the same way.',
  build(stage) {
    stage.style.background = 'linear-gradient(#dfeaf2 0%, #b9d3e0 60%, #9ab8a4 100%)'
    const svg = layer(stage)
    const rand = seeded(4242)

    // Recursive branch: each level is its own <g> with its own origin, so sway composes.
    function branch(parent, x, y, len, angle, depth) {
      const g = el(parent, 'g')
      // Opt out of the fill-box rule above: a branch rotates about the joint where it meets its
      // parent, which is a point in user space, not the centre of its own bounding box.
      g.style.transformBox = 'view-box'
      g.style.transformOrigin = `${x}px ${y}px`
      // Deeper branches sway further and faster — that gradient is what sells it as one organism.
      const amp = 0.5 + depth * 1.5
      const dur = 5.5 - depth * 0.5
      g.style.animation = `sway${depth} ${dur}s ease-in-out ${-rand() * dur}s infinite alternate`
      g.dataset.amp = amp

      const x2 = x + Math.cos(angle) * len
      const y2 = y + Math.sin(angle) * len
      el(g, 'line', {
        x1: x, y1: y, x2, y2,
        stroke: `hsl(28 ${30 - depth * 3}% ${22 + depth * 5}%)`,
        'stroke-width': Math.max(1.5, 13 - depth * 2.4), 'stroke-linecap': 'round',
      })

      if (depth < 4) {
        branch(g, x2, y2, len * 0.74, angle - 0.44 - rand() * 0.2, depth + 1)
        branch(g, x2, y2, len * 0.72, angle + 0.42 + rand() * 0.2, depth + 1)
        if (depth > 1 && rand() > 0.55) branch(g, x2, y2, len * 0.5, angle + (rand() - 0.5) * 0.5, depth + 1)
      } else {
        for (let i = 0; i < 9; i++) {
          // NOTE: no rotate() with an explicit centre here. The shared rule sets
          // transform-box: fill-box, which re-resolves the coordinates inside a transform
          // attribute against the element's own box — a rotate(deg cx cy) written in user space
          // then throws the leaf across the scene. With fill-box in play, rotate about the
          // element's own centre and let transform-origin do the positioning.
          el(g, 'ellipse', {
            cx: x2 + (rand() - 0.5) * 30, cy: y2 + (rand() - 0.5) * 30,
            rx: 7 + rand() * 5, ry: 4.5 + rand() * 3,
            transform: `rotate(${(rand() * 360).toFixed(0)})`,
            fill: `hsl(${88 + rand() * 34} 42% ${32 + rand() * 18}%)`, opacity: 0.92,
          })
        }
      }
      return g
    }
    branch(svg, 600, 620, 132, -Math.PI / 2, 0)

    // Loose leaves drifting off, on the free channel.
    const air = layer(stage)
    for (let i = 0; i < 9; i++) {
      const leaf = el(air, 'ellipse', {
        cx: 0, cy: 0, rx: 6, ry: 3.4,
        fill: `hsl(${40 + rand() * 30} 55% 45%)`, opacity: 0.85,
      })
      leaf.style.transformOrigin = 'center'
      leaf.style.animation = `leafFall ${7 + rand() * 6}s linear ${-rand() * 12}s infinite`
      leaf.style.setProperty('--x0', `${300 + rand() * 600}px`)
    }
  },
})

// ── 4. Clouds at sunset ─────────────────────────────────────────────────────
scene({
  id: 'clouds',
  title: 'Sunset clouds',
  recipe: 'turbulence generated once + drift at two rates + gradient sky',
  cost: 'raster — 7.44 ms/s, 0 layout/s (prototype 12)',
  note:
    'The noise field is evaluated once and then translated. Animating baseFrequency instead held ' +
    '60 fps at this size when measured, but regenerating a field every frame does not scale and ' +
    'buys nothing here: movement reads the same when you move a finished field.',
  build(stage) {
    stage.style.background =
      'linear-gradient(#1d2a54 0%, #8a4a6a 45%, #d9784f 72%, #f2b06a 100%)'
    const sun = layer(stage)
    const sunEl = el(sun, 'circle', { cx: 620, cy: 430, r: 62, fill: '#ffd79a' })
    sunEl.style.animation = 'breathe 11s ease-in-out infinite'
    for (let i = 0; i < 3; i++) {
      const halo = el(sun, 'circle', {
        cx: 620, cy: 430, r: 62 + i * 46, fill: '#ffb56b', opacity: 0.16 - i * 0.045,
      })
      halo.style.animation = `breathe ${9 + i * 3}s ease-in-out ${-i * 2}s infinite`
    }

    const bands = [
      { seed: 7, freq: '0.003 0.008', dur: 120, opacity: 0.5, tint: '0.98 0.72 0.62' },
      { seed: 19, freq: '0.006 0.013', dur: 70, opacity: 0.72, tint: '1 0.82 0.70' },
    ]
    bands.forEach((b, i) => {
      const svg = layer(stage, { viewBox: '0 0 2400 640', width: '200%' })
      svg.setAttribute('preserveAspectRatio', 'none')
      svg.style.animation = `roll ${b.dur}s linear infinite`
      svg.style.opacity = b.opacity
      const defs = el(svg, 'defs')
      const f = el(defs, 'filter', { id: `cloud${i}`, x: '0', y: '0', width: '100%', height: '100%' })
      el(f, 'feTurbulence', {
        type: 'fractalNoise', baseFrequency: b.freq, numOctaves: 4, seed: b.seed, result: 'n',
      })
      const [r, g, bl] = b.tint.split(' ')
      el(f, 'feColorMatrix', {
        in: 'n', type: 'matrix',
        values: `0 0 0 0 ${r}  0 0 0 0 ${g}  0 0 0 0 ${bl}  0 0 0 -1.25 1.05`,
      })
      el(svg, 'rect', { width: 2400, height: 420, filter: `url(#cloud${i})` })
    })
  },
})

// ── 5. Solar system ─────────────────────────────────────────────────────────
scene({
  id: 'solar',
  title: 'Solar system',
  recipe: 'nested orbit + rotate + scale for depth',
  cost: 'layout — 12 animated groups',
  note:
    'An orbit is a rotating group whose child sits off-centre — not trigonometry recomputed per ' +
    'frame. Nesting gives you moons for free: the moon\'s group rotates inside the planet\'s, so it ' +
    'follows the planet without any code knowing where the planet is.',
  build(stage) {
    stage.style.background = 'radial-gradient(circle at 50% 50%, #12173a 0%, #05070f 70%)'
    const stars = layer(stage)
    const rand = seeded(9001)
    for (let i = 0; i < 130; i++) {
      const s = el(stars, 'circle', {
        cx: rand() * 1200, cy: rand() * 640, r: 0.4 + rand() * 1.1,
        fill: '#dfe8ff', opacity: 0.2 + rand() * 0.5,
      })
      s.style.animation = `twinkle ${3 + rand() * 5}s ease-in-out ${-rand() * 6}s infinite`
    }

    const svg = layer(stage)
    const sun = el(svg, 'circle', { cx: 600, cy: 320, r: 30, fill: '#ffcf5c' })
    sun.style.animation = 'breathe 6s ease-in-out infinite'
    el(svg, 'circle', { cx: 600, cy: 320, r: 52, fill: '#ffcf5c', opacity: 0.14 })

    const planets = [
      { r: 78, size: 5, color: '#b9a48a', period: 8 },
      { r: 116, size: 8, color: '#d9a066', period: 14 },
      { r: 158, size: 9, color: '#5fa8d3', period: 22, moon: true },
      { r: 206, size: 7, color: '#c2603f', period: 34 },
      { r: 268, size: 15, color: '#d8b48a', period: 52, ring: true },
    ]
    for (const p of planets) {
      el(svg, 'circle', {
        cx: 600, cy: 320, r: p.r, fill: 'none',
        stroke: '#8fa6d8', 'stroke-width': 0.5, opacity: 0.18,
      })
      const orbit = el(svg, 'g')
      orbit.style.transformBox = 'view-box'
      orbit.style.transformOrigin = '600px 320px'
      orbit.style.animation = `spin ${p.period}s linear infinite`

      const body = el(orbit, 'g')
      el(body, 'circle', { cx: 600 + p.r, cy: 320, r: p.size, fill: p.color })
      if (p.ring) {
        el(body, 'ellipse', {
          cx: 600 + p.r, cy: 320, rx: p.size * 2.1, ry: p.size * 0.62,
          fill: 'none', stroke: '#e6cfa8', 'stroke-width': 2.4, opacity: 0.75,
          transform: `rotate(-18 ${600 + p.r} 320)`,
        })
      }
      if (p.moon) {
        // Nested orbit: this group spins about the planet, which is itself being carried.
        const moonOrbit = el(body, 'g')
        moonOrbit.style.transformBox = 'view-box'
        moonOrbit.style.transformOrigin = `${600 + p.r}px 320px`
        moonOrbit.style.animation = 'spin 3.2s linear infinite'
        el(moonOrbit, 'circle', { cx: 600 + p.r + 20, cy: 320, r: 2.6, fill: '#e8e8e8' })
      }
    }
  },
})

// ── 6. Birds ────────────────────────────────────────────────────────────────
// Rewritten after the first version was rightly called a symbol of a bird rather than a bird.
// What was wrong with it is worth naming, because it is the default failure: two mirrored arcs
// rotating by the same angle, at constant span, on a single sine. Nothing in that is what a wing
// does.
//
// What a wing actually does, researched before redrawing:
//   - The cycle has FOUR phases, not two: upstroke, upstroke-to-downstroke transition, downstroke,
//     and downstroke-to-upstroke transition.
//   - The DOWNSTROKE is the power stroke. The wing goes down AND FORWARD, fully extended, elbow
//     straight, primaries pointing away from the body.
//   - The UPSTROKE is recovery. The wing goes up AND BACK, and it PARTIALLY FOLDS — elbow bent,
//     primaries drawn in toward the body — which cuts drag.
//   - So the SPAN CHANGES through the cycle. That is the single detail whose absence makes an
//     animated bird read as a paper cutout, and no amount of easing substitutes for it.
//   - The two halves are not symmetric in time: the downstroke is the faster, harder one.
//   - In level cruising flight the beat is SHALLOW. The wing does not swing to vertical.
//
// The implementation follows the anatomy rather than approximating it: each wing is two hinged
// segments — an arm from the shoulder and a hand from the elbow — so folding is a rotation at the
// elbow and the span shortens as a CONSEQUENCE, not as a separate tween pretending to be one.
//
// ── ANCHOR MAP (method phase 1b) — where each part sits, in fractions of body length ──
//   shoulder        0.22 L from the bill, at the TOP OF THE BACK (not at the neck — the first
//                   version put it there and the wings appeared to grow out of the head)
//   elbow / wrist   39% of the half-span out from the shoulder. The hand is ~2x the arm; putting
//                   the fold at the midpoint is the classic error
//   tail root       0.74 L        head 0.10 L skull, 0.090 L bill
//   depth order     far wing · body · tail · head · near wing
//
// ── KINEMATICS (method phase 1c) — how far each joint travels ──
//   Published for a gull in flight: elbow angle ~130 deg, forward sweep ~15 deg.
//   Degrees of freedom in a bird forelimb: shoulder 3, elbow 1, wrist 2 — here reduced to one
//   rotation each, which is the 2D projection of the first axis of each.
//   CHECKED against the built geometry rather than assumed:
//     0%  top of upstroke, most folded  -> interior elbow 133.9 deg   (published: 130)
//     48% bottom of downstroke          -> interior elbow 178.9 deg   (fully extended)
//   Four degrees off a measured value. This wing reached that by trial; with phase 1c filled in
//   first it would have been set directly.
//
//   A caution earned here: the first attempt at this check computed the angle without normalising
//   and reported 196 deg, which would have prompted "fixing" a wing that was already right. A
//   verification step is code too, and wrong verification is worse than none.
scene({
  id: 'birds',
  title: 'Birds',
  recipe: 'follow-path + offset-rotate + two-bone wing (arm + hand) + phase-offset stagger',
  cost: 'layout — 7 birds, 4 hinged segments each',
  note:
    'The first version of this plate was two mirrored arcs rotating on one sine, and it read as a ' +
    'symbol rather than a bird. Redrawn from how a wing works: the downstroke is the power stroke ' +
    'and goes down and forward fully extended; the upstroke recovers, going up and back while the ' +
    'elbow FOLDS. Because the wing is built as two hinged bones, the span shortens on the upstroke ' +
    'as a consequence of the fold rather than as a separate tween. The elbow leads the shoulder by ' +
    'a fraction of the cycle, which is what produces the whip through the wingtip.',
  build(stage) {
    stage.style.background = 'linear-gradient(#b9d6ea 0%, #dbe9f2 48%, #f2e6d4 78%, #f7ddb8 100%)'
    const rand = seeded(31337)
    const svg = layer(stage)

    // Hills, in receding tone and contrast — the far ridge is hazier because air between the
    // viewer and it scatters light. Three layers so the birds have depth to travel through.
    const ridges = [
      { d: 'M0 640 L0 452 Q 190 392 372 444 Q 556 500 754 434 Q 952 366 1200 442 L1200 640 Z', fill: '#a9c2b6', opacity: 0.55 },
      { d: 'M0 640 L0 512 Q 250 462 452 504 Q 690 552 892 496 Q 1058 452 1200 500 L1200 640 Z', fill: '#87a894', opacity: 0.78 },
      { d: 'M0 640 L0 566 Q 300 534 540 570 Q 800 610 1010 566 Q 1120 542 1200 558 L1200 640 Z', fill: '#6a8d78', opacity: 0.95 },
    ]
    for (const r of ridges) el(svg, 'path', r)

    const paths = [
      'M-90 168 C 210 96, 520 236, 800 132 S 1180 62, 1330 140',
      'M-90 268 C 260 198, 470 330, 810 226 S 1150 172, 1330 244',
      'M-90 104 C 300 176, 590 58, 890 156 S 1190 222, 1330 116',
    ]

    // One bird, drawn in PROFILE. The first attempt mixed two viewpoints — mirrored wings, which
    // is the view from below, on a body drawn from the side — and the result read as an aircraft.
    // Profile is also the view that shows the anatomy this scene is about: from below, the fold is
    // foreshortened into nothing.
    //
    // Facing +x. The wing is drawn in its neutral, extended position — swept back from the
    // shoulder, which is where a wing actually sits on a bird: over the back, not at the neck.
    function bird(host, phase, beat) {
      const g = el(host, 'g')

      // Far wing first, so the body occludes its root. Dimmer, because it is on the other side of
      // the body and further from the light — and lagging slightly, because a bird's two wings are
      // never exactly in phase from this angle.
      wing(g, -0.022, '#2b3540', 0.9)

      // Body: deep chest forward, tapering to the tail. A gull in cruise carries its mass ahead of
      // the wing root, which is what makes the silhouette read as flying rather than floating.
      el(g, 'path', {
        d: 'M-13 1.2 C -10 -1.6, -3 -4.4, 4 -4.2 C 9 -4, 12.5 -2.4, 13.5 -0.6 '
         + 'C 12.5 1.6, 8 3.4, 1 3.4 C -5 3.4, -10 2.8, -13 1.2 Z',
        fill: '#39434f',
      })

      // Tail: a short fan, angled down a little. Not a spike — a spike reads as a second beak.
      el(g, 'path', { d: 'M-11.5 0.4 C -15 -0.8, -19.5 -1.6, -22 -0.4 C -19 1.2, -15 2.4, -11.5 2.6 Z', fill: '#39434f' })

      // Head and bill are ONE PIECE, and that is not a shortcut — it is the diagnostic feature.
      // On a gull the apex of the skull sits BEHIND the eye, with a low, swept-back forehead
      // running in a continuous ramp to the bill tip. A pigeon is the exact opposite: high, domed
      // forehead. A round head with a bill stuck on the front is a pigeon, whatever else is right.
      // Proportions from the species, in units of total length L (bill to tail), L ≈ 43.5 here:
      // skull 0.10 L, bill 0.090 L. The previous head was 0.15 L and the bill 0.13 L — both far
      // too big, which is why it read as a cartoon.
      el(g, 'path', {
        d: 'M9.6 -4.1 C 11.6 -5.2, 13.8 -5.1, 15.1 -3.9 '   // low forehead, apex behind the eye
         + 'C 16.2 -3.2, 18.4 -2.9, 20 -2.5 '               // continuous ramp into the bill
         + 'L20.1 -1.9 C 18.2 -1.5, 16 -1.2, 14.6 -1 '
         + 'C 12 -1, 10.2 -2.2, 9.6 -4.1 Z',
        fill: '#39434f',
      })
      el(g, 'path', { d: 'M16.4 -3.2 C 18 -2.9, 19.6 -2.6, 20.4 -2.2 L20.4 -1.8 C 19 -1.6, 17.4 -1.4, 16.2 -1.3 Z', fill: '#e0a33f' })
      el(g, 'circle', { cx: 13.1, cy: -3.3, r: 0.62, fill: '#101820' })

      // Near wing last, over the body.
      wing(g, 0, '#39434f', 1)

      function wing(parent, lag, fill, opacity) {
        // Shoulder sits over the BACK — x just behind the chest, y at the top of the body.
        const shoulder = el(parent, 'g', { opacity })
        shoulder.style.transformBox = 'view-box'
        shoulder.style.transformOrigin = '3px -3px'
        shoulder.style.animation =
          `wingArm ${beat}s cubic-bezier(.34,0,.3,1) ${(phase + lag).toFixed(3)}s infinite`

        // ORDER MATTERS, and it is the anatomy that dictates it: the hand goes in FIRST and the
        // arm is drawn OVER it. On a real wing the secondaries overlap the base of the primaries,
        // and here that overlap is also what closes the joint. Two shapes meeting along an edge
        // open a visible gap the moment their rotations diverge — which is exactly what the first
        // version did, and what a strip of ten frozen frames showed immediately.
        const elbow = el(shoulder, 'g')
        elbow.style.transformBox = 'view-box'
        elbow.style.transformOrigin = '-7.4px -6.8px'
        // The hand leads the arm by a fraction of the cycle. That lag is what makes the tip trail
        // and then whip through, instead of the wing moving as one rigid plank.
        elbow.style.animation =
          `wingHand ${beat}s cubic-bezier(.34,0,.3,1) ${(phase + lag - beat * 0.13).toFixed(3)}s infinite`

        // Hand: the primaries. Its root runs far enough up the arm that the arm always covers it,
        // through the whole range of the elbow. Long, swept, tapering to a point.
        //
        // The fold sits at 39% of the half-span, close to the body — the hand is nearly twice the
        // arm. Putting the fold at the midpoint is the classic error and it is what produces the
        // wrong wing.
        el(elbow, 'path', {
          d: 'M-2.4 -6.6 C -9.5 -9.8, -16.8 -10.7, -22.4 -9.6 '
           + 'C -19.4 -6.8, -12.5 -3.6, -3.6 -1.1 '
           + 'C -3.2 -3, -2.8 -4.9, -2.4 -6.6 Z',
          fill,
        })
        // Black wingtip with white mirrors. This is what makes the eye read "gull" at twenty
        // pixels, and it costs a fill, not geometry.
        el(elbow, 'path', {
          d: 'M-14.5 -9.4 C -17.6 -10.3, -20.4 -10.2, -22.4 -9.6 '
           + 'C -20.6 -8, -18 -6.6, -15.2 -5.4 '
           + 'C -14.8 -6.8, -14.6 -8.2, -14.5 -9.4 Z',
          fill: '#151b23', opacity: opacity * 0.92,
        })
        el(elbow, 'circle', { cx: -20.4, cy: -9.1, r: 0.55, fill: '#e9eef5', opacity: opacity * 0.85 })
        el(elbow, 'circle', { cx: -17.9, cy: -8.4, r: 0.45, fill: '#e9eef5', opacity: opacity * 0.7 })

        // Arm: the secondaries. Broad and blunt, and wide enough at the elbow end to sit over the
        // hand's root in every pose. This is the part that gives a wing its area — drawing it as a
        // line is what made the first version read as a stick.
        el(shoulder, 'path', {
          d: 'M3.6 -2.2 C 1.4 -5.8, -3.4 -8.6, -10.6 -8.4 '
           + 'C -11.4 -5.2, -7.4 -1.8, -1.8 -0.5 '
           + 'C 0.4 -1.1, 2.4 -1.8, 3.6 -2.2 Z',
          fill,
        })


      }

      return g
    }

    for (let i = 0; i < 7; i++) {
      const holder = document.createElement('div')
      holder.className = 'bird'
      holder.style.offsetPath = `path("${paths[i % paths.length]}")`
      holder.style.animation = `fly ${19 + rand() * 11}s linear ${-rand() * 24}s infinite`

      const b = document.createElementNS(SVG_NAMESPACE, 'svg')
      b.setAttribute('viewBox', '-26 -18 56 36')
      b.setAttribute('width', 78)
      b.setAttribute('height', 50)
      const scale = 0.85 + rand() * 0.7
      // Beat rate scales inversely with size, as it does in life: the smaller bird beats faster.
      bird(b, -rand() * 1.2, (0.85 / scale) * (0.54 + rand() * 0.14))
      b.style.transform = `scale(${scale})`
      holder.appendChild(b)
      stage.appendChild(holder)
    }
  },
})

// ── 7. Rain on canvas ───────────────────────────────────────────────────────
scene({
  id: 'rain',
  title: 'Rain',
  recipe: 'swarm on Canvas + SVG for everything with identity',
  cost: 'canvas — 1200 drops; the SVG version of this costs 3.7x the main thread',
  note:
    'This is the scene that proves the boundary. The drops are a field, not objects: nothing needs ' +
    'to style, hit-test or read them, so they belong on a canvas. The window frame behind them is ' +
    'SVG, because it has identity. One scene, both technologies, composed by ordinary stacking.',
  build(stage) {
    stage.style.background = 'linear-gradient(#2b3444 0%, #3d4a5c 60%, #4a5768 100%)'
    const back = layer(stage)
    for (let i = 0; i < 5; i++) {
      el(back, 'rect', {
        x: 90 + i * 210, y: 300 - (i % 3) * 52, width: 150, height: 400,
        rx: 6, fill: '#1d2531', opacity: 0.55,
      })
      for (let w = 0; w < 6; w++) {
        const lit = (i * 7 + w * 3) % 5 < 2
        el(back, 'rect', {
          x: 104 + i * 210 + (w % 2) * 66, y: 320 - (i % 3) * 52 + Math.floor(w / 2) * 78,
          width: 52, height: 60, rx: 2,
          fill: lit ? '#f0d79a' : '#2a3442', opacity: lit ? 0.82 : 0.9,
        })
      }
    }

    const canvas = document.createElement('canvas')
    canvas.className = 'layer canvasLayer'
    canvas.width = 1200
    canvas.height = 640
    stage.appendChild(canvas)
    const ctx = canvas.getContext('2d')
    const rand = seeded(5150)
    const drops = []
    for (let i = 0; i < 1200; i++) {
      drops.push({
        x: rand() * 1200, y: rand() * 640,
        len: 8 + rand() * 20, speed: 420 + rand() * 480, alpha: 0.15 + rand() * 0.4,
      })
    }
    let last = performance.now()
    let running = true
    function frame(now) {
      if (!running) return
      const dt = Math.min((now - last) / 1000, 0.05)
      last = now
      ctx.clearRect(0, 0, 1200, 640)
      ctx.strokeStyle = '#cfe0f5'
      ctx.lineWidth = 1
      for (const d of drops) {
        d.y += d.speed * dt
        d.x -= d.speed * 0.18 * dt
        if (d.y > 650) { d.y = -20; d.x = rand() * 1300 }
        ctx.globalAlpha = d.alpha
        ctx.beginPath()
        ctx.moveTo(d.x, d.y)
        ctx.lineTo(d.x + d.len * 0.18, d.y - d.len)
        ctx.stroke()
      }
      requestAnimationFrame(frame)
    }
    requestAnimationFrame(frame)
    return () => { running = false }
  },
})

// ── 8. Lightning ────────────────────────────────────────────────────────────
scene({
  id: 'lightning',
  title: 'Lightning',
  recipe: 'draw (stroke-dashoffset) + flicker + irregular timing',
  cost: 'layout — one path drawn per strike',
  note:
    'stroke-dasharray and stroke-dashoffset set to the path length make a line draw itself; that ' +
    'is the one effect with no HTML equivalent. The strike is regenerated with a new branching ' +
    'path each time and the interval is random, because a bolt on a fixed timer stops being ' +
    'weather and starts being a metronome.',
  build(stage) {
    stage.style.background = 'linear-gradient(#0a0e1c 0%, #161d33 60%, #232c47 100%)'
    const rand = seeded(1990)
    const svg = layer(stage)
    const flash = document.createElement('div')
    flash.className = 'flash'
    stage.appendChild(flash)

    // Storm cloud: the same generate-once-and-drift pattern as the sunset scene, so the sky is
    // never empty between strikes. Without it the scene reads as broken while it waits.
    const cloud = layer(stage, { viewBox: '0 0 2400 640', width: '200%' })
    cloud.setAttribute('preserveAspectRatio', 'none')
    cloud.style.animation = 'roll 100s linear infinite'
    const cloudDefs = el(cloud, 'defs')
    const cloudFilter = el(cloudDefs, 'filter', { id: 'storm', x: '0', y: '0', width: '100%', height: '100%' })
    el(cloudFilter, 'feTurbulence', {
      type: 'fractalNoise', baseFrequency: '0.005 0.011', numOctaves: 5, seed: 3, result: 'n',
    })
    el(cloudFilter, 'feColorMatrix', {
      in: 'n', type: 'matrix',
      values: '0 0 0 0 0.42  0 0 0 0 0.47  0 0 0 0 0.58  0 0 0 -1.1 0.95',
    })
    el(cloud, 'rect', { width: 2400, height: 330, filter: 'url(#storm)', opacity: 0.85 })

    el(svg, 'path', {
      d: 'M0 640 L0 500 Q 180 430 360 486 Q 560 548 780 470 Q 980 398 1200 468 L1200 640 Z',
      fill: '#0b1120', opacity: 0.9,
    })

    const bolt = el(svg, 'path', {
      fill: 'none', stroke: '#eaf1ff', 'stroke-width': 2.6, 'stroke-linecap': 'round',
      'stroke-linejoin': 'round', filter: 'drop-shadow(0 0 6px #9fc2ff)',
    })

    function makeBolt() {
      let x = 250 + rand() * 700
      let y = -10
      let d = `M${x.toFixed(0)} ${y}`
      const branches = []
      while (y < 430) {
        y += 22 + rand() * 40
        x += (rand() - 0.5) * 90
        d += ` L${x.toFixed(0)} ${y.toFixed(0)}`
        if (rand() > 0.76) {
          let bx = x, by = y, bd = `M${bx.toFixed(0)} ${by.toFixed(0)}`
          const dir = rand() > 0.5 ? 1 : -1
          for (let i = 0; i < 3; i++) {
            bx += dir * (18 + rand() * 40)
            by += 16 + rand() * 30
            bd += ` L${bx.toFixed(0)} ${by.toFixed(0)}`
          }
          branches.push(bd)
        }
      }
      return d + ' ' + branches.join(' ')
    }

    let timer
    function strike() {
      bolt.setAttribute('d', makeBolt())
      const len = bolt.getTotalLength()
      bolt.style.transition = 'none'
      bolt.style.strokeDasharray = len
      bolt.style.strokeDashoffset = len
      bolt.style.opacity = '1'
      // Force the reset to land before the reveal starts, or the transition is skipped.
      void bolt.getBoundingClientRect()
      bolt.style.transition = 'stroke-dashoffset 110ms linear, opacity 420ms ease-out 140ms'
      bolt.style.strokeDashoffset = '0'
      bolt.style.opacity = '0'

      flash.style.animation = 'none'
      void flash.getBoundingClientRect()
      flash.style.animation = 'flashPulse 480ms ease-out'

      timer = setTimeout(strike, 900 + rand() * 2200)
    }
    timer = setTimeout(strike, 500)
    return () => clearTimeout(timer)
  },
})

// ── 9. Ferdinand: the coastwatch ────────────────────────────────────────────
// A scene taken from a real project rather than invented for a demo, to show what these primitives
// are for. Ferdinand is an out-of-band Kubernetes node watchdog, named after the South Pacific
// Coastwatchers: posts scattered across occupied islands, each operator seeing only their own patch
// of sea, reporting by radio. Its own doctrine, from the README: observe and report, never
// intervene.
//
// The thing the scene has to say is in src/deadman/heartbeat.ts: "the operator is warned by its
// SILENCE". A dead man's switch inverts the alarm — the post that stops transmitting is the alert,
// because the messenger is inside the fire. So the scene's dramatic beat is not a post lighting up.
// It is a post going quiet, and the ring of watch around it closing.
scene({
  id: 'ferdinand',
  title: 'Ferdinand — the coastwatch',
  recipe: 'wave + parallax + ripple (staggered sked) + flicker + draw + the absence of ripple',
  cost: 'free + layout — 5 posts, sea on the tile channel',
  note:
    'A real project, not an invented subject: an out-of-band Kubernetes node watchdog named after ' +
    'the South Pacific Coastwatchers. Each island is a post; each expanding ring is that post ' +
    'reporting on its schedule, staggered so the network never pulses in unison. The alert is the ' +
    'one that STOPS — a dead man\'s switch is warned by silence, so the scene animates an absence. ' +
    'Severity colours are the project\'s own three: info, warning, critical.',
  build(stage) {
    stage.style.background = 'linear-gradient(#0a1428 0%, #12203c 42%, #1b3352 68%, #24405f 100%)'
    const rand = seeded(1942)   // the year the network went up

    // Sky: stars and a low moon. Anchored, so the drifting sea reads as the thing that moves.
    const sky = layer(stage)
    for (let i = 0; i < 90; i++) {
      const s = el(sky, 'circle', {
        cx: rand() * 1200, cy: rand() * 260, r: 0.4 + rand() * 1.0,
        fill: '#dce8ff', opacity: 0.2 + rand() * 0.45,
      })
      s.style.animation = `twinkle ${3 + rand() * 5}s ease-in-out ${-rand() * 7}s infinite`
    }
    const moonDefs = el(sky, 'defs')
    const moonGradient = el(moonDefs, 'radialGradient', { id: 'ferdinandMoon' })
    el(moonGradient, 'stop', { offset: '0%', 'stop-color': '#ffeec4', 'stop-opacity': '0.4' })
    el(moonGradient, 'stop', { offset: '100%', 'stop-color': '#ffeec4', 'stop-opacity': '0' })
    const glow = el(sky, 'circle', { cx: 200, cy: 120, r: 86, fill: 'url(#ferdinandMoon)' })
    glow.style.animation = 'breathe 13s ease-in-out infinite'
    el(sky, 'circle', { cx: 200, cy: 120, r: 26, fill: '#f6efd8' })

    // Five posts. Depth decides island size, haze and how far back the parallax puts them.
    // Two are quiet on purpose — that is the scene's subject, not decoration.
    const posts = [
      { x: 165, depth: 0, severity: 'info',     silent: false },
      { x: 430, depth: 1, severity: 'info',     silent: false },
      { x: 660, depth: 2, severity: 'warning',  silent: false },
      { x: 905, depth: 1, severity: 'critical', silent: true  },
      { x: 1105, depth: 0, severity: 'info',    silent: false },
    ]
    const severityColour = { info: '#7fd6a8', warning: '#e8c057', critical: '#e0654f' }

    // Sea behind the islands: two seamless tiles on the free channel (prototype 18).
    const seaBack = []
    for (let d = 0; d < 2; d++) {
      const svg = layer(stage, { viewBox: '0 0 2400 640', width: '200%' })
      svg.setAttribute('preserveAspectRatio', 'none')
      svg.style.animation = `roll ${26 + d * 14}s linear infinite`
      seaBack.push({ svg, base: 352 + d * 22, amp: 7 - d * 2, tone: 26 + d * 5 })
    }

    const islandLayer = layer(stage)
    const skedLayer = layer(stage)

    for (const post of posts) {
      // Depth reads through scale and haze, not through height: pushing the far islands down the
      // canvas sank them under the front sea bands, which start at y=430.
      const groundY = 372 + post.depth * 8
      const scale = 1 - post.depth * 0.17
      const haze = 0.95 - post.depth * 0.2

      const g = el(islandLayer, 'g', { opacity: haze })
      const w = 118 * scale
      // Island silhouette.
      el(g, 'path', {
        d: `M${post.x - w} ${groundY}
            Q ${post.x - w * 0.55} ${groundY - 30 * scale} ${post.x - w * 0.18} ${groundY - 20 * scale}
            Q ${post.x} ${groundY - 44 * scale} ${post.x + w * 0.3} ${groundY - 22 * scale}
            Q ${post.x + w * 0.7} ${groundY - 12 * scale} ${post.x + w} ${groundY} Z`,
        fill: `hsl(208 32% ${13 + post.depth * 5}%)`,
      })
      // Two palms, swaying about their base — the sway primitive, same rule as the tree scene.
      for (const side of [-1, 1]) {
        const px = post.x + side * 34 * scale
        const palm = el(g, 'g')
        palm.style.transformBox = 'view-box'
        palm.style.transformOrigin = `${px}px ${groundY - 16 * scale}px`
        palm.style.animation = `swayPalm ${4.2 + rand() * 1.8}s ease-in-out ${-rand() * 4}s infinite alternate`
        el(palm, 'line', {
          x1: px, y1: groundY - 16 * scale, x2: px + side * 4 * scale, y2: groundY - 44 * scale,
          stroke: `hsl(206 24% ${9 + post.depth * 4}%)`, 'stroke-width': 2 * scale,
          'stroke-linecap': 'round',
        })
        for (let f = 0; f < 4; f++) {
          const a = -Math.PI / 2 + (f - 1.5) * 0.55
          el(palm, 'line', {
            x1: px + side * 4 * scale, y1: groundY - 44 * scale,
            x2: px + side * 4 * scale + Math.cos(a) * 15 * scale,
            y2: groundY - 44 * scale + Math.sin(a) * 9 * scale,
            stroke: `hsl(206 24% ${9 + post.depth * 4}%)`, 'stroke-width': 1.6 * scale,
            'stroke-linecap': 'round',
          })
        }
      }
      // The transmitter mast.
      const mastTop = groundY - 62 * scale
      el(g, 'line', {
        x1: post.x, y1: groundY - 14 * scale, x2: post.x, y2: mastTop,
        stroke: '#7d8ea6', 'stroke-width': 1.8 * scale,
      })
      el(g, 'line', {
        x1: post.x - 9 * scale, y1: mastTop + 13 * scale,
        x2: post.x + 9 * scale, y2: mastTop + 13 * scale,
        stroke: '#7d8ea6', 'stroke-width': 1.3 * scale,
      })

      const lamp = el(g, 'circle', {
        cx: post.x, cy: mastTop - 3 * scale, r: 3 * scale,
        fill: severityColour[post.severity],
      })

      if (post.silent) {
        // The scene's whole point. This post transmits nothing: no ring leaves its mast. Its lamp
        // does not blink an alarm either — a dead post cannot raise one. What marks it is the ring
        // of watch closing around it, drawn by the posts that are still listening.
        lamp.setAttribute('opacity', '0.28')
        const ring = el(skedLayer, 'circle', {
          cx: post.x, cy: mastTop - 3 * scale, r: 46 * scale,
          fill: 'none', stroke: severityColour.critical, 'stroke-width': 1.5,
          'stroke-dasharray': '4 7', opacity: 0.9,
        })
        ring.style.transformBox = 'fill-box'
        ring.style.transformOrigin = 'center'
        ring.style.animation = 'silentRing 3.6s ease-in-out infinite'
        const mark = el(skedLayer, 'text', {
          x: post.x, y: mastTop - 58 * scale, 'text-anchor': 'middle',
          fill: severityColour.critical, 'font-size': 11 * scale,
          'font-family': 'ui-monospace, monospace', 'letter-spacing': 1.4,
        })
        mark.textContent = 'NO SKED'
        mark.style.animation = 'silentMark 3.6s ease-in-out infinite'
      } else {
        // The sked: this post reporting on its schedule. Three rings, staggered by a negative
        // delay, so the network never pulses in unison — which is what makes it read as five
        // independent operators rather than one animation.
        const period = 3.4 + post.depth * 0.7 + rand() * 0.9
        for (let i = 0; i < 3; i++) {
          const ripple = el(skedLayer, 'circle', {
            cx: post.x, cy: mastTop - 3 * scale, r: 8 * scale,
            fill: 'none', stroke: severityColour[post.severity], 'stroke-width': 1.4,
          })
          ripple.style.transformBox = 'fill-box'
          ripple.style.transformOrigin = 'center'
          ripple.style.animation = `sked ${period}s ease-out ${-(i / 3) * period}s infinite`
        }
        // A warning post still reports — it just reports badly. Flicker, not silence.
        if (post.severity === 'warning') {
          lamp.style.animation = 'flickerK 1.9s steps(1) infinite'
        } else {
          lamp.style.animation = `pulseLamp ${period}s ease-out infinite`
        }
      }
    }

    // Sea in front, drawn after the islands so they sit in the water rather than on it.
    for (const band of seaBack) {
      let d = `M0 640 L0 ${band.base}`
      for (let i = 0; i <= 160; i++) {
        const x = (i / 160) * 2400
        const u = (x / 2400) * Math.PI * 2
        const y = band.base + Math.sin(u * 4) * band.amp + Math.sin(u * 9) * band.amp * 0.45
        d += ` L${x.toFixed(1)} ${y.toFixed(2)}`
      }
      el(band.svg, 'path', { d: `${d} L2400 640 Z`, fill: `hsl(208 40% ${band.tone}%)` })
    }
    for (let d = 0; d < 3; d++) {
      const svg = layer(stage, { viewBox: '0 0 2400 640', width: '200%' })
      svg.setAttribute('preserveAspectRatio', 'none')
      svg.style.animation = `roll ${9 + d * 5}s linear infinite`
      const base = 430 + d * 62
      const amp = 15 - d * 2
      let d2 = `M0 640 L0 ${base}`
      for (let i = 0; i <= 200; i++) {
        const x = (i / 200) * 2400
        const u = (x / 2400) * Math.PI * 2
        const y = base + Math.sin(u * 3 + d) * amp
          + Math.sin(u * 7 - d * 0.6) * amp * 0.4 + Math.sin(u * 13) * amp * 0.16
        d2 += ` L${x.toFixed(1)} ${y.toFixed(2)}`
      }
      el(svg, 'path', {
        d: `${d2} L2400 640 Z`, fill: `hsl(${207 + d * 2} ${44 - d * 6}% ${17 + d * 6}%)`,
        opacity: 0.9,
      })
    }

    // Moonlight on the water: glints on the free channel, decorrelated.
    const glints = layer(stage)
    for (let i = 0; i < 20; i++) {
      const gl = el(glints, 'ellipse', {
        cx: 90 + rand() * 300, cy: 430 + rand() * 180,
        rx: 8 + rand() * 22, ry: 1.4, fill: '#ffeec4', opacity: 0.4,
      })
      gl.style.animation = `glint ${2.2 + rand() * 3}s ease-in-out ${-rand() * 5}s infinite`
    }
  },
})

// ── 10. Feldt: what the doctrine adds to a canvas that already works ────────
// The companion to scene 9, and the more useful of the two, because it starts from code that is
// already right rather than from a blank page.
//
// `feldt` is the central dead man's switch the ferdinand posts report to. Its /world screen draws an
// archipelago — one island per network, shape derived deterministically from the network id — and it
// draws it on a CANVAS, with a camera, level-of-detail and a baked stage. Measured in the source:
// src/http/scene.ts contains 49 canvas references, zero SVG, and — the number that decides this
// scene — ZERO requestAnimationFrame. The island is static; the only rAF is the camera flight.
//
// The honest reading of that, against the measurements in ../measurements.md: THE CANVAS IS RIGHT.
// A world with pan, zoom and many islands is exactly the case where retained-mode SVG loses, and
// nothing in this research suggests porting it. What the doctrine adds is elsewhere — the ambient
// motion the screen does not have, placed on the channel that costs nothing, so it never competes
// with the camera's bake.
//
// The toggle in the corner is the whole argument: same islands, same canvas, motion added only in
// layers above it.
scene({
  id: 'feldt',
  title: 'Feldt — motion added to a canvas that was already right',
  recipe: 'canvas (kept) + wave + parallax + ripple/absence + flicker, all in layers above it',
  cost: 'the canvas is baked once; every added layer is on the 0-layout/s channel',
  note:
    'Starts from real code that is already correct. The /world screen draws its archipelago on a ' +
    'canvas with a camera and level-of-detail, and its island is static — 49 canvas references and ' +
    'zero requestAnimationFrame in src/http/scene.ts. The doctrine does NOT say port it to SVG: a ' +
    'world with pan and zoom is where SVG loses. It says put the missing ambient motion in layers ' +
    'above the canvas, where it costs no layout and never invalidates the bake. Toggle the switch ' +
    'to see exactly what is added. States are the project\'s own four.',
  build(stage, options = {}) {
    // options.naiveMarks puts every sked ring inside ONE <svg>, which is the obvious way to write
    // it — and costs layout every frame, because §2 of the report applies to these rings exactly as
    // it applies to anything else inside an SVG. The default promotes each mark to its own <svg>
    // element, which is the same picture on the free channel. Prototypes 20 and 21 measure both.
    const naiveMarks = options.naiveMarks === true
    stage.style.background = 'linear-gradient(#0c1a2b 0%, #143454 45%, #1d4668 100%)'

    // The project's own four states, and its own rule about colour: scenery stays in sea tones,
    // outside the state vocabulary, so terrain can never be misread as information.
    const stateColour = {
      transmitting: '#1f9d61',
      late: '#d99a2b',
      lost: '#c8452a',
      muted: '#6b7280',
    }

    // Nine networks. Shape comes from the id, exactly as scene.js derives it from a seeded hash —
    // so a network's island is the same island every time, and never moves because its severity
    // changed. That is the project's own rule and it is a good one: motion without cause, on an
    // on-call screen, reads as something happening.
    const networks = [
      { id: 'k0s-prd',        posts: 9, state: 'transmitting' },
      { id: 'vps-kinghost',   posts: 3, state: 'transmitting' },
      { id: 'housek8s',       posts: 6, state: 'late' },
      { id: 'edge-sp',        posts: 4, state: 'transmitting' },
      { id: 'lab-vm',         posts: 2, state: 'lost' },
      { id: 'observability',  posts: 5, state: 'transmitting' },
      { id: 'gearound',       posts: 3, state: 'muted' },
      { id: 'fabcost3d',      posts: 2, state: 'transmitting' },
      { id: 'speakmemo',      posts: 4, state: 'transmitting' },
    ]

    // FNV-1a, the same family scene.js uses for its stable seed.
    const seedFrom = (text) => {
      let h = 0x811c9dc5
      for (let i = 0; i < text.length; i++) {
        h ^= text.charCodeAt(i)
        h = Math.imul(h, 0x01000193) >>> 0
      }
      return h
    }
    const rngFrom = (seed) => {
      let s = seed || 1
      return () => ((s = Math.imul(s ^ (s >>> 15), 1 | s) >>> 0), ((s ^ (s >>> 7)) >>> 0) / 4294967296)
    }

    // Island outline as a closed radial shape, radius modulated by the seed — the shape of the
    // coast is a function of the network id and nothing else.
    function islandRadii(seed) {
      const rand = rngFrom(seed)
      const points = 30
      const a1 = 0.16 + rand() * 0.2, a2 = 0.1 + rand() * 0.14, a3 = 0.05 + rand() * 0.09
      const p1 = rand() * 6.28, p2 = rand() * 6.28, p3 = rand() * 6.28
      const radii = []
      for (let i = 0; i < points; i++) {
        const a = (i / points) * Math.PI * 2
        radii.push(1 + Math.sin(a * 2 + p1) * a1 + Math.sin(a * 3 + p2) * a2 + Math.sin(a * 5 + p3) * a3)
      }
      return radii
    }

    // Layout: islands placed on a loose grid, size from post count — the project's own rule that a
    // bigger network is a bigger island, from the same population band table.
    const W = 1200, H = 640
    const placed = networks.map((net, i) => {
      const rand = rngFrom(seedFrom(net.id + ':place'))
      const col = i % 3, row = Math.floor(i / 3)
      return {
        ...net,
        x: 150 + col * 400 + (rand() - 0.5) * 90,
        y: 165 + row * 165 + (rand() - 0.5) * 50,
        radius: 34 + Math.sqrt(net.posts) * 15,
        radii: islandRadii(seedFrom(net.id)),
      }
    })

    // ── The canvas: exactly the part that stays as it is ──────────────────
    // Drawn ONCE, like the project's baked stage. Nothing below re-enters this context per frame,
    // which is the whole point: the added motion must not invalidate the bake.
    const canvas = document.createElement('canvas')
    canvas.className = 'layer canvasLayer'
    canvas.width = W
    canvas.height = H
    stage.appendChild(canvas)
    const ctx = canvas.getContext('2d')

    function islandPath(island, grow) {
      ctx.beginPath()
      island.radii.forEach((r, i) => {
        const a = (i / island.radii.length) * Math.PI * 2
        const rr = (island.radius + grow) * r
        const px = island.x + Math.cos(a) * rr
        const py = island.y + Math.sin(a) * rr * 0.62      // flattened: seen from above, at an angle
        i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py)
      })
      ctx.closePath()
    }

    for (const island of placed) {
      // Shelf, beach, land, uplands — scenery in sea and earth tones only.
      ctx.fillStyle = 'rgba(120, 190, 220, 0.16)'
      islandPath(island, 16)
      ctx.fill()
      ctx.fillStyle = '#d9cba4'
      islandPath(island, 4)
      ctx.fill()
      ctx.fillStyle = '#4a6b4a'
      islandPath(island, 0)
      ctx.fill()
      ctx.fillStyle = '#3d5c40'
      islandPath(island, -island.radius * 0.28)
      ctx.fill()
      ctx.fillStyle = '#5b7a52'
      islandPath(island, -island.radius * 0.55)
      ctx.fill()

      // Vegetation stippling, seeded so the island is identical on every render.
      const rand = rngFrom(seedFrom(island.id + ':veg'))
      for (let i = 0; i < island.posts * 14; i++) {
        const a = rand() * Math.PI * 2
        const rr = island.radius * (0.15 + rand() * 0.6)
        ctx.globalAlpha = 0.35 + rand() * 0.4
        ctx.fillStyle = rand() > 0.5 ? '#37542f' : '#6a8a55'
        ctx.beginPath()
        ctx.arc(island.x + Math.cos(a) * rr, island.y + Math.sin(a) * rr * 0.62, 1.4 + rand() * 2, 0, 6.3)
        ctx.fill()
      }
      ctx.globalAlpha = 1
    }

    // ── The layers the doctrine adds, above the canvas ────────────────────
    // Each is its own <svg> element or a CSS-animated box: 0 layout per frame, and the canvas is
    // never touched again.
    const motion = document.createElement('div')
    motion.className = 'feldtMotion'
    stage.appendChild(motion)

    // Sea: two seamless tiles behind nothing — they read as swell moving past the archipelago.
    for (let d = 0; d < 2; d++) {
      const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
      svg.setAttribute('viewBox', '0 0 2400 640')
      svg.setAttribute('preserveAspectRatio', 'none')
      svg.setAttribute('class', 'layer')
      svg.style.width = '200%'
      svg.style.animation = `roll ${34 + d * 22}s linear infinite`
      svg.style.opacity = 0.5 - d * 0.2
      let path = ''
      for (let band = 0; band < 6; band++) {
        const base = 70 + band * 105 + d * 40
        let seg = `M0 ${base}`
        for (let i = 0; i <= 120; i++) {
          const x = (i / 120) * 2400
          const u = (x / 2400) * Math.PI * 2
          seg += ` L${x.toFixed(1)} ${(base + Math.sin(u * 4 + band) * 5 + Math.sin(u * 9 + d) * 2).toFixed(2)}`
        }
        path += seg + ' '
      }
      el(svg, 'path', { d: path, fill: 'none', stroke: '#9fd2ea', 'stroke-width': 1.1 })
      motion.appendChild(svg)
    }

    // Sked rings and state lamps, one <svg> for the whole set — they do not move as units, so they
    // do not each need to be their own element.
    const marks = document.createElementNS(SVG_NAMESPACE, 'svg')
    marks.setAttribute('viewBox', `0 0 ${W} ${H}`)
    marks.setAttribute('preserveAspectRatio', 'xMidYMid slice')
    marks.setAttribute('class', 'layer')
    motion.appendChild(marks)

    // One <svg> per moving mark, sized and positioned to the island it belongs to. Everything that
    // animates lives at the top of its own element, so the transform is on an HTML-level box.
    // Static text and non-animated lamps stay in the shared `marks` layer: they do not move, so
    // promoting them would buy nothing and cost elements.
    // One <svg> per ANIMATION, and the animation is applied to that <svg> itself — not to a shape
    // inside it. That distinction is the whole lesson: promoting the container while still
    // animating a child leaves the work exactly where it was (measured: prototype 20 and a first
    // version of 21 both reported 37 layout/s). The transform has to land on the HTML-level box.
    function movingMark(island, extent, animation) {
      if (naiveMarks) return { host: marks, cx: island.x, cy: island.markY, animated: null }
      const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
      const size = extent * 2
      svg.setAttribute('viewBox', `${-extent} ${-extent} ${size} ${size}`)
      svg.setAttribute('class', 'mark')
      // Positioned in percentages of the stage so it tracks the canvas's cover mapping.
      svg.style.left = `${((island.x - extent) / W) * 100}%`
      svg.style.top = `${((island.markY - extent) / H) * 100}%`
      svg.style.width = `${(size / W) * 100}%`
      svg.style.height = `${(size / H) * 100}%`
      if (animation) svg.style.animation = animation
      motion.appendChild(svg)
      return { host: svg, cx: 0, cy: 0, animated: svg }
    }

    for (const island of placed) {
      const colour = stateColour[island.state]
      const y = island.y - island.radius * 0.5
      island.markY = y
      const period = 3.2 + (seedFrom(island.id) % 1000) / 650
      const extent = island.radius + 26

      const applyAnimation = (mark, shape, animation) => {
        // Promoted: the box animates and the shape is inert. Naive: the shape animates, inside the
        // shared <svg>, which is what costs layout every frame.
        const target = mark.animated || shape
        if (!mark.animated) {
          shape.style.transformBox = 'fill-box'
          shape.style.transformOrigin = 'center'
        }
        target.style.animation = animation
      }

      if (island.state === 'lost') {
        // The dead man's switch, again: no ring leaves this island. What marks it is a ring
        // closing on it, and the mark only means anything because the others are pulsing.
        const mark = movingMark(island, extent, null)
        const ring = el(mark.host, 'circle', {
          cx: mark.cx, cy: mark.cy, r: island.radius + 20,
          fill: 'none', stroke: colour, 'stroke-width': 1.6, 'stroke-dasharray': '4 7',
        })
        applyAnimation(mark, ring, 'silentRing 3.6s ease-in-out infinite')
      } else if (island.state !== 'muted') {
        for (let i = 0; i < 2; i++) {
          const mark = movingMark(island, extent, null)
          const ripple = el(mark.host, 'circle', {
            cx: mark.cx, cy: mark.cy, r: island.radius * 0.5,
            fill: 'none', stroke: colour, 'stroke-width': 1.3, opacity: 0.8,
          })
          applyAnimation(mark, ripple, `sked ${period}s ease-out ${-(i / 2) * period}s infinite`)
        }
      }

      const lampMark = movingMark(island, 10, null)
      const lamp = el(lampMark.host, 'circle', { cx: lampMark.cx, cy: lampMark.cy, r: 4, fill: colour })
      if (island.state === 'late') applyAnimation(lampMark, lamp, 'flickerK 1.9s steps(1) infinite')
      else if (island.state === 'transmitting') applyAnimation(lampMark, lamp, `pulseLamp ${period}s ease-out infinite`)
      else if (island.state === 'muted') lamp.setAttribute('opacity', '0.4')
      else lamp.setAttribute('opacity', '0.3')

      const label = el(marks, 'text', {
        x: island.x, y: island.y + island.radius * 0.72 + 16, 'text-anchor': 'middle',
        fill: '#c8dcef', 'font-size': 10, 'font-family': 'ui-monospace, monospace', opacity: 0.72,
      })
      label.textContent = island.id
    }

    // The switch. The comparison is the point of the plate, so it has to be operable, not described.
    const toggle = document.createElement('button')
    toggle.type = 'button'
    toggle.className = 'feldtToggle'
    toggle.textContent = 'ambient motion: on'
    toggle.addEventListener('click', () => {
      const off = stage.classList.toggle('motionOff')
      toggle.textContent = `ambient motion: ${off ? 'off — this is the screen today' : 'on'}`
    })
    stage.appendChild(toggle)
  },
})

// ── The creatures: mechanics, isolated ──────────────────────────────────────
// A bestiary rather than a scene. Each animal is shown alone and large, because the point is the
// MECHANISM, and a mechanism is not judgeable at forty pixels inside a landscape.
//
// The rule this set exists to teach, and which cost the birds two rewrites to learn:
//
//   CHOOSE THE VIEW IN WHICH THE MECHANISM IS VISIBLE.
//
// A dolphin and a shark both "swim with the tail", and their mechanics are opposites. Cetaceans
// descend from land mammals whose spines flex UP AND DOWN, so their flukes are HORIZONTAL and they
// oscillate dorsoventrally. Sharks descend from fish whose spines flex SIDE TO SIDE, so their
// caudal fin is VERTICAL and they undulate laterally. Draw both from the side and one of them is a
// lie: the shark's whole stroke happens in the plane you cannot see. So the dolphin is shown in
// profile and the shark from above, and that choice is not a stylistic one.
const creatures = []
const creature = (def) => { creatures.push(def); return def }

/**
 * Build a fusiform body from a PROFILE TABLE rather than from guessed Bézier curves.
 *
 * The first bestiary was drawn by writing curve handles by eye, and the result was exactly what
 * that method produces: a hole between the melon and the rostrum, a rectangular step where one
 * hand-written path met the next, a belly patch floating off the body. Judged large and against a
 * grid, it was indefensible.
 *
 * A body like this is not a set of curves, it is a THICKNESS FUNCTION. At each station along the
 * axis there is a distance up to the back and a distance down to the belly; the outline is what you
 * get by walking the stations. Written that way the silhouette is continuous by construction — there
 * is one path, so there is nothing to misalign — and each number is a proportion that can be
 * checked against the animal instead of a handle that can only be judged by taste.
 *
 * Stations are fractions of body length; back/belly are fractions of body length too, so the whole
 * table is scale-free and the final size is one multiplier.
 */
function fusiform(stations, length, scale = 1) {
  const px = (v) => v * length * scale
  // Station 0 is the snout and station 1 the tail, on an animal facing +x.
  const ax = (x) => px(0.5 - x)
  const top = stations.map((s) => [ax(s.x), -px(s.back)])
  const bottom = [...stations].reverse().map((s) => [ax(s.x), px(s.belly)])
  const ring = [...top, ...bottom]

  // Catmull-Rom through the stations, emitted as cubics: a smooth closed outline that passes
  // exactly through every measured point, which a hand-written Bézier does not.
  const n = ring.length
  let d = `M${ring[0][0].toFixed(2)} ${ring[0][1].toFixed(2)}`
  for (let i = 0; i < n; i++) {
    const p0 = ring[(i - 1 + n) % n], p1 = ring[i], p2 = ring[(i + 1) % n], p3 = ring[(i + 2) % n]
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6]
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6]
    d += `C${c1[0].toFixed(2)} ${c1[1].toFixed(2)} ${c2[0].toFixed(2)} ${c2[1].toFixed(2)} ${p2[0].toFixed(2)} ${p2[1].toFixed(2)}`
  }
  return d + 'Z'
}

/** A chain of hinged segments carrying a travelling wave — the spine of every swimmer here. */
function spine(host, segments, animation, beat, phaseStep) {
  const nodes = []
  let parent = host
  for (let i = 0; i < segments.length; i++) {
    const g = el(parent, 'g')
    g.style.transformBox = 'view-box'
    g.style.transformOrigin = `${segments[i].pivotX}px ${segments[i].pivotY}px`
    // Each segment lags the one before it. That lag IS the travelling wave: without it the animal
    // flexes as one rigid hinge, which reads as a windscreen wiper rather than a swimmer.
    g.style.animation = `${animation} ${beat}s ease-in-out ${(-i * phaseStep * beat).toFixed(3)}s infinite`
    nodes.push(g)
    parent = g
  }
  return nodes
}

creature({
  id: 'dolphin',
  title: 'Bottlenose dolphin',
  latin: 'Tursiops truncatus',
  view: 'profile — the stroke is vertical, so profile is where it shows',
  mechanism: 'dorsoventral oscillation · horizontal fluke · body wave from mid-body back',
  build(host) {
    const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
    svg.setAttribute('viewBox', '-76 -34 152 68')
    svg.setAttribute('class', 'mini')
    host.appendChild(svg)

    const skin = '#4c6076', dark = '#3d5165', belly = '#c9d7e3'
    const L = 100

    const root = el(svg, 'g')
    root.style.transformBox = 'view-box'
    root.style.transformOrigin = '0px 0px'
    root.style.animation = 'swimHeave 1.9s ease-in-out infinite'

    // Profile table for Tursiops. x is distance from the snout as a fraction of body length; back
    // and belly are also fractions of body length, so the whole animal is scale-free.
    // The shape facts these numbers encode, each checkable against the animal:
    //   · maximum girth at ~34% back from the snout, not at the middle
    //   · the MELON — a fatty dome that rises steeply from ~7% and peaks at ~14%
    //   · a CREASE between melon and rostrum: the profile steps down, it does not taper smoothly
    //   · the rostrum is short and thick (a bottlenose, not a spinner), about 6% of length
    //   · total depth ~0.21 L
    const body = [
      { x: 0.000, back: 0.012, belly: 0.012 },   // tip of the rostrum
      { x: 0.030, back: 0.024, belly: 0.022 },
      { x: 0.058, back: 0.032, belly: 0.030 },   // rostrum, near-cylindrical
      { x: 0.072, back: 0.058, belly: 0.034 },   // THE CREASE — melon rises abruptly here
      { x: 0.100, back: 0.082, belly: 0.044 },
      { x: 0.140, back: 0.094, belly: 0.060 },   // crown of the melon
      { x: 0.190, back: 0.099, belly: 0.074 },   // blowhole sits about here
      { x: 0.260, back: 0.104, belly: 0.090 },
      { x: 0.340, back: 0.108, belly: 0.100 },   // maximum girth
      { x: 0.430, back: 0.104, belly: 0.094 },
      { x: 0.520, back: 0.094, belly: 0.082 },
      { x: 0.620, back: 0.080, belly: 0.066 },
      { x: 0.720, back: 0.062, belly: 0.050 },
      { x: 0.820, back: 0.044, belly: 0.035 },
      { x: 0.900, back: 0.031, belly: 0.025 },   // peduncle
      { x: 0.955, back: 0.024, belly: 0.019 },
    ]

    // THE TAIL IS BUILT FIRST, so the trunk is painted over its root.
    //
    // Drawn last it sat on top of the body, and its own outline cut a visible step across the back,
    // the belly and the countershading. Order is not a detail here: a rotating part must go UNDER
    // the part it hinges from, or its edge becomes a seam that no amount of curve-tuning removes.
    const tail = spine(root, [
      { pivotX: (0.5 - 0.86) * L, pivotY: 0 },
      { pivotX: (0.5 - 0.955) * L, pivotY: 0 },
    ], 'swimFlukeUpDown', 1.9, 0.16)

    const stock = [
      { x: 0.74, back: 0.058, belly: 0.045 },   // starts well inside the trunk: no visible seam
      { x: 0.82, back: 0.047, belly: 0.037 },
      { x: 0.90, back: 0.034, belly: 0.027 },
      { x: 0.95, back: 0.026, belly: 0.021 },
      { x: 0.99, back: 0.021, belly: 0.017 },
    ]
    el(tail[0], 'path', { d: fusiform(stock, L), fill: skin })

    // Fluke: two broad lobes swept back from a central notch, horizontal. Span about 0.25 L.
    el(tail[1], 'path', {
      d: `M${(0.5 - 0.92) * L} ${-0.021 * L} `
       + `C${(0.5 - 0.99) * L} ${-0.052 * L}, ${(0.5 - 1.08) * L} ${-0.098 * L}, ${(0.5 - 1.17) * L} ${-0.126 * L} `
       + `C${(0.5 - 1.19) * L} ${-0.108 * L}, ${(0.5 - 1.15) * L} ${-0.075 * L}, ${(0.5 - 1.08) * L} ${-0.040 * L} `
       + `C${(0.5 - 1.04) * L} ${-0.020 * L}, ${(0.5 - 1.015) * L} ${-0.008 * L}, ${(0.5 - 1.008) * L} ${0} `
       + `C${(0.5 - 1.015) * L} ${0.008 * L}, ${(0.5 - 1.04) * L} ${0.020 * L}, ${(0.5 - 1.08) * L} ${0.040 * L} `
       + `C${(0.5 - 1.15) * L} ${0.075 * L}, ${(0.5 - 1.19) * L} ${0.108 * L}, ${(0.5 - 1.17) * L} ${0.126 * L} `
       + `C${(0.5 - 1.08) * L} ${0.098 * L}, ${(0.5 - 0.99) * L} ${0.052 * L}, ${(0.5 - 0.92) * L} ${0.021 * L} Z`,
      fill: skin,
    })

    // The dorsal fin, ALSO before the trunk. Same rule as the tail, and the one I failed to apply
    // to the fins: an appendage drawn after the body meets it along an edge, and that edge is a
    // notch. Drawn before, its root is simply buried — the body's own outline becomes the join,
    // and no blending is needed because there is nothing to blend.
    //
    // Falcate: swept back with a concave trailing edge, tip falling behind the base. Its root runs
    // deep enough inside the back that no part of the base can ever surface.
    el(root, 'path', {
      d: `M${(0.5 - 0.345) * L} ${-0.060 * L} `                                     // root, inside the body
       + `C${(0.5 - 0.395) * L} ${-0.150 * L}, ${(0.5 - 0.445) * L} ${-0.196 * L}, ${(0.5 - 0.500) * L} ${-0.206 * L} `
       + `C${(0.5 - 0.472) * L} ${-0.166 * L}, ${(0.5 - 0.458) * L} ${-0.120 * L}, ${(0.5 - 0.456) * L} ${-0.055 * L} Z`,
      fill: skin,
    })

    // Now the trunk, over the roots of both.
    el(root, 'path', { d: fusiform(body, L), fill: skin })

    // Belly countershading, built from the SAME table so it can never drift off the body: the
    // lower half of the outline, pulled up by a fraction of the local thickness.
    //
    // It STOPS at the peduncle. Carried to the end of the table it ran out over the tail stock —
    // which is drawn earlier and therefore underneath — and surfaced as a pale tongue lying across
    // the tail. Countershading belongs to the trunk; the peduncle and flukes are dark all round.
    // It also TAPERS rather than stopping: cut off square it read as a sticker with a rounded end.
    // On the animal the pale field narrows to nothing along the peduncle, so the band's height is
    // faded out over the last stretch.
    const taper = (x) => Math.min(1, Math.max(0, (0.88 - x) / 0.22))
    const bellyBand = body.filter((s) => s.x <= 0.86)
      .map((s) => ({
        x: s.x,
        back: -s.belly * 0.30 * taper(s.x),
        belly: s.belly * 0.92 * taper(s.x),
      }))
    el(root, 'path', { d: fusiform(bellyBand, L), fill: belly, opacity: 0.85 })

    // Mouthline: from the tip of the rostrum, straight back and lifting slightly at the gape. It
    // ends where the melon crease is, which is where a dolphin's mouth actually ends.
    el(root, 'path', {
      d: `M${(0.5 - 0.012) * L} ${0.010 * L} L${(0.5 - 0.062) * L} ${0.024 * L} `
       + `C${(0.5 - 0.082) * L} ${0.028 * L}, ${(0.5 - 0.098) * L} ${0.026 * L}, ${(0.5 - 0.110) * L} ${0.020 * L}`,
      fill: 'none', stroke: dark, 'stroke-width': 0.9, 'stroke-linecap': 'round',
    })
    el(root, 'circle', { cx: (0.5 - 0.118) * L, cy: -0.006 * L, r: 1.0, fill: '#101820' })
    el(root, 'ellipse', { cx: (0.5 - 0.195) * L, cy: -0.096 * L, rx: 1.6, ry: 0.75, fill: dark })

    // Pectoral flipper — a DOLPHIN's, which is a different object from a whale's:
    //   · short: about 0.14 L, against the humpback's 0.30
    //   · BROAD at the root and tapering, so it reads as a paddle, not a blade
    //   · gently swept back with a slightly convex leading edge and a concave trailing edge
    //   · rooted at ~24%, just behind the head, and angled down and back
    // The root is buried inside the flank so the join has no edge.
    el(root, 'path', {
      d: `M${(0.5 - 0.205) * L} ${0.070 * L} `                                  // root, inside the body
       + `C${(0.5 - 0.245) * L} ${0.125 * L}, ${(0.5 - 0.295) * L} ${0.175 * L}, ${(0.5 - 0.355) * L} ${0.205 * L} `  // leading edge, convex
       + `C${(0.5 - 0.372) * L} ${0.208 * L}, ${(0.5 - 0.378) * L} ${0.196 * L}, ${(0.5 - 0.366) * L} ${0.184 * L} `  // rounded tip
       + `C${(0.5 - 0.325) * L} ${0.150 * L}, ${(0.5 - 0.283) * L} ${0.108 * L}, ${(0.5 - 0.262) * L} ${0.062 * L} Z`, // trailing edge, concave
      fill: skin,
    })

  },
})

creature({
  id: 'whale',
  title: 'Humpback whale',
  latin: 'Megaptera novaeangliae',
  view: 'profile — the same vertical stroke as the dolphin, at a third of the rate',
  mechanism: 'dorsoventral oscillation · pectorals ⅓ of body length · ventral pleats · knobbly rostrum',
  build(host) {
    const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
    svg.setAttribute('viewBox', '-78 -40 156 80')
    svg.setAttribute('class', 'mini')
    host.appendChild(svg)

    const skin = '#3b4d61', dark = '#2e3d4e', belly = '#b9c8d6'
    const L = 100

    const root = el(svg, 'g')
    root.style.transformBox = 'view-box'
    root.style.transformOrigin = '0px 0px'
    root.style.animation = 'swimHeave 5.4s ease-in-out infinite'

    // Profile table for Megaptera. What separates it from the dolphin is not decoration:
    //   · far bulkier — depth ~0.30 L against the dolphin's 0.21
    //   · NO rostrum. The head is a broad, blunt wedge, about a third of total length
    //   · maximum girth further forward, ~28%
    //   · the "hump": a low rise carrying a small dorsal fin at ~65%
    //   · a deep, narrow peduncle behind it
    const body = [
      { x: 0.000, back: 0.028, belly: 0.030 },   // blunt snout — no beak at all
      { x: 0.040, back: 0.050, belly: 0.058 },
      { x: 0.090, back: 0.076, belly: 0.092 },
      { x: 0.150, back: 0.100, belly: 0.122 },   // the jaw is deep: this is a lunge feeder
      { x: 0.220, back: 0.120, belly: 0.140 },
      { x: 0.280, back: 0.132, belly: 0.148 },   // maximum girth, well forward
      { x: 0.360, back: 0.134, belly: 0.140 },
      { x: 0.450, back: 0.128, belly: 0.124 },
      { x: 0.540, back: 0.116, belly: 0.104 },
      { x: 0.630, back: 0.104, belly: 0.082 },
      { x: 0.660, back: 0.108, belly: 0.076 },   // the hump
      { x: 0.720, back: 0.086, belly: 0.062 },
      { x: 0.800, back: 0.062, belly: 0.044 },
      { x: 0.870, back: 0.044, belly: 0.031 },
      { x: 0.930, back: 0.032, belly: 0.023 },   // peduncle
      { x: 0.970, back: 0.025, belly: 0.018 },
    ]
    // Tail first, so the trunk covers its root — same rule as the dolphin. A rotating part goes
    // UNDER the part it hinges from, or its outline cuts a step across the body.
    const tail = spine(root, [
      { pivotX: (0.5 - 0.88) * L, pivotY: 0 },
      { pivotX: (0.5 - 0.975) * L, pivotY: 0 },
    ], 'swimFlukeUpDown', 5.4, 0.16)

    const stock = [
      { x: 0.76, back: 0.078, belly: 0.055 },
      { x: 0.86, back: 0.050, belly: 0.036 },
      { x: 0.93, back: 0.034, belly: 0.024 },
      { x: 0.99, back: 0.024, belly: 0.017 },
    ]
    el(tail[0], 'path', { d: fusiform(stock, L), fill: skin })

    // Fluke: broad, deeply notched, with a ragged trailing edge. Span ~0.33 L.
    el(tail[1], 'path', {
      d: `M${(0.5 - 0.94) * L} ${-0.024 * L} `
       + `C${(0.5 - 1.02) * L} ${-0.075 * L}, ${(0.5 - 1.12) * L} ${-0.145 * L}, ${(0.5 - 1.23) * L} ${-0.175 * L} `
       + `C${(0.5 - 1.26) * L} ${-0.150 * L}, ${(0.5 - 1.20) * L} ${-0.100 * L}, ${(0.5 - 1.10) * L} ${-0.048 * L} `
       + `C${(0.5 - 1.05) * L} ${-0.022 * L}, ${(0.5 - 1.015) * L} ${-0.008 * L}, ${(0.5 - 1.008) * L} ${0} `
       + `C${(0.5 - 1.015) * L} ${0.008 * L}, ${(0.5 - 1.05) * L} ${0.022 * L}, ${(0.5 - 1.10) * L} ${0.048 * L} `
       + `C${(0.5 - 1.20) * L} ${0.100 * L}, ${(0.5 - 1.26) * L} ${0.150 * L}, ${(0.5 - 1.23) * L} ${0.175 * L} `
       + `C${(0.5 - 1.12) * L} ${0.145 * L}, ${(0.5 - 1.02) * L} ${0.075 * L}, ${(0.5 - 0.94) * L} ${0.024 * L} Z`,
      fill: skin,
    })

    // Dorsal before the trunk, for the same reason as the dolphin's. Small, low and far back,
    // sitting on the hump the animal is named for.
    el(root, 'path', {
      d: `M${(0.5 - 0.620) * L} ${-0.070 * L} `                                      // root, inside the body
       + `C${(0.5 - 0.648) * L} ${-0.130 * L}, ${(0.5 - 0.680) * L} ${-0.158 * L}, ${(0.5 - 0.714) * L} ${-0.156 * L} `
       + `C${(0.5 - 0.700) * L} ${-0.132 * L}, ${(0.5 - 0.692) * L} ${-0.106 * L}, ${(0.5 - 0.694) * L} ${-0.066 * L} Z`,
      fill: skin,
    })

    el(root, 'path', { d: fusiform(body, L), fill: skin })

    const taper = (x) => Math.min(1, Math.max(0, (0.86 - x) / 0.20))
    const bellyBand = body.filter((s) => s.x <= 0.84)
      .map((s) => ({
        x: s.x,
        back: -s.belly * 0.42 * taper(s.x),
        belly: s.belly * 0.94 * taper(s.x),
      }))
    el(root, 'path', { d: fusiform(bellyBand, L), fill: belly, opacity: 0.8 })

    // Ventral pleats: the grooved throat that expands when it lunges. They run from the chin back
    // to about 45% and follow the belly line, so they are generated from the same table.
    for (let i = 0; i < 8; i++) {
      const depth = 0.94 - i * 0.075          // fraction of the local belly depth
      const pts = body.filter((s) => s.x > 0.02 && s.x < 0.34)
        .map((s) => `${((0.5 - s.x) * L).toFixed(1)} ${(s.belly * L * depth).toFixed(1)}`)
      el(root, 'path', {
        d: 'M' + pts.join(' L'),
        fill: 'none', stroke: '#8fa3b6', 'stroke-width': 0.45, opacity: 0.5,
      })
    }

    // Tubercles: the knobs along the rostrum and jaw, each with a single hair. Nobody draws them,
    // and they are the feature that says "humpback" rather than "generic whale".
    for (const [x, side] of [[0.04, -1], [0.085, -1], [0.135, -1], [0.19, -1],
                             [0.05, 1], [0.10, 1], [0.155, 1], [0.21, 1]]) {
      const s = body.reduce((a, b) => (Math.abs(b.x - x) < Math.abs(a.x - x) ? b : a))
      el(root, 'circle', {
        cx: (0.5 - x) * L,
        cy: side < 0 ? -s.back * L * 0.86 : s.belly * L * 0.90,
        r: 1.25, fill: dark,
      })
    }
    el(root, 'circle', { cx: (0.5 - 0.185) * L, cy: -0.058 * L, r: 1.25, fill: '#0d141c' })

    // Pectoral: Megaptera — "big wing". About a THIRD of body length, scalloped along the leading
    // edge, white below. It sculls slowly and out of phase with the tail.
    const pec = el(root, 'g')
    pec.style.transformBox = 'view-box'
    pec.style.transformOrigin = '24px 15px'
    pec.style.animation = 'whalePectoral 5.4s ease-in-out infinite'
    // A humpback's pectoral, written as an explicit outline. Generating it from an axis and a
    // chord function gave no control over the two things that carry the shape — the width and the
    // rounded tip — and produced first a saw blade and then a ribbon.
    //
    // The shape, from the animal:
    //   · about 0.30 L long: a third of the whale, the longest flipper of any cetacean
    //   · WIDE — roughly 1/6 of its own length, widest a third of the way out
    //   · the LEADING edge (upper, forward) carries rounded tubercles; the trailing edge is smooth
    //   · the tip is ROUNDED, never pointed
    //   · white below, which is why it is the pale shape on a dark animal
    //
    // Coordinates are absolute in the L-grid: the root sits inside the flank at ~22%, and the tip
    // reaches back and down to ~52%.
    el(pec, 'path', {
      // The root LIES ON the ventral surface rather than inside it.
      //
      // The dolphin's flipper could be buried because it is the same colour as the body — the
      // buried part simply disappears. A humpback's is white, so anything of it inside the body
      // shows as a pale wedge with a straight edge, which is the corner the maintainer's arrow
      // found. The fix is not a deeper root: it is a root that follows the belly line, so there is
      // no interior part at all. The two numbers below are belly(0.22) and belly(0.30) read off the
      // profile table above.
      d: 'M28 13.9 C 26.8 15.4, 25.6 16.6, 24 17.8 '
        // Leading edge, root to tip. Each pair of curves is one tubercle: out, then back in.
       + 'C 22.4 19.6, 21.9 20.5, 20.1 22.2 '
       + 'C 18.4 24, 17.8 24.9, 15.8 26.5 '
       + 'C 13.9 28.1, 13.2 28.9, 11 30.3 '
       + 'C 8.9 31.7, 8.1 32.2, 5.8 33.3 '
       + 'C 3.5 34.4, 2.6 34.8, 0.2 35.5 '
        // Rounded tip.
       + 'C -2.5 36.3, -5.1 35.7, -5.7 33.6 '
       + 'C -6.2 31.7, -4.7 30.1, -2.6 29.1 '
        // Trailing edge back to the root: smooth, no tubercles, gently concave.
       + 'C 3.6 25.9, 11.2 21.2, 17.4 16.4 '
       + 'C 19.4 15.8, 20 15.2, 20 14.8 Z',
      fill: '#cbdae5', stroke: '#93a8ba', 'stroke-width': 0.7, 'stroke-linejoin': 'round',
    })

  },
})

creature({
  id: 'shark',
  title: 'Shark',
  latin: 'lamniform build — Carcharodon / Isurus',
  view: 'FROM ABOVE — the stroke is lateral, and in profile it would be invisible',
  mechanism: 'lateral undulation · vertical caudal fin · thunniform: the wave lives in the rear third',
  build(host) {
    const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
    svg.setAttribute('viewBox', '-72 -36 144 72')
    svg.setAttribute('class', 'mini')
    host.appendChild(svg)

    const back = '#55646f', flank = '#67757f', dark = '#404d57'
    const L = 100
    const root = el(svg, 'g')

    // Plan view, so the table is half-widths mirrored about the axis rather than back and belly.
    // The shape facts: a conical snout; widest at the pectoral girdle around 26%; a long taper to
    // a very narrow peduncle — narrow is the point, it is what lets the tail beat without dragging
    // the body sideways.
    const half = [
      { x: 0.000, w: 0.008 },
      { x: 0.035, w: 0.030 },
      { x: 0.080, w: 0.055 },
      { x: 0.140, w: 0.076 },
      { x: 0.200, w: 0.088 },
      { x: 0.260, w: 0.092 },   // widest, at the pectoral girdle
      { x: 0.340, w: 0.086 },
      { x: 0.430, w: 0.074 },
      { x: 0.520, w: 0.060 },
      { x: 0.620, w: 0.046 },
      { x: 0.720, w: 0.033 },
      { x: 0.810, w: 0.023 },
      { x: 0.880, w: 0.016 },   // peduncle: very narrow
      { x: 0.940, w: 0.013 },
    ]
    el(root, 'path', { d: fusiform(half.map((s) => ({ x: s.x, back: s.w, belly: s.w })), L), fill: back })

    // Pectorals: long, narrow and swept. They are wings — a shark has no swim bladder, so lift
    // comes from these and from the body. Rooted inside the outline.
    for (const side of [-1, 1]) {
      el(root, 'path', {
        d: `M${(0.5 - 0.24) * L} ${side * 0.070 * L} `
         + `C${(0.5 - 0.30) * L} ${side * 0.150 * L}, ${(0.5 - 0.40) * L} ${side * 0.235 * L}, ${(0.5 - 0.50) * L} ${side * 0.270 * L} `
         + `C${(0.5 - 0.455) * L} ${side * 0.200 * L}, ${(0.5 - 0.375) * L} ${side * 0.120 * L}, ${(0.5 - 0.315) * L} ${side * 0.060 * L} Z`,
        fill: flank,
      })
    }
    // Second dorsal and pelvics, small, further back — their absence is why the first attempt read
    // as a toy.
    for (const side of [-1, 1]) {
      el(root, 'path', {
        d: `M${(0.5 - 0.56) * L} ${side * 0.052 * L} C${(0.5 - 0.60) * L} ${side * 0.090 * L}, ${(0.5 - 0.64) * L} ${side * 0.105 * L}, ${(0.5 - 0.67) * L} ${side * 0.100 * L} C${(0.5 - 0.63) * L} ${side * 0.070 * L}, ${(0.5 - 0.60) * L} ${side * 0.048 * L}, ${(0.5 - 0.59) * L} ${side * 0.042 * L} Z`,
        fill: flank,
      })
    }
    // First dorsal, seen from above: a narrow blade on the midline, base at ~30-42%.
    el(root, 'path', {
      d: `M${(0.5 - 0.295) * L} ${-0.020 * L} `
       + `C${(0.5 - 0.35) * L} ${-0.021 * L}, ${(0.5 - 0.40) * L} ${-0.015 * L}, ${(0.5 - 0.445) * L} ${-0.005 * L} `
       + `L${(0.5 - 0.455) * L} ${0} L${(0.5 - 0.445) * L} ${0.005 * L} `
       + `C${(0.5 - 0.40) * L} ${0.015 * L}, ${(0.5 - 0.35) * L} ${0.021 * L}, ${(0.5 - 0.295) * L} ${0.020 * L} Z`,
      fill: dark,
    })
    // Eyes at the widest part of the head, and five gill slits ahead of the pectorals.
    for (const side of [-1, 1]) {
      el(root, 'circle', { cx: (0.5 - 0.105) * L, cy: side * 0.055 * L, r: 1.15, fill: '#131b21' })
      for (let i = 0; i < 5; i++) {
        const x = 0.165 + i * 0.028
        const s = half.reduce((a, b) => (Math.abs(b.x - x) < Math.abs(a.x - x) ? b : a))
        el(root, 'path', {
          d: `M${(0.5 - x) * L} ${side * s.w * L * 0.94} C${(0.5 - x - 0.012) * L} ${side * s.w * L * 0.66}, ${(0.5 - x - 0.012) * L} ${side * s.w * L * 0.40}, ${(0.5 - x) * L} ${side * s.w * L * 0.22}`,
          fill: 'none', stroke: dark, 'stroke-width': 0.7,
        })
      }
    }

    // The wave lives in the rear third — thunniform, not anguilliform. The head barely moves, and
    // that restraint is the difference between a shark and an eel.
    const tail = spine(root, [
      { pivotX: (0.5 - 0.66) * L, pivotY: 0 },
      { pivotX: (0.5 - 0.84) * L, pivotY: 0 },
    ], 'swimTailSideways', 1.35, 0.10)

    const stock = [
      { x: 0.60, w: 0.050 },
      { x: 0.70, w: 0.036 },
      { x: 0.80, w: 0.024 },
      { x: 0.86, w: 0.019 },
      { x: 0.92, w: 0.017 },
    ]
    el(tail[0], 'path', { d: fusiform(stock.map((s) => ({ x: s.x, back: s.w, belly: s.w })), L), fill: back })

    // Caudal fin FROM ABOVE. This is the whole lesson of the bestiary: a cetacean's fluke is a
    // broad horizontal wing and fills this view, while a shark's caudal fin is a vertical blade and
    // is nearly edge-on here — a narrow leaf, not a fan. Drawn as a fan it would be a dolphin.
    el(tail[1], 'path', {
      d: `M${(0.5 - 0.80) * L} ${-0.024 * L} `                                  // root buried in the stock
       + `C${(0.5 - 0.92) * L} ${-0.026 * L}, ${(0.5 - 1.02) * L} ${-0.024 * L}, ${(0.5 - 1.10) * L} ${-0.017 * L} `
       + `C${(0.5 - 1.14) * L} ${-0.009 * L}, ${(0.5 - 1.14) * L} ${0.009 * L}, ${(0.5 - 1.10) * L} ${0.017 * L} `
       + `C${(0.5 - 1.02) * L} ${0.024 * L}, ${(0.5 - 0.92) * L} ${0.026 * L}, ${(0.5 - 0.80) * L} ${0.024 * L} Z`,
      fill: back,
    })
  },
})

creature({
  id: 'turtle',
  title: 'Green sea turtle',
  latin: 'Chelonia mydas',
  view: 'profile — the stroke is vertical, as with the cetaceans',
  mechanism: 'UNDERWATER FLIGHT · flippers flap like wings · rigid shell: the body does not undulate',
  build(host) {
    const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
    svg.setAttribute('viewBox', '-64 -40 128 80')
    svg.setAttribute('class', 'mini')
    host.appendChild(svg)

    // Built by running the method from a blank page, to test whether the method works. Phase 1's
    // sheet, filled before anything was drawn:
    //
    //   MECHANISM   The fore flippers FLAP like wings — "underwater flight". They are the whole of
    //               the thrust. The rear flippers steer and stabilise; they barely move.
    //   PHASES      FIVE stages, not four. The stroke is a closed loop with a "sweep" in which the
    //               flipper tip travels in toward the centre of the shell — a clapping motion —
    //               rather than a simple up-and-down arc.
    //   ASYMMETRY   Thrust occurs almost ENTIRELY on the downstroke. More extreme than a bird's.
    //   CHANGES     The flipper sweeps INWARD as well as down, so the stroke is a loop in two axes.
    //   PROPORTIONS Carapace width is 76-82% of its length. Adult shell strongly vaulted. Margin
    //               emarginate over the neck and fore flippers, DEEPLY emarginate over the rear
    //               ones. Head small relative to the body.
    //   MARKS       Heart-shaped shell with scutes; ONE visible claw on the outer edge of each
    //               flipper; long paddle fore flippers.
    //   UNKNOWN     Flipper length as a fraction of straight carapace length was not found. The
    //               value used here is set by eye and is flagged as such rather than presented as
    //               measured.
    //
    // The one fact that shapes everything: THE SHELL IS RIGID. Where the dolphin's body carries a
    // travelling wave, this animal's does not move at all — only the limbs work. Giving a turtle a
    // dolphin's body wave would be the same class of error as giving a shark a cetacean's fluke.

    const shell = '#4a5f43', shellDark = '#3b4d36', scute = '#5c7152'
    const skin = '#6b7f63', plastron = '#c9c48d'
    const L = 100

    const root = el(svg, 'g')
    root.style.transformBox = 'view-box'
    root.style.transformOrigin = '0px 0px'
    // A shallow heave only — the thrust moves the animal, but nothing in it flexes.
    root.style.animation = 'turtleHeave 2.6s ease-in-out infinite'

    // FAR flipper first, behind the body, lagging slightly.
    flipper(root, -0.10, '#42553c', 0.85)

    // Rear flipper: small, held out as a rudder, with only a slight trim adjustment. Drawn before
    // the shell so its root is covered — the midline case of the join rule.
    const rear = el(root, 'g')
    rear.style.transformBox = 'view-box'
    rear.style.transformOrigin = `${(0.5 - 0.80) * L}px ${0.07 * L}px`
    rear.style.animation = 'turtleRudder 2.6s ease-in-out infinite'
    el(rear, 'path', {
      d: `M${(0.5 - 0.74) * L} ${0.055 * L} `
       + `C${(0.5 - 0.83) * L} ${0.105 * L}, ${(0.5 - 0.93) * L} ${0.135 * L}, ${(0.5 - 1.00) * L} ${0.130 * L} `
       + `C${(0.5 - 0.97) * L} ${0.095 * L}, ${(0.5 - 0.88) * L} ${0.055 * L}, ${(0.5 - 0.78) * L} ${0.020 * L} Z`,
      fill: skin,
    })

    // Neck and head: SMALL, which is diagnostic. Drawn before the shell so the neck's root is
    // covered by it.
    el(root, 'path', {
      d: `M${(0.5 - 0.16) * L} ${-0.030 * L} `
       + `C${(0.5 - 0.08) * L} ${-0.070 * L}, ${(0.5 - 0.02) * L} ${-0.080 * L}, ${(0.5 + 0.02) * L} ${-0.068 * L} `
       + `C${(0.5 + 0.05) * L} ${-0.050 * L}, ${(0.5 + 0.052) * L} ${-0.020 * L}, ${(0.5 + 0.03) * L} ${-0.002 * L} `
       + `C${(0.5 - 0.02) * L} ${0.018 * L}, ${(0.5 - 0.10) * L} ${0.020 * L}, ${(0.5 - 0.16) * L} ${0.010 * L} Z`,
      fill: skin,
    })
    el(root, 'circle', { cx: (0.5 + 0.012) * L, cy: -0.042 * L, r: 1.15, fill: '#13180f' })
    // Beak: short and blunt. A green turtle's jaw is serrated, not hooked — a hooked beak is a
    // hawksbill, which is the neighbour this must not be mistaken for.
    el(root, 'path', {
      d: `M${(0.5 + 0.048) * L} ${-0.028 * L} C${(0.5 + 0.062) * L} ${-0.020 * L}, ${(0.5 + 0.062) * L} ${-0.006 * L}, ${(0.5 + 0.046) * L} ${0} Z`,
      fill: '#8b8f5f',
    })

    // The CARAPACE, from a profile table. Vaulted: the crown sits a little forward of centre, and
    // the margin dips over the neck and again, deeply, over the rear flippers.
    const carapace = [
      { x: 0.000, back: 0.020, belly: 0.020 },   // front margin, over the neck
      { x: 0.060, back: 0.090, belly: 0.048 },
      { x: 0.150, back: 0.140, belly: 0.078 },
      { x: 0.260, back: 0.168, belly: 0.096 },
      { x: 0.380, back: 0.176, belly: 0.104 },   // crown, forward of centre
      { x: 0.500, back: 0.170, belly: 0.100 },
      { x: 0.620, back: 0.152, belly: 0.090 },
      { x: 0.740, back: 0.120, belly: 0.072 },
      { x: 0.850, back: 0.082, belly: 0.050 },
      { x: 0.930, back: 0.048, belly: 0.030 },
      { x: 0.985, back: 0.018, belly: 0.014 },   // rear margin
    ]
    el(root, 'path', { d: fusiform(carapace, L), fill: shell })

    // Plastron: the pale underside. From the same table, tapering at both ends.
    const taper = (x) => Math.min(1, Math.max(0, Math.min((x - 0.04) / 0.16, (0.94 - x) / 0.18)))
    el(root, 'path', {
      d: fusiform(carapace.map((s) => ({
        x: s.x,
        back: -s.belly * 0.55 * taper(s.x),
        belly: s.belly * 0.96 * taper(s.x),
      })), L),
      fill: plastron, opacity: 0.9,
    })

    // Scutes: four pairs of costals plus the vertebral row. Drawn as seams rather than filled
    // shapes — they read at size and cost four strokes.
    for (let i = 1; i <= 4; i++) {
      const x = 0.13 + i * 0.165
      const s = carapace.reduce((a, b) => (Math.abs(b.x - x) < Math.abs(a.x - x) ? b : a))
      el(root, 'path', {
        d: `M${(0.5 - x) * L} ${-s.back * L * 0.98} C${(0.5 - x - 0.02) * L} ${-s.back * L * 0.55}, ${(0.5 - x - 0.025) * L} ${-s.back * L * 0.2}, ${(0.5 - x - 0.02) * L} ${s.belly * L * 0.18}`,
        fill: 'none', stroke: shellDark, 'stroke-width': 0.8, opacity: 0.55,
      })
    }
    // The vertebral ridge: one long seam along the crown.
    el(root, 'path', {
      d: 'M' + carapace.filter((s) => s.x > 0.05 && s.x < 0.95)
        .map((s) => `${((0.5 - s.x) * L).toFixed(1)} ${(-s.back * L * 0.62).toFixed(1)}`).join(' L'),
      fill: 'none', stroke: scute, 'stroke-width': 1.1, opacity: 0.6,
    })

    // NEAR flipper last, over the shell.
    flipper(root, 0, skin, 1)

    function flipper(parent, lag, fill, opacity) {
      // Shoulder sits at the front margin, low. Two segments as with the wing — upper arm and the
      // paddle — because the sweep is a fold plus a rotation, not one rotation.
      const shoulder = el(parent, 'g', { opacity })
      shoulder.style.transformBox = 'view-box'
      shoulder.style.transformOrigin = `${(0.5 - 0.19) * L}px ${0.045 * L}px`
      shoulder.style.animation = `turtleStroke 2.6s cubic-bezier(.3,0,.35,1) ${(lag * 2.6).toFixed(2)}s infinite`

      const wrist = el(shoulder, 'g')
      wrist.style.transformBox = 'view-box'
      wrist.style.transformOrigin = `${(0.5 - 0.32) * L}px ${0.115 * L}px`
      // The sweep: the tip travels IN toward the shell as well as up. Lagging the shoulder gives
      // the closed loop the research describes, instead of a flat arc.
      wrist.style.animation = `turtleSweep 2.6s cubic-bezier(.3,0,.35,1) ${((lag - 0.14) * 2.6).toFixed(2)}s infinite`

      // The paddle: long, broad, bluntly rounded, with a single claw on the leading edge — the
      // recognition mark from the sheet, and one path.
      el(wrist, 'path', {
        d: `M${(0.5 - 0.27) * L} ${0.080 * L} `
         + `C${(0.5 - 0.36) * L} ${0.135 * L}, ${(0.5 - 0.47) * L} ${0.205 * L}, ${(0.5 - 0.58) * L} ${0.250 * L} `
         + `C${(0.5 - 0.625) * L} ${0.266 * L}, ${(0.5 - 0.655) * L} ${0.250 * L}, ${(0.5 - 0.635) * L} ${0.220 * L} `
         + `C${(0.5 - 0.55) * L} ${0.170 * L}, ${(0.5 - 0.42) * L} ${0.110 * L}, ${(0.5 - 0.30) * L} ${0.048 * L} Z`,
        fill,
      })
      el(wrist, 'path', {
        d: `M${(0.5 - 0.60) * L} ${0.243 * L} L${(0.5 - 0.645) * L} ${0.232 * L} L${(0.5 - 0.615) * L} ${0.222 * L} Z`,
        fill: '#c9c48d',
      })

      // Upper arm, drawn over the paddle's root: the flipper is one colour, so the buried case of
      // the join rule applies and there is nothing to blend.
      el(shoulder, 'path', {
        d: `M${(0.5 - 0.155) * L} ${0.020 * L} `
         + `C${(0.5 - 0.24) * L} ${0.060 * L}, ${(0.5 - 0.31) * L} ${0.110 * L}, ${(0.5 - 0.345) * L} ${0.140 * L} `
         + `C${(0.5 - 0.315) * L} ${0.160 * L}, ${(0.5 - 0.26) * L} ${0.130 * L}, ${(0.5 - 0.20) * L} ${0.090 * L} `
         + `C${(0.5 - 0.175) * L} ${0.070 * L}, ${(0.5 - 0.16) * L} ${0.048 * L}, ${(0.5 - 0.155) * L} ${0.020 * L} Z`,
        fill,
      })
    }
  },
})

creature({
  id: 'walker',
  title: 'Walking figure',
  latin: 'gait cycle · Homo sapiens',
  view: 'profile — the sagittal plane is where a gait cycle is defined and measured',
  mechanism: 'stance 60% / swing 40% · hip, knee and ankle driven from published joint angles',
  build(host) {
    const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
    svg.setAttribute('viewBox', '-50 -8 100 108')
    svg.setAttribute('class', 'mini')
    host.appendChild(svg)

    // Built to SIMULATE the method's newest additions — the anchor map (1b), the kinematics sheet
    // (1c) and the depth order (1d) — on an object no part of this research had touched. A walking
    // human is the hardest available test: everyone knows what walking looks like, so an error is
    // not subtle.
    //
    // ── 1b ANCHOR MAP, in fractions of standing height H, measured from the ground ──
    //   shoulder 0.82  ·  hip 0.53  ·  knee 0.28  ·  ankle 0.04
    //   thigh = 0.25 H   shank = 0.24 H   foot ≈ 0.15 H long
    //   shoulder width 0.25 H   arm 0.44 H   head 0.13 H
    //
    // ── 1c KINEMATICS, from published gait analysis ──
    //   stance 60% / swing 40% — the asymmetry is a measured number, not a feel
    //   sub-phases: loading response 1-10 · mid-stance 11-30 · terminal stance 31-50 ·
    //               pre-swing 51-60 · initial swing 61-73 · mid-swing 74-87 · terminal swing 88-100
    //   initial contact  hip flexed, knee near full extension, ankle neutral
    //   terminal stance  hip 20 deg EXTENSION, knee neutral, ankle 5-10 deg dorsiflexion
    //   pre-swing        hip 20 deg ext -> neutral, knee neutral -> 40 deg flexion,
    //                    ankle 10 deg dorsi -> 20 deg plantarflexion
    //   terminal swing   hip 20 deg flexion, knee 30 deg flexion -> neutral, ankle neutral
    //   knee peaks near 60 deg in mid-swing — the one value taken from general knowledge rather
    //   than from the sources read here, and flagged as such
    //   the two legs are exactly half a cycle apart; arms swing CONTRALATERALLY
    //   the pelvis rises and falls TWICE per cycle, peaking at each mid-stance
    //
    // ── 1d DEPTH ORDER ──
    //   far leg · far arm · torso · head · near leg · near arm
    //
    // Signs: SVG rotation is clockwise-positive. The figure faces +x and limbs hang toward +y, so
    // hip FLEXION (thigh forward) is NEGATIVE and extension positive. Getting this wrong is the
    // error that inverted the bird and the turtle; here it was written down before any keyframe.

    const H = 100
    const skin = '#c69a76', cloth = '#3f5a72', clothDark = '#33495c', shoe = '#26313c'
    const hipY = (1 - 0.53) * H, kneeLen = 0.25 * H, shankLen = 0.24 * H

    // Ground line, drawn first. A gait cycle cannot be judged without a floor: the entire cycle is
    // defined by when and where the foot meets it. Rendering the figure against nothing was a real
    // defect of the first pass, not a presentational choice.
    el(svg, 'line', {
      x1: -50, y1: H - 0.5, x2: 50, y2: H - 0.5,
      stroke: '#9db3c4', 'stroke-width': 0.8,
    })

    const root = el(svg, 'g')
    root.style.transformBox = 'view-box'
    root.style.transformOrigin = `0px ${hipY}px`
    root.style.animation = 'gaitBob 1.1s ease-in-out infinite'

    // One leg. `phase` shifts it half a cycle for the far side; `depth` dims and de-saturates it,
    // which is the cheapest possible aerial perspective and enough at this size.
    function leg(parent, phase, fill, shoeFill, opacity) {
      const thigh = el(parent, 'g', { opacity })
      thigh.style.transformBox = 'view-box'
      thigh.style.transformOrigin = `0px ${hipY}px`
      thigh.style.animation = `gaitHip 1.1s linear ${phase}s infinite`
      el(thigh, 'path', {
        d: `M-4.5 ${hipY - 1} L4.5 ${hipY - 1} L3.4 ${hipY + kneeLen} L-3.4 ${hipY + kneeLen} Z`,
        fill, 'stroke-linejoin': 'round',
      })

      const shank = el(thigh, 'g')
      shank.style.transformBox = 'view-box'
      shank.style.transformOrigin = `0px ${hipY + kneeLen}px`
      shank.style.animation = `gaitKnee 1.1s linear ${phase}s infinite`
      el(shank, 'path', {
        d: `M-3.4 ${hipY + kneeLen} L3.4 ${hipY + kneeLen} L2.5 ${hipY + kneeLen + shankLen} L-2.5 ${hipY + kneeLen + shankLen} Z`,
        fill, 'stroke-linejoin': 'round',
      })

      const foot = el(shank, 'g')
      foot.style.transformBox = 'view-box'
      foot.style.transformOrigin = `0px ${hipY + kneeLen + shankLen}px`
      foot.style.animation = `gaitAnkle 1.1s linear ${phase}s infinite`
      el(foot, 'path', {
        d: `M-3 ${hipY + kneeLen + shankLen - 2} L2.4 ${hipY + kneeLen + shankLen - 2} `
         + `L11 ${hipY + kneeLen + shankLen + 2.6} L11 ${hipY + kneeLen + shankLen + 4} `
         + `L-3.6 ${hipY + kneeLen + shankLen + 4} Z`,
        fill: shoeFill,
      })
    }

    // One arm. Contralateral: it carries the opposite leg's phase.
    function arm(parent, phase, fill, opacity) {
      const shoulderY = (1 - 0.82) * H
      const upper = el(parent, 'g', { opacity })
      upper.style.transformBox = 'view-box'
      upper.style.transformOrigin = `0px ${shoulderY}px`
      upper.style.animation = `gaitShoulder 1.1s linear ${phase}s infinite`
      el(upper, 'path', {
        d: `M-3 ${shoulderY} L3 ${shoulderY} L2.3 ${shoulderY + 0.19 * H} L-2.3 ${shoulderY + 0.19 * H} Z`,
        fill,
      })
      const fore = el(upper, 'g')
      fore.style.transformBox = 'view-box'
      fore.style.transformOrigin = `0px ${shoulderY + 0.19 * H}px`
      fore.style.animation = `gaitElbow 1.1s linear ${phase}s infinite`
      el(fore, 'path', {
        d: `M-2.3 ${shoulderY + 0.19 * H} L2.3 ${shoulderY + 0.19 * H} L1.9 ${shoulderY + 0.36 * H} L-1.9 ${shoulderY + 0.36 * H} Z`,
        fill,
      })
      el(fore, 'circle', { cx: 0, cy: shoulderY + 0.375 * H, r: 2.6, fill: skin })
    }

    // 1d depth order, drawn in sequence.
    leg(root, -0.55, '#33495c', '#1c242c', 0.75)      // far leg, half a cycle behind
    arm(root, 0, '#2c4055', 0.7)                       // far arm, contralateral to the far leg

    // Torso: shoulders back, pelvis forward, with a slight forward lean — a walker's trunk is not
    // vertical.
    const torso = el(root, 'g')
    torso.style.transformBox = 'view-box'
    torso.style.transformOrigin = `0px ${hipY}px`
    torso.style.animation = 'gaitTrunk 1.1s ease-in-out infinite'
    el(torso, 'path', {
      d: `M-7 ${hipY + 2} L7 ${hipY + 2} L8.5 ${(1 - 0.75) * H} L7.5 ${(1 - 0.83) * H} `
       + `L-7.5 ${(1 - 0.83) * H} L-8 ${(1 - 0.75) * H} Z`,
      fill: cloth,
    })
    // Neck and head. Head is 0.13 H; a head drawn larger is the single most common proportion error
    // in a walking figure.
    el(torso, 'rect', { x: -2.2, y: (1 - 0.855) * H, width: 4.4, height: 0.035 * H, fill: skin })
    el(torso, 'ellipse', { cx: 1.2, cy: (1 - 0.925) * H, rx: 0.048 * H, ry: 0.062 * H, fill: skin })
    el(torso, 'path', {
      d: `M${-0.048 * H + 1.2} ${(1 - 0.955) * H} A ${0.048 * H} ${0.062 * H} 0 0 1 ${0.048 * H + 1.2} ${(1 - 0.95) * H} `
       + `L${0.04 * H + 1.2} ${(1 - 0.925) * H} L${-0.048 * H + 1.2} ${(1 - 0.925) * H} Z`,
      fill: '#4a3a2e',
    })

    leg(root, 0, cloth, shoe, 1)                       // near leg
    // The near arm was the torso's exact colour and disappeared into it — only the hand read.
    // A sleeve one step lighter separates it, which is also what a real garment does under light
    // from above.
    arm(root, -0.55, '#51708c', 1)                     // near arm, contralateral to the near leg
  },
})

// ── The primitives themselves, each as a self-contained loop ────────────────
// The scenes are compositions; these are the parts. Rendered live so the vocabulary can be seen
// rather than read — a reader who has watched `sway` next to `oscillate` never confuses them again.
const primitives = [
  { id: 'oscillate', channel: 'transform', build: (s) => dot(s, 'oscillateK 2.4s ease-in-out infinite alternate') },
  { id: 'sway', channel: 'rotate about a base', build: swayDemo },
  { id: 'drift', channel: 'transform', build: (s) => dot(s, 'driftK 3.4s linear infinite alternate') },
  { id: 'float', channel: 'transform', build: (s) => dot(s, 'floatK 3s ease-in-out infinite alternate') },
  { id: 'breathe', channel: 'scale', build: (s) => dot(s, 'breathe 3.2s ease-in-out infinite') },
  { id: 'pulse', channel: 'opacity', build: (s) => dot(s, 'pulseK 0.9s ease-out infinite') },
  { id: 'flicker', channel: 'opacity, irregular', build: (s) => dot(s, 'flickerK 1.7s steps(1) infinite') },
  { id: 'orbit', channel: 'rotate a group', build: orbitDemo },
  { id: 'ripple', channel: 'scale + opacity', build: rippleDemo },
  { id: 'draw', channel: 'stroke-dashoffset', build: drawDemo },
  { id: 'wave', channel: 'translate a tile', build: waveDemo },
  { id: 'stagger', channel: 'negative delay', build: staggerDemo },
]

function miniSvg(stage) {
  const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
  svg.setAttribute('viewBox', '0 0 100 60')
  svg.setAttribute('class', 'mini')
  stage.appendChild(svg)
  return svg
}
function dot(stage, animation) {
  const svg = miniSvg(stage)
  const c = el(svg, 'circle', { cx: 50, cy: 30, r: 9, fill: 'currentColor' })
  c.style.animation = animation
  return svg
}
function swayDemo(stage) {
  const svg = miniSvg(stage)
  const g = el(svg, 'g')
  g.style.transformBox = 'view-box'
  g.style.transformOrigin = '50px 54px'          // the joint, not the centre
  g.style.animation = 'swayK 2.6s ease-in-out infinite alternate'
  el(g, 'line', { x1: 50, y1: 54, x2: 50, y2: 12, stroke: 'currentColor', 'stroke-width': 3, 'stroke-linecap': 'round' })
  el(g, 'circle', { cx: 50, cy: 12, r: 5, fill: 'currentColor' })
}
function orbitDemo(stage) {
  const svg = miniSvg(stage)
  el(svg, 'circle', { cx: 50, cy: 30, r: 5, fill: 'currentColor', opacity: 0.45 })
  const g = el(svg, 'g')
  g.style.transformBox = 'view-box'
  g.style.transformOrigin = '50px 30px'
  g.style.animation = 'spin 3s linear infinite'
  el(g, 'circle', { cx: 70, cy: 30, r: 3.5, fill: 'currentColor' })
}
function rippleDemo(stage) {
  const svg = miniSvg(stage)
  for (let i = 0; i < 3; i++) {
    const r = el(svg, 'circle', { cx: 50, cy: 30, r: 6, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.6 })
    r.style.animation = `rippleK 2.4s ease-out ${-i * 0.8}s infinite`
  }
}
function drawDemo(stage) {
  const svg = miniSvg(stage)
  const p = el(svg, 'path', {
    d: 'M12 44 C 30 8, 48 52, 64 22 S 84 12, 90 26',
    fill: 'none', stroke: 'currentColor', 'stroke-width': 2.4, 'stroke-linecap': 'round',
  })
  // The technique in one line: dash the path by its own length, then animate the offset to zero.
  const length = p.getTotalLength ? p.getTotalLength() : 120
  p.style.setProperty('--length', length)
  p.style.strokeDasharray = length
  p.style.animation = 'drawK 2.8s ease-in-out infinite'
}
function waveDemo(stage) {
  const svg = miniSvg(stage)
  svg.setAttribute('viewBox', '0 0 200 60')
  svg.setAttribute('preserveAspectRatio', 'none')
  svg.style.width = '200%'
  svg.style.animation = 'roll 3.4s linear infinite'
  let d = 'M0 60 L0 34'
  for (let i = 0; i <= 80; i++) {
    const x = (i / 80) * 200
    const u = (x / 200) * Math.PI * 2
    d += ` L${x.toFixed(1)} ${(34 + Math.sin(u * 3) * 7 + Math.sin(u * 7) * 2.5).toFixed(2)}`
  }
  el(svg, 'path', { d: `${d} L200 60 Z`, fill: 'currentColor', opacity: 0.75 })
}
function staggerDemo(stage) {
  const svg = miniSvg(stage)
  for (let i = 0; i < 7; i++) {
    const bar = el(svg, 'rect', { x: 10 + i * 12, y: 20, width: 6, height: 20, rx: 2, fill: 'currentColor' })
    bar.style.transformBox = 'view-box'
    bar.style.transformOrigin = `${13 + i * 12}px 40px`
    // The whole of stagger: a negative delay proportional to the index.
    bar.style.animation = `barK 1.3s ease-in-out ${-(i / 7) * 1.3}s infinite alternate`
  }
}

/** The stylesheet every scene above depends on. Kept here so there is one definition of it. */
const sceneCss = `
  .stage { position: relative; overflow: hidden; }
  /* SVG's initial transform-origin is 0 0 — NOT 50% 50% as it is for HTML boxes. A scale() or
     rotate() on an SVG child therefore moves it as well as transforming it, which is how the sun's
     halo ended up offset from the sun the first time these scenes were rendered. transform-box:
     fill-box makes percentage origins resolve against the element's own bounding box, restoring
     the behaviour every author already expects. */
  .stage svg circle, .stage svg ellipse, .stage svg path, .stage svg rect, .stage svg g {
    transform-box: fill-box;
    transform-origin: center;
  }
  .stage .layer { position: absolute; inset: 0; height: 100%; will-change: transform; }
  /* object-fit: cover makes a <canvas> map its bitmap the way preserveAspectRatio="xMidYMid slice"
     maps an SVG viewBox. Without it the canvas stretches while an SVG overlay crops, the two use
     different mappings, and every marker drifts off the thing it marks — measured by looking at the
     first render of the feldt plate. */
  .stage .canvasLayer { width: 100%; height: 100%; object-fit: cover; }
  .stage .bird { position: absolute; offset-rotate: auto; offset-distance: 0%;
    transform: scale(var(--scale, 1)); transform-origin: center; will-change: offset-distance; }
  .stage .flash { position: absolute; inset: 0; background: #dce8ff; opacity: 0;
    pointer-events: none; }

  @keyframes drift  { from { transform: translateX(0);   } to { transform: translateX(-50%); } }
  @keyframes roll   { from { transform: translateX(0);   } to { transform: translateX(-50%); } }
  @keyframes spin   { from { transform: rotate(0deg);    } to { transform: rotate(360deg);   } }
  @keyframes twinkle{ 0%,100% { opacity: .18 } 50% { opacity: .95 } }
  @keyframes breathe{ 0%,100% { transform: scale(1) } 50% { transform: scale(1.07) } }
  @keyframes glint  { 0%,100% { opacity: .12; transform: scaleX(.7) } 50% { opacity: .7; transform: scaleX(1.15) } }
  @keyframes fly    { from { offset-distance: 0% } to { offset-distance: 100% } }
  /* The wingbeat, in four phases rather than two, and deliberately asymmetric in time.
     0%   top of the upstroke, wing high and folded
     18%  the fast, powerful downstroke begins — down AND forward, arm extending
     46%  bottom of the downstroke, fully extended: this is where the span is longest
     62%  recovery starts: up and back, and the elbow begins to fold
     100% back to the top, folded
     The downstroke occupies less of the cycle than the recovery, which is the asymmetry the
     research describes. The elbow curves are not a copy of the shoulder's: the hand folds hardest
     mid-upstroke, which is what shortens the span exactly when drag would otherwise be paid. */
  /* The wingbeat, in four phases and deliberately asymmetric in time. In profile, both wings
     swing the same way, so there is one pair of curves rather than a mirrored set.
       0%   top of the upstroke: wing high, and folded
       20%  the downstroke begins — fast, powerful, arm extending as it goes down and forward
       48%  bottom of the downstroke, fully extended: the span is longest here
       64%  recovery begins: up and back, and the elbow starts to fold
       100% back to the top, folded
     The downstroke occupies less of the cycle than the recovery, which is the asymmetry the
     research describes. The hand's curve is not a copy of the arm's: it folds hardest through the
     upstroke, which is what shortens the span exactly when drag would otherwise be paid. */
  @keyframes wingArm {
    0%   { transform: rotate(52deg) translateX(0) }
    20%  { transform: rotate(44deg) translateX(0.4px) }
    48%  { transform: rotate(-62deg) translateX(1.6px) }
    64%  { transform: rotate(-30deg) translateX(0.6px) }
    100% { transform: rotate(52deg) translateX(0) }
  }
  @keyframes wingHand {
    0%   { transform: rotate(-31deg) }
    20%  { transform: rotate(-11deg) }
    48%  { transform: rotate(14deg) }
    64%  { transform: rotate(-26deg) }
    100% { transform: rotate(-31deg) }
  }
  @keyframes flashPulse { 0% { opacity: 0 } 12% { opacity: .5 } 100% { opacity: 0 } }
  @keyframes leafFall {
    from { transform: translate(var(--x0, 400px), 240px) rotate(0deg); opacity: 0 }
    12%  { opacity: .95 }
    to   { transform: translate(calc(var(--x0, 400px) - 300px), 660px) rotate(520deg); opacity: 0 }
  }
  @keyframes sway0 { from { transform: rotate(-0.7deg) } to { transform: rotate(0.7deg) } }
  @keyframes sway1 { from { transform: rotate(-1.5deg) } to { transform: rotate(1.5deg) } }
  @keyframes sway2 { from { transform: rotate(-2.6deg) } to { transform: rotate(2.6deg) } }
  @keyframes sway3 { from { transform: rotate(-3.8deg) } to { transform: rotate(3.8deg) } }
  @keyframes sway4 { from { transform: rotate(-5.2deg) } to { transform: rotate(5.2deg) } }

  /* Primitive demos */
  .mini { width: 100%; height: 100%; display: block; }
  @keyframes oscillateK { from { transform: translateX(-22px) } to { transform: translateX(22px) } }
  @keyframes driftK   { from { transform: translateX(-40px) } to { transform: translateX(40px) } }
  @keyframes floatK   { from { transform: translateY(9px) } to { transform: translateY(-9px) } }
  @keyframes pulseK   { 0% { opacity: 1; transform: scale(1) } 70%,100% { opacity: .15; transform: scale(1.5) } }
  @keyframes flickerK { 0%,100% { opacity: 1 } 12% { opacity: .25 } 19% { opacity: .9 } 47% { opacity: .35 } 52% { opacity: 1 } 71% { opacity: .5 } }
  @keyframes swayK    { from { transform: rotate(-13deg) } to { transform: rotate(13deg) } }
  @keyframes rippleK  { from { transform: scale(.3); opacity: .9 } to { transform: scale(2.6); opacity: 0 } }
  @keyframes drawK    { 0% { stroke-dashoffset: var(--length) } 55%,100% { stroke-dashoffset: 0 } }
  @keyframes barK     { from { transform: scaleY(.35) } to { transform: scaleY(1) } }

  /* Feldt */
  .stage .feldtMotion { position: absolute; inset: 0; }
  /* width: 100% is not optional here. An <svg> with inset:0 but no width falls back to the
     intrinsic width of its viewBox ratio — measured at 984px against a 1200px stage — and every
     overlay mark lands beside the thing it marks instead of on it. */
  .stage .feldtMotion .layer { position: absolute; inset: 0; width: 100%; height: 100%; }
  /* Each moving mark is promoted to its own element: the transform then lands on an HTML-level box
     instead of on a child of a shared <svg>, which is the difference between 37 layout/s and 0
     (prototypes 20 vs 21). overflow: visible so a ripple can expand past its own box. */
  .stage .feldtMotion .mark { position: absolute; overflow: visible; will-change: transform; }
  .stage.motionOff .feldtMotion { display: none; }
  .stage .feldtToggle {
    position: absolute; right: 10px; bottom: 10px; z-index: 5;
    font: 11px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
    color: #cfe1ff; background: rgba(9, 18, 32, 0.82); border: 1px solid rgba(159, 210, 234, 0.35);
    border-radius: 3px; padding: 7px 10px; cursor: pointer;
  }
  .stage .feldtToggle:focus-visible { outline: 2px solid #9fd2ea; outline-offset: 2px; }

  /* Creatures */
  @keyframes swimHeave        { 0%,100% { transform: translateY(-2.5px) } 50% { transform: translateY(2.5px) } }
  /* Cetacean: the fluke sweeps UP and DOWN. */
  @keyframes swimFlukeUpDown  { 0%,100% { transform: rotate(-13deg) } 50% { transform: rotate(13deg) } }
  /* Shark, seen from above: the same rotation, but it is a LATERAL sweep. Identical maths,
     opposite plane — which is exactly why the view has to be chosen by the mechanism. */
  /* Thunniform swimming: the amplitude is SMALL along the body and only the fin tip travels far.
     Driving every segment at the same large angle bent the peduncle into a fork — visible the
     moment the animal was rendered large. */
  @keyframes swimTailSideways { 0%,100% { transform: rotate(-8deg) } 50% { transform: rotate(8deg) } }
  @keyframes whalePectoral    { 0%,100% { transform: rotate(-7deg) } 50% { transform: rotate(9deg) } }

  /* Gait cycle. Every stop below is a published number, placed at its published percentage — this
     is the first figure in this directory whose keyframes were transcribed rather than guessed.
     Sign convention, fixed before writing any of them: hip flexion (thigh forward) is NEGATIVE. */
  @keyframes gaitHip {
    0%   { transform: rotate(-25deg) }   /* initial contact: hip flexed */
    10%  { transform: rotate(-20deg) }   /* loading response */
    30%  { transform: rotate(-6deg) }    /* mid-stance: passing under the body */
    50%  { transform: rotate(20deg) }    /* terminal stance: 20 deg EXTENSION */
    60%  { transform: rotate(12deg) }    /* pre-swing / toe off */
    73%  { transform: rotate(-14deg) }   /* initial swing */
    87%  { transform: rotate(-25deg) }   /* mid to terminal swing: 20-25 deg flexion */
    100% { transform: rotate(-25deg) }
  }
  @keyframes gaitKnee {
    0%   { transform: rotate(-4deg) }    /* near full extension at contact */
    10%  { transform: rotate(-18deg) }   /* loading response absorbs — the "knee dip" */
    30%  { transform: rotate(-6deg) }
    50%  { transform: rotate(-4deg) }    /* terminal stance: neutral */
    60%  { transform: rotate(-40deg) }   /* pre-swing: 40 deg flexion */
    73%  { transform: rotate(-60deg) }   /* mid-swing peak */
    87%  { transform: rotate(-30deg) }   /* terminal swing: extending again */
    100% { transform: rotate(-4deg) }
  }
  @keyframes gaitAnkle {
    0%   { transform: rotate(0deg) }     /* neutral at heel strike */
    10%  { transform: rotate(6deg) }     /* plantarflexion as the foot flattens */
    30%  { transform: rotate(-4deg) }    /* dorsiflexion through mid-stance */
    50%  { transform: rotate(-9deg) }    /* terminal stance: 5-10 deg dorsiflexion */
    60%  { transform: rotate(20deg) }    /* toe off: 20 deg PLANTARflexion */
    73%  { transform: rotate(8deg) }
    87%  { transform: rotate(0deg) }     /* neutral, ready for the next contact */
    100% { transform: rotate(0deg) }
  }
  /* Arms swing contralaterally, with about a third of the leg's amplitude. */
  @keyframes gaitShoulder {
    0%   { transform: rotate(14deg) }
    50%  { transform: rotate(-12deg) }
    100% { transform: rotate(14deg) }
  }
  @keyframes gaitElbow {
    0%   { transform: rotate(-10deg) }
    50%  { transform: rotate(-26deg) }
    100% { transform: rotate(-10deg) }
  }
  /* The pelvis rises and falls TWICE per cycle, peaking at each mid-stance. Animating it once per
     cycle is the classic tell of a figure that was not researched.
     KNOWN DEFECT, kept small rather than hidden: this chain is rooted at the HIP, so when the
     pelvis rises the planted foot rises with it and slides against the ground. In a real gait the
     stance foot is FIXED and the hip moves relative to IT — the hierarchy should be rooted at the
     contact point, which is inverse kinematics rather than a transform chain. The amplitude is
     therefore held to ~1% of height, where the slip is below the noise; a correct version reverses
     the chain for whichever leg is in stance. */
  @keyframes gaitBob {
    0%, 50%, 100% { transform: translateY(0.7px) }
    28%, 78%      { transform: translateY(-0.7px) }
  }
  @keyframes gaitTrunk {
    0%, 50%, 100% { transform: rotate(-1.6deg) }
    25%, 75%      { transform: rotate(-3deg) }
  }

  /* Turtle. FIVE stages, from the kinematics: thrust is almost entirely on the downstroke, so the
     downstroke is short and fast and the recovery is long and slow — a stronger asymmetry than the
     bird's. The shell does not flex at all; only the limbs work. */
  /* Sign was inverted on the first pass — at 0%, which the script calls the top of the recovery,
     the flipper was at the BOTTOM. The frozen-pose strip found it in one look. In this geometry a
     POSITIVE rotation lifts the paddle. The upper bound is also capped: swung further the paddle
     lay across the shell, which a flipper hinged at the shoulder cannot do. */
  @keyframes turtleStroke {
    0%   { transform: rotate(24deg) }    /* top of the recovery, flippers high */
    30%  { transform: rotate(-30deg) }   /* DOWNSTROKE — fast, and where the thrust is */
    45%  { transform: rotate(-34deg) }   /* sweep: the tip travels in toward the shell */
    80%  { transform: rotate(12deg) }    /* upstroke — slow, folded, no thrust */
    95%  { transform: rotate(24deg) }    /* extension back to the top */
    100% { transform: rotate(24deg) }    /* brief glide before the next beat */
  }
  @keyframes turtleSweep {
    0%   { transform: rotate(-20deg) }
    30%  { transform: rotate(8deg) }
    45%  { transform: rotate(22deg) }    /* the clap: paddle swept inward under the shell */
    80%  { transform: rotate(-14deg) }
    100% { transform: rotate(-20deg) }
  }
  @keyframes turtleHeave { 0%,100% { transform: translateY(1.6px) } 35% { transform: translateY(-1.8px) } }
  @keyframes turtleRudder { 0%,100% { transform: rotate(-3deg) } 50% { transform: rotate(3deg) } }

  /* Ferdinand */
  @keyframes swayPalm  { from { transform: rotate(-3.5deg) } to { transform: rotate(3.5deg) } }
  @keyframes sked      { 0% { transform: scale(.35); opacity: .85 } 100% { transform: scale(4.2); opacity: 0 } }
  @keyframes pulseLamp { 0% { opacity: 1 } 22% { opacity: .35 } 100% { opacity: 1 } }
  /* The silent post is marked by a ring that CLOSES on it, not by a signal leaving it. */
  @keyframes silentRing { 0%,100% { transform: scale(1.25); opacity: .16 } 55% { transform: scale(.82); opacity: .95 } }
  @keyframes silentMark { 0%,100% { opacity: .25 } 55% { opacity: 1 } }

`

/* Reduce, do not remove. Travel, parallax and rotation go; the scene keeps breathing so the
   information a moving element carried is not simply deleted. See report.md section 7.
   Held as its own string so the same declarations can serve the real media query AND a manual
   switch, letting a reader see the reduced variant without changing their OS setting. */
const reducedMotionRules = (scope) => `
  ${scope} .layer, ${scope} .bird { animation: none !important; }
  ${scope} g { animation: none !important; }
  ${scope} circle, ${scope} ellipse {
    animation-name: breathe !important;
    animation-duration: 14s !important;
    animation-timing-function: ease-in-out !important;
  }
  ${scope} .flash { animation: none !important; }
  ${scope} canvas { opacity: .45; }
`

const reducedMotionCss = `
  @media (prefers-reduced-motion: reduce) { ${reducedMotionRules('.stage')} }
  :root[data-motion="reduced"] { ${reducedMotionRules('.stage')} }
`

return { scenes, primitives, creatures, sceneCss, reducedMotionCss, seeded }
})()
