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
  title: 'Dolphin',
  latin: 'Tursiops truncatus',
  view: 'profile — the stroke is vertical, so profile is where it shows',
  mechanism: 'dorsoventral oscillation · horizontal fluke · body wave from mid-body back',
  build(host) {
    const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
    svg.setAttribute('viewBox', '-58 -30 116 60')
    svg.setAttribute('class', 'mini')
    host.appendChild(svg)

    const skin = '#4c6076', belly = '#c8d6e2'
    const root = el(svg, 'g')
    // Whole-body rise and fall: a swimming cetacean does not hold its head still while the tail
    // works — the thrust moves the entire animal.
    root.style.transformBox = 'view-box'
    root.style.transformOrigin = '0px 0px'
    root.style.animation = 'swimHeave 1.9s ease-in-out infinite'

    // Head and trunk: fusiform, deepest just behind the head, tapering to a narrow peduncle.
    el(root, 'path', {
      d: 'M-6 -9.5 C 6 -11.5, 20 -9, 30 -4.5 C 34 -3, 36 -1.5, 37.5 -0.5 '
       + 'C 36 0.8, 33 2.2, 29 3.6 C 18 7.4, 4 8.6, -6 7.2 Z',
      fill: skin,
    })
    el(root, 'path', {
      d: 'M-4 6.4 C 6 8.2, 18 7, 28 3.6 C 31 2.4, 34 1, 36 0 C 33 1.6, 26 4.6, 16 6.4 C 6 8, -1 7.6, -4 6.4 Z',
      fill: belly,
    })
    // MELON then ROSTRUM, in that order, because that is the diagnostic pair. The melon is the
    // round fatty forehead that bulges ABOVE and AHEAD of the eye and then drops sharply into a
    // distinct crease; the rostrum is a separate, near-cylindrical beak below it. Draw the head as
    // one taper into a point and you get a generic fish — which is what the first attempt did.
    el(root, 'path', {
      // Rooted well back inside the trunk (x=12), so the melon grows out of the body instead of
      // sitting on it. Started at the body's leading edge, it left a wedge of background between
      // the two outlines — invisible in motion, obvious in a still.
      d: 'M12 -10.6 C 22 -12.2, 32 -11.2, 38 -7.8 '   // melon: bulges up and forward
       + 'C 40 -6.4, 40.5 -4.8, 40 -3.6 '             // and drops steeply into the crease
       + 'C 34 -2.2, 24 -2.4, 14 -4.6 Z',
      fill: skin,
    })
    // Rostrum: short and blunt for a bottlenose — about 0.06 of body length, not a swordfish bill.
    el(root, 'path', {
      d: 'M37.5 -4.6 C 42 -3.8, 45.8 -2.9, 48.2 -1.8 '
       + 'C 45.6 -0.3, 42 0.4, 37.4 0.2 '
       + 'C 37.8 -1.5, 37.8 -3.2, 37.5 -4.6 Z',
      fill: skin,
    })
    // The mouthline: a long curve that lifts at the back. It is the whole of the "dolphin smile",
    // and it costs one stroke.
    el(root, 'path', {
      d: 'M47 -1.4 C 43 -0.6, 38 0.2, 33.5 0.2 C 31.5 0.2, 30 -0.2, 29 -0.8',
      fill: 'none', stroke: '#33475c', 'stroke-width': 0.7, 'stroke-linecap': 'round',
    })
    el(root, 'circle', { cx: 32.5, cy: -3.6, r: 1.0, fill: '#101820' })
    // Blowhole, on top, behind the melon's crest.
    el(root, 'ellipse', { cx: 25, cy: -9.4, rx: 1.5, ry: 0.7, fill: '#33475c' })
    // Dorsal fin: falcate — concave along the trailing edge, not a triangle. That curve is the
    // difference between a dolphin's fin and a shark's.
    el(root, 'path', {
      d: 'M8 -10 C 11 -17, 15.5 -21, 19.5 -22 '
       + 'C 17 -18.5, 15.5 -14, 15.5 -9.4 Z',
      fill: skin,
    })
    // Pectoral flipper: set LOW and FORWARD, near the head, and small. Placed mid-body and large
    // it reads as a second tail, which is exactly how the first version failed.
    el(root, 'path', {
      d: 'M24 4.4 C 22 9.4, 18 13.6, 13.5 15.4 C 15 10.6, 17.5 6.8, 21 4.2 Z',
      fill: '#41556b',
    })

    // Tail stock: three segments, each lagging the last, ending in the fluke. The lag is what
    // makes the flex read as a wave passing down the body instead of a hinge opening.
    const tail = spine(root, [
      { pivotX: -4, pivotY: -1 },
      { pivotX: -16, pivotY: -0.6 },
      { pivotX: -27, pivotY: -0.4 },
    ], 'swimFlukeUpDown', 1.9, 0.13)

    el(tail[0], 'path', { d: 'M-4 -8.4 C -10 -8, -15 -7, -18 -5.6 C -18 -3, -18 1.6, -18 4 C -14 5.6, -9 6.6, -4 7 Z', fill: skin })
    el(tail[1], 'path', { d: 'M-17 -5.8 C -22 -4.8, -26 -3.6, -28 -2.6 C -28 -1, -28 1.2, -28 2.6 C -25 3.4, -21 4.4, -17 4.2 Z', fill: skin })
    // The fluke itself: horizontal, notched at the centre, swept back. Drawn as the last segment so
    // it carries the accumulated lag and trails the peduncle.
    el(tail[2], 'path', {
      d: 'M-27 -2.4 C -33 -3.6, -41 -6.2, -47 -8.6 C -41 -6.2, -35 -3, -31 -0.4 '
       + 'C -35 2.2, -41 5.2, -47 7.4 C -41 5.4, -33 3, -27 2 Z',
      fill: skin,
    })
  },
})

