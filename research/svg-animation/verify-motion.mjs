#!/usr/bin/env node
// verify-motion.mjs — watches an animation actually run, and checks what it does.
//
// WHY THIS EXISTS
//
// Frozen-pose strips show the THEORETICAL state at each percentage of a cycle: they are rendered by
// pausing the animation with a negative delay. They caught a great deal — inverted signs, joints
// opening, mixed viewpoints — but they cannot catch anything about the motion itself, because in a
// frozen strip there is no motion.
//
// They cannot see: whether a foot that should be planted stays planted; whether two limbs that
// should be half a cycle apart actually are; whether a cycle returns to where it started; whether a
// part drifts; whether easing makes something hesitate where it should not.
//
// So this samples the REAL animation, frame by frame, reads the on-screen position of marked
// points, and reports trajectories plus a set of checks. Looking at a picture answers "is it
// shaped right". This answers "is it moving right".
//
// USAGE
//   node verify-motion.mjs <page.html> [--ms 2400] [--fps 30]
//
// The page marks the points it wants tracked:
//   <circle data-track="ankle-near" ...>
// Any element with data-track is sampled. Positions are reported in the SVG's own viewBox units,
// so they are comparable to the numbers in the profile tables and anchor maps.

import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  `${process.env.HOME}/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome`,
  `${process.env.HOME}/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome`,
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
].filter(Boolean)

function findChrome() {
  const found = CHROME_CANDIDATES.find((p) => existsSync(p))
  if (!found) throw new Error(`no Chrome found; set CHROME_PATH`)
  return found
}

function launch(chromePath, url) {
  const proc = spawn(chromePath, [
    '--headless=new', '--remote-debugging-port=0', '--no-sandbox',
    '--disable-dev-shm-usage', '--hide-scrollbars', '--window-size=1200,700', url,
  ], { stdio: ['ignore', 'ignore', 'pipe'] })
  return new Promise((res, rej) => {
    let buf = ''
    const timer = setTimeout(() => rej(new Error('no debugging port')), 20000)
    proc.stderr.on('data', (c) => {
      buf += c
      const m = buf.match(/ws:\/\/[^\s]+/)
      if (m) { clearTimeout(timer); res({ proc, browserWs: m[0] }) }
    })
    proc.on('exit', (code) => { clearTimeout(timer); rej(new Error(`chrome exited ${code}`)) })
  })
}

function connect(wsUrl) {
  const ws = new WebSocket(wsUrl)
  const pending = new Map()
  let nextId = 1
  const ready = new Promise((res) => ws.addEventListener('open', () => res()))
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data)
    if (msg.id && pending.has(msg.id)) {
      const { res, rej } = pending.get(msg.id)
      pending.delete(msg.id)
      msg.error ? rej(new Error(msg.error.message)) : res(msg.result)
    }
  })
  const send = (method, params = {}, sessionId) =>
    ready.then(() => new Promise((res, rej) => {
      const id = nextId++
      pending.set(id, { res, rej })
      ws.send(JSON.stringify({ id, method, params, sessionId }))
    }))
  return { send, close: () => ws.close() }
}

/**
 * Sampler, injected into the page.
 *
 * Reads each tracked element's position via getScreenCTM, which composes every transform between
 * the element and the SVG root — including the CSS animations, which is the whole point. The result
 * is converted back into viewBox units so it can be compared against the anchor map directly.
 */
const samplerSource = (ms, fps) => `
  new Promise((resolve) => {
    const marks = [...document.querySelectorAll('[data-track]')]
    if (!marks.length) { resolve({ error: 'no [data-track] elements on the page' }); return }
    const svg = marks[0].ownerSVGElement
    const inverse = svg.getScreenCTM().inverse()
    const samples = []
    const started = performance.now()
    const step = 1000 / ${fps}
    let next = started

    function read(now) {
      if (now >= next) {
        next += step
        const frame = { t: +(now - started).toFixed(1), p: {} }
        for (const m of marks) {
          const box = m.getBoundingClientRect()
          const pt = new DOMPoint(box.x + box.width / 2, box.y + box.height / 2)
            .matrixTransform(inverse)
          frame.p[m.dataset.track] = [+pt.x.toFixed(3), +pt.y.toFixed(3)]
        }
        samples.push(frame)
      }
      if (now - started < ${ms}) requestAnimationFrame(read)
      else resolve({ samples })
    }
    requestAnimationFrame(read)
  })
`

const range = (values) => Math.max(...values) - Math.min(...values)
const fmt = (n) => (n >= 0 ? ' ' : '') + n.toFixed(2)

