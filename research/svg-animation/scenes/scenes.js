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
  .stage .canvasLayer { width: 100%; }
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