creature({
  id: 'whale',
  title: 'Humpback whale',
  latin: 'Megaptera novaeangliae',
  view: 'profile — same vertical stroke as the dolphin, at a quarter of the rate',
  mechanism: 'dorsoventral oscillation · enormous pectorals (⅓ of body length) · ventral pleats',
  build(host) {
    const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
    svg.setAttribute('viewBox', '-64 -34 128 68')
    svg.setAttribute('class', 'mini')
    host.appendChild(svg)

    const skin = '#37485c', belly = '#b9c8d6', fin = '#2c3a4b'
    const root = el(svg, 'g')
    root.style.transformBox = 'view-box'
    root.style.transformOrigin = '0px 0px'
    root.style.animation = 'swimHeave 5.4s ease-in-out infinite'

    // Body: far bulkier than the dolphin, widest a third back, with a blunt head. The genus name
    // means "big wing" — the pectorals are the diagnostic feature and they are about a third of
    // total length, which is longer than almost anyone draws them.
    el(root, 'path', {
      d: 'M-8 -13 C 4 -16, 20 -14, 32 -8 C 38 -5, 42 -2.5, 44 -1 '
       + 'C 42 1.5, 37 5, 30 8 C 16 14, 2 15, -8 12 Z',
      fill: skin,
    })
    el(root, 'path', {
      d: 'M-6 10.5 C 4 13.5, 16 12.5, 28 7 C 34 4.2, 39 1.2, 42 -0.4 '
       + 'C 37 3, 28 8, 16 11 C 6 13.4, -2 12.6, -6 10.5 Z',
      fill: belly,
    })
    // Ventral pleats: the grooved throat. Cheap lines, and without them the belly reads as plastic.
    for (let i = 0; i < 7; i++) {
      el(root, 'path', {
        d: `M${26 - i * 3.2} ${8.4 - i * 0.55} C ${30 - i * 3.2} ${7 - i * 0.5}, ${34 - i * 3.2} ${4 - i * 0.4}, ${37 - i * 3.2} ${1.6 - i * 0.3}`,
        fill: 'none', stroke: '#8fa2b4', 'stroke-width': 0.55, opacity: 0.5,
      })
    }
    // Knobbly head — tubercles, one hair each. Another feature nobody draws, and the one that
    // says "humpback" rather than "generic whale".
    for (const [x, y] of [[36, -5.4], [31, -7.6], [26, -9.4], [40, -3.2], [34.5, -2.2], [29, -1.2]]) {
      el(root, 'circle', { cx: x, cy: y, r: 1.15, fill: '#2f3f51' })
    }
    el(root, 'circle', { cx: 33, cy: -3.2, r: 1.1, fill: '#101820' })
    // Small, far-back dorsal on a hump — the name.
    el(root, 'path', { d: 'M4 -14.6 C 6 -18.5, 9 -20, 11.5 -19.6 C 9.5 -17.4, 9 -15.6, 9.2 -13.8 Z', fill: skin })
    // Pectoral: vast, scalloped along the leading edge, white underneath. It sculls slowly.
    const pec = el(root, 'g')
    pec.style.transformBox = 'view-box'
    pec.style.transformOrigin = '22px 6px'
    pec.style.animation = 'whalePectoral 5.4s ease-in-out infinite'
    el(pec, 'path', {
      d: 'M26 0.5 C 22 11, 13 22, 2 28 C -2 30, -5 30, -4 27 C 1 20, 10 10, 18 1.5 Z',
      fill: '#dbe6ee',
    })
    el(pec, 'path', {
      d: 'M24 3 C 21 10, 15 18, 7 24 C 4 26, 1 27, 1.5 25 C 5 20, 12 12, 18 4.6 Z',
      fill: fin, opacity: 0.28,
    })

    const tail = spine(root, [
      { pivotX: -6, pivotY: -1 },
      { pivotX: -22, pivotY: -0.6 },
      { pivotX: -36, pivotY: -0.4 },
    ], 'swimFlukeUpDown', 5.4, 0.14)

    el(tail[0], 'path', { d: 'M-6 -12 C -14 -11, -20 -9.4, -24 -7.4 C -24 -3.6, -24 3, -24 5.6 C -19 8, -12 10, -6 11 Z', fill: skin })
    el(tail[1], 'path', { d: 'M-23 -7.6 C -30 -6, -35 -4.4, -38 -3 C -38 -1, -38 1.8, -38 3.6 C -34 4.8, -29 6.2, -23 5.8 Z', fill: skin })
    el(tail[2], 'path', {
      d: 'M-37 -2.8 C -46 -5, -56 -9.4, -62 -13 C -55 -9, -47 -4.2, -42 -0.5 '
       + 'C -47 3.4, -55 8, -62 11.6 C -56 8.2, -46 3.8, -37 1.8 Z',
      fill: skin,
    })
  },
})

