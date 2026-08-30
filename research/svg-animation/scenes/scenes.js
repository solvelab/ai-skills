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
scene({
  id: 'birds',
  title: 'Birds',
  recipe: 'follow-path + offset-rotate + wing oscillate + stagger',
  cost: 'layout — 11 birds, 22 animated wings',
  note:
    'offset-path carries each bird along a curve and offset-rotate: auto turns it to face where it ' +
    'is going — that facing is what stops it reading as a sliding sticker. Wing period and path ' +
    'offset are per-bird, so the flock never beats in unison.',
  build(stage) {
    stage.style.background = 'linear-gradient(#cfe3f2 0%, #eaf2f7 55%, #f6e9d8 100%)'
    const rand = seeded(31337)
    const svg = layer(stage)

    // Hills behind, for the birds to be in front of.
    el(svg, 'path', {
      d: 'M0 640 L0 470 Q 200 400 380 455 Q 560 512 760 442 Q 960 372 1200 452 L1200 640 Z',
      fill: '#9fb8a6', opacity: 0.55,
    })
    el(svg, 'path', {
      d: 'M0 640 L0 540 Q 260 486 460 528 Q 700 578 900 520 Q 1060 476 1200 526 L1200 640 Z',
      fill: '#7e9c8a', opacity: 0.75,
    })

    const paths = [
      'M-80 180 C 200 90, 520 250, 800 140 S 1180 60, 1320 150',
      'M-80 300 C 260 220, 480 360, 820 250 S 1160 190, 1320 270',
      'M-80 110 C 300 190, 600 60, 900 170 S 1200 240, 1320 120',
    ]
    for (let i = 0; i < 11; i++) {
      const bird = document.createElement('div')
      bird.className = 'bird'
      bird.style.offsetPath = `path("${paths[i % paths.length]}")`
      bird.style.animation = `fly ${17 + rand() * 12}s linear ${-rand() * 22}s infinite`
      bird.style.setProperty('--scale', (1.1 + rand() * 1.1).toFixed(2))

      const b = document.createElementNS(SVG_NAMESPACE, 'svg')
      b.setAttribute('viewBox', '-14 -10 28 20')
      b.setAttribute('width', '30')
      b.setAttribute('height', '22')
      const wingL = el(b, 'path', {
        d: 'M0 0 C -5 -7, -10 -8, -13 -3', fill: 'none',
        stroke: '#2f3b46', 'stroke-width': 1.9, 'stroke-linecap': 'round',
      })
      const wingR = el(b, 'path', {
        d: 'M0 0 C 5 -7, 10 -8, 13 -3', fill: 'none',
        stroke: '#2f3b46', 'stroke-width': 1.9, 'stroke-linecap': 'round',
      })
      const period = (0.34 + rand() * 0.3).toFixed(2)
      wingL.style.transformOrigin = '0 0'
      wingR.style.transformOrigin = '0 0'
      wingL.style.animation = `flapL ${period}s ease-in-out infinite alternate`
      wingR.style.animation = `flapR ${period}s ease-in-out infinite alternate`
      bird.appendChild(b)
      stage.appendChild(bird)
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
  @keyframes flapL  { from { transform: rotate(16deg) } to { transform: rotate(-34deg) } }
  @keyframes flapR  { from { transform: rotate(-16deg) } to { transform: rotate(34deg) } }
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

return { scenes, primitives, sceneCss, reducedMotionCss, seeded }
})()