/** A tiny sparkline so a trajectory can be read in the terminal rather than imagined. */
function spark(values, width = 48) {
  const chars = '▁▂▃▄▅▆▇█'
  const lo = Math.min(...values), hi = Math.max(...values)
  const span = hi - lo || 1
  const out = []
  for (let i = 0; i < width; i++) {
    const v = values[Math.floor((i / width) * values.length)]
    out.push(chars[Math.min(7, Math.floor(((v - lo) / span) * 8))])
  }
  return out.join('')
}

async function main() {
  const args = process.argv.slice(2)
  const page = args.find((a) => a.includes('.html'))
  if (!page) { console.error('usage: node verify-motion.mjs <page.html> [--ms N] [--fps N]'); process.exit(2) }
  const fps = args.includes('--fps') ? Number(args[args.indexOf('--fps') + 1]) : 30
  // The cycle duration matters: the closing check compares the last frame to the first, which is
  // only meaningful over a WHOLE number of cycles. Sampling an arbitrary window reported drift on
  // a perfectly periodic animation — a false positive from this tool, found by using it.
  const cycle = args.includes('--cycle') ? Number(args[args.indexOf('--cycle') + 1]) : null
  let ms = args.includes('--ms') ? Number(args[args.indexOf('--ms') + 1]) : 2400
  if (cycle) ms = cycle * Math.max(1, Math.round(ms / cycle))

  const [rawPath, query] = page.split('?')
  const url = pathToFileURL(resolve(HERE, rawPath)).href + (query ? '?' + query : '')
  const { proc, browserWs } = await launch(findChrome(), url)
  const browser = connect(browserWs)

  try {
    const { targetInfos } = await browser.send('Target.getTargets')
    const target = targetInfos.find((t) => t.type === 'page')
    const { sessionId } = await browser.send('Target.attachToTarget', { targetId: target.targetId, flatten: true })
    await browser.send('Runtime.enable', {}, sessionId)

    for (let i = 0; i < 100; i++) {
      try {
        const r = await browser.send('Runtime.evaluate', {
          expression: 'location.href + "|" + document.readyState', returnByValue: true,
        }, sessionId)
        const [href, state] = r.result.value.split('|')
        if (href === url && state === 'complete') break
      } catch (e) { if (!/context was destroyed|Cannot find context/i.test(e.message)) throw e }
      await new Promise((r) => setTimeout(r, 100))
    }
    await browser.send('Runtime.evaluate', { expression: 'new Promise(r=>setTimeout(r,400))', awaitPromise: true }, sessionId)

    const { result, exceptionDetails } = await browser.send('Runtime.evaluate', {
      expression: samplerSource(ms, fps), awaitPromise: true, returnByValue: true,
    }, sessionId)
    if (exceptionDetails) throw new Error(exceptionDetails.text)
    if (result.value.error) throw new Error(result.value.error)

    const samples = result.value.samples
    const names = Object.keys(samples[0].p)

    console.log(`tracked ${names.length} point(s) over ${samples.length} real frames, ${ms}ms`
      + (cycle ? ` (${Math.round(ms / cycle)} whole cycles of ${cycle}ms)` : ' — pass --cycle for the closing check'))
    console.log('')

    console.log('point                     x-range   y-range   y over time')
    console.log('------------------------  --------  --------  ' + '-'.repeat(48))
    for (const name of names) {
      const xs = samples.map((s) => s.p[name][0])
      const ys = samples.map((s) => s.p[name][1])
      console.log(
        `${name.padEnd(24)}  ${fmt(range(xs)).padStart(8)}  ${fmt(range(ys)).padStart(8)}  ${spark(ys)}`,
      )
    }

    // ── Checks that a still image cannot make ─────────────────────────────
    console.log('\nchecks')
    console.log('------')
    const findings = []

    // 1. Does the cycle close? Only checkable over whole cycles.
    for (const name of (cycle ? names : [])) {
      const first = samples[0].p[name]
      const last = samples[samples.length - 1].p[name]
      const drift = Math.hypot(last[0] - first[0], last[1] - first[1])
      const extent = Math.max(range(samples.map((s) => s.p[name][0])), range(samples.map((s) => s.p[name][1])), 1)
      if (drift > extent * 0.25) {
        findings.push(`${name}: does not return to its start — drift ${drift.toFixed(2)} over a ${extent.toFixed(2)} range`)
      }
    }

    // 2. Points named "*-near" and "*-far" are expected to be half a cycle apart.
    //
    //    The first version tested this with a plain correlation and called a negative value
    //    "antiphase". That only holds for roughly sinusoidal signals. An inverse-kinematics gait has
    //    a 60% PLATEAU while the foot is planted, and two half-cycle-shifted copies of a plateaued
    //    wave overlap enough to score -0.45 — reported as a defect on a limb pair that was exactly
    //    half a cycle apart. A third false positive from this tool, again found by using it.
    //
    //    The shape-independent test: shift one series by half a cycle and check that it MATCHES.
    const correlate = (a, b) => {
      const n = Math.min(a.length, b.length)
      const ma = a.slice(0, n).reduce((x, y) => x + y, 0) / n
      const mb = b.slice(0, n).reduce((x, y) => x + y, 0) / n
      let num = 0, da = 0, db = 0
      for (let i = 0; i < n; i++) {
        num += (a[i] - ma) * (b[i] - mb); da += (a[i] - ma) ** 2; db += (b[i] - mb) ** 2
      }
      return num / (Math.sqrt(da * db) || 1)
    }
    for (const name of names.filter((n) => n.endsWith('-near'))) {
      const twin = name.replace(/-near$/, '-far')
      if (!names.includes(twin)) continue
      const a = samples.map((s) => s.p[name][1])
      const b = samples.map((s) => s.p[twin][1])
      if (!cycle) { console.log(`  ${name} vs ${twin}: skipped — needs --cycle`); continue }
      const perCycle = Math.round(samples.length / (ms / cycle))
      const half = Math.round(perCycle / 2)
      const shifted = correlate(a.slice(0, a.length - half), b.slice(half))
      const verdict = shifted > 0.8 ? 'half a cycle apart, as expected'
        : shifted > 0.4 ? 'roughly, but loosely' : 'NOT half a cycle apart'
      console.log(`  ${name} vs ${twin}: shift-by-half-cycle match ${shifted.toFixed(2)} — ${verdict}`)
      if (shifted < 0.8) findings.push(`${name}/${twin} are not half a cycle apart (match=${shifted.toFixed(2)})`)
    }

    // 3. A point marked "*-contact" must hold still while it is at its lowest — that is what being
    //    planted means, and it is the check the walking figure needed.
    //
    //    Slip is RELATIVE TO THE SURFACE. Measuring it in absolute viewBox coordinates was wrong:
    //    on a treadmill the ground moves, so a foot correctly locked to the ground still travels
    //    across the frame. If the page marks a point on the surface as `*-surface`, its motion is
    //    subtracted. Found by using this tool: the first version reported a foot "sliding" when it
    //    was in fact stationary against a moving floor.
    const surfaceName = names.find((n) => n.endsWith('-surface'))
    for (const name of names.filter((n) => n.includes('contact'))) {
      const ys = samples.map((s) => s.p[name][1])
      const lowest = Math.max(...ys)
      // Group the planted frames into CONTIGUOUS EPISODES and measure within each. Measuring across
      // the whole sample lumped two separate stance phases together and counted the reposition
      // between them as slip — a second false positive from this tool, again found by using it.
      const episodes = []
      let current = null
      samples.forEach((s, i) => {
        if (s.p[name][1] > lowest - 1.5) {
          if (!current) { current = []; episodes.push(current) }
          current.push(s)
        } else current = null
      })
      const measured = episodes.filter((e) => e.length > 2).map((e) => {
        const rel = e.map((s) => s.p[name][0] - (surfaceName ? s.p[surfaceName][0] : 0))
        return { frames: e.length, slip: range(rel) }
      })
      if (measured.length) {
        const worst = measured.reduce((a, b) => (b.slip > a.slip ? b : a))
        const basis = surfaceName ? `relative to ${surfaceName}` : 'ABSOLUTE — no *-surface marked'
        console.log(`  ${name}: ${measured.length} contact episode(s), worst slip ${worst.slip.toFixed(2)} units over ${worst.frames} frames (${basis})`)
        if (worst.slip > 2) findings.push(`${name} SLIDES while planted: ${worst.slip.toFixed(2)} units, ${basis}`)
      }
    }

    // 4. Nothing should be frozen: a tracked point that never moves is usually a broken selector or
    //    an animation that failed to apply.
    for (const name of names) {
      const moved = Math.max(range(samples.map((s) => s.p[name][0])), range(samples.map((s) => s.p[name][1])))
      if (moved < 0.05) findings.push(`${name} never moves — animation not applied, or wrong element marked`)
    }

    console.log('')
    if (findings.length === 0) {
      console.log('PASS — no motion defects found')
    } else {
      console.log(`${findings.length} finding(s):`)
      for (const f of findings) console.log(`  ! ${f}`)
      process.exitCode = 1
    }
  } finally {
    browser.close()
    proc.kill()
  }
}

main().catch((e) => { console.error(e.message); process.exit(1) })