creature({
  id: 'shark',
  title: 'Shark',
  latin: 'Carcharodon / lamniform build',
  view: 'FROM ABOVE — the stroke is lateral, and in profile it would be invisible',
  mechanism: 'lateral undulation · vertical caudal fin · thunniform: the wave lives in the rear third',
  build(host) {
    const svg = document.createElementNS(SVG_NAMESPACE, 'svg')
    svg.setAttribute('viewBox', '-58 -30 116 60')
    svg.setAttribute('class', 'mini')
    host.appendChild(svg)

    const back = '#54636e', flank = '#6b7a85'
    const root = el(svg, 'g')

    // Seen from above: a conical snout, the widest point at the pectorals, then a long taper to a
    // narrow peduncle. Fast lamniform sharks are near-symmetrical in the tail, unlike the
    // upper-lobe-dominant tail of most other sharks — the great white and mako are the exception
    // that gets drawn as the rule.
    el(root, 'path', {
      d: 'M44 0 C 40 -2.6, 34 -5.2, 26 -7 C 14 -9.4, 2 -9.4, -8 -7.6 '
       + 'C -8 7.6, 2 9.4, 14 9.4, 26 7, 44 0 Z',
      fill: back,
    })
    // Correcting the sloppy shorthand above with an explicit outline: nose, left flank, tail
    // stock, right flank.
    root.lastChild.setAttribute('d',
      'M44 0 C 39 -3.4, 32 -6, 24 -7.6 C 14 -9.4, 2 -9.2, -8 -7 '
      + 'C -10 -4, -10 4, -8 7 C 2 9.2, 14 9.4, 24 7.6 C 32 6, 39 3.4, 44 0 Z')

    // Pectorals: long, narrow, swept — the wings that hold it up, since a shark has no swim bladder.
    el(root, 'path', { d: 'M18 -6.4 C 12 -14, 2 -21, -6 -24 C -2 -17, 6 -10, 14 -5.6 Z', fill: '#4e5d69' })
    el(root, 'path', { d: 'M18 6.4 C 12 14, 2 21, -6 24 C -2 17, 6 10, 14 5.6 Z', fill: '#4e5d69' })
    // Dorsal fin, seen from above as a narrow blade along the midline.
    el(root, 'path', { d: 'M6 -1.6 C 2 -2, -4 -2, -8 -1.4 L-8 1.4 C -4 2, 2 2, 6 1.6 Z', fill: '#46545f' })
    el(root, 'circle', { cx: 30, cy: -4.2, r: 1.1, fill: '#141c22' })
    el(root, 'circle', { cx: 30, cy: 4.2, r: 1.1, fill: '#141c22' })
    // Gill slits: five, angled, just ahead of the pectorals.
    for (let i = 0; i < 5; i++) {
      el(root, 'path', {
        d: `M${24 - i * 2.6} -6.6 C ${23 - i * 2.6} -5, ${23 - i * 2.6} -3.4, ${24 - i * 2.6} -2`,
        fill: 'none', stroke: '#3d4a54', 'stroke-width': 0.6,
      })
      el(root, 'path', {
        d: `M${24 - i * 2.6} 6.6 C ${23 - i * 2.6} 5, ${23 - i * 2.6} 3.4, ${24 - i * 2.6} 2`,
        fill: 'none', stroke: '#3d4a54', 'stroke-width': 0.6,
      })
    }

    // The wave lives in the rear third — thunniform, not anguilliform. The head barely moves, and
    // that restraint is the difference between a shark and an eel.
    const tail = spine(root, [
      { pivotX: -8, pivotY: 0 },
      { pivotX: -22, pivotY: 0 },
      { pivotX: -34, pivotY: 0 },
    ], 'swimTailSideways', 1.35, 0.16)

    el(tail[0], 'path', { d: 'M-7 -7.2 C -13 -6.4, -18 -5.2, -22 -4 C -22 4, -22 4, -22 4 C -18 5.2, -13 6.4, -7 7.2 Z', fill: back })
    el(tail[1], 'path', { d: 'M-21 -4.2 C -26 -3.2, -31 -2.4, -34 -1.8 L-34 1.8 C -31 2.4, -26 3.2, -21 4.2 Z', fill: back })
    // Caudal fin, from above: a narrow vertical blade, so it reads as a thin sweeping line rather
    // than the broad fluke of a cetacean. That contrast is the entire lesson of this bestiary.
    el(tail[2], 'path', {
      d: 'M-33 -2 C -40 -1.6, -48 -1.2, -54 -0.8 L-54 0.8 C -48 1.2, -40 1.6, -33 2 Z',
      fill: back,
    })
    el(tail[2], 'path', { d: 'M-40 -1.5 C -46 -3.6, -52 -5.4, -55 -6 C -50 -3.6, -45 -2, -40 -1.2 Z', fill: flank, opacity: 0.75 })
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
  @keyframes swimTailSideways { 0%,100% { transform: rotate(-15deg) } 50% { transform: rotate(15deg) } }
  @keyframes whalePectoral    { 0%,100% { transform: rotate(-7deg) } 50% { transform: rotate(9deg) } }

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
