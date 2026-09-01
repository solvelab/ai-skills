#!/usr/bin/env node
// measure.mjs — runs one prototype in a real Chrome and reports what it costs the main thread.
//
// Zero dependencies: it speaks the Chrome DevTools Protocol over the WebSocket that Node 22+
// ships as a global, so re-running it needs no npm install. Point CHROME_PATH at any Chrome or
// Chromium build; the default is the Playwright cache this repository's author already had.
//
// Usage:
//   node measure.mjs prototypes/<file>.html [--ms 4000] [--label "name"]
//   node measure.mjs --all            # every prototype, one table
//
// WHAT IT MEASURES
//   frame timing        rAF deltas sampled inside the page: count, mean, p50, p95, worst, and how
//                       many frames missed a 60 Hz budget (>16.7ms)
//   presented frames    Page.screencastFrame count / wall seconds. Fires per COMPOSITED frame, so
//                       it is the only handle here on work that never reaches the main thread —
//                       raster, and therefore filters. The Performance domain exposes no paint or
//                       raster counter at all (checked against this build: the metric list has
//                       LayoutCount and RecalcStyleCount and nothing for paint).
//   main-thread work    CDP Performance.getMetrics deltas across the sample window:
//                       RecalcStyleCount, LayoutCount, RecalcStyleDuration, LayoutDuration,
//                       ScriptDuration, TaskDuration
//
// WHAT IT DOES NOT MEASURE — read this before quoting a number from it
//   It cannot tell "composited on the GPU" apart from "painted cheaply". A technique that shows
//   near-zero style/layout work is doing little main-thread work; that is the useful signal, and
//   it is not the same claim as "runs on the compositor".
//   It runs headless. Under WSL2 there is no GPU, so rasterisation is software (SwiftShader).
//   Absolute frame times therefore do NOT transfer to a desktop with a GPU. What does transfer is
//   the RELATIVE ordering of two techniques measured on the same machine in the same run, which is
//   what every comparison in this directory relies on.
//   One browser, one device class. Nothing here says anything about Firefox, Safari, or a phone.

import { spawn } from 'node:child_process'
import { readdir } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { dirname, resolve, basename } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  `${process.env.HOME}/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome`,
  `${process.env.HOME}/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome`,
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
].filter(Boolean)

// Counters read as deltas across the sample window: they say what a second of animation costs.
const METRICS = [
  'RecalcStyleCount',
  'LayoutCount',
  'RecalcStyleDuration',
  'LayoutDuration',
  'ScriptDuration',
  'TaskDuration',
]

// Gauges read once, at the end: they say what the scene costs to merely exist. A technique can be
// free per frame and still lose on this axis, which is the whole point of the <use> comparison.
const GAUGES = ['Nodes', 'LayoutObjects', 'JSHeapUsedSize']

function findChrome() {
  const found = CHROME_CANDIDATES.find((p) => existsSync(p))
  if (!found) {
    throw new Error(
      `no Chrome found. Set CHROME_PATH. Looked in:\n  ${CHROME_CANDIDATES.join('\n  ')}`,
    )
  }
  return found
}

/** Launch headless Chrome and resolve once it prints the DevTools endpoint on stderr. */
function launch(chromePath, url) {
  const proc = spawn(chromePath, [
    '--headless=new',
    '--remote-debugging-port=0',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--hide-scrollbars',
    '--window-size=1280,720',
    '--force-device-scale-factor=1',
    url,
  ], { stdio: ['ignore', 'ignore', 'pipe'] })

  return new Promise((res, rej) => {
    let buf = ''
    const timer = setTimeout(() => rej(new Error('Chrome did not report a debugging port')), 20000)
    proc.stderr.on('data', (chunk) => {
      buf += chunk
      const m = buf.match(/ws:\/\/[^\s]+/)
      if (m) {
        clearTimeout(timer)
        res({ proc, browserWs: m[0] })
      }
    })
    proc.on('exit', (code) => {
      clearTimeout(timer)
      rej(new Error(`Chrome exited early with code ${code}`))
    })
  })
}

/** Minimal CDP client: send(method, params) -> Promise<result>. */
function connect(wsUrl) {
  const ws = new WebSocket(wsUrl)
  const pending = new Map()
  let nextId = 1

  const ready = new Promise((res, rej) => {
    ws.addEventListener('open', () => res())
    ws.addEventListener('error', (e) => rej(new Error(`CDP socket error: ${e.message ?? e.type}`)))
  })

  const listeners = new Map()

  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data)
    if (msg.id && pending.has(msg.id)) {
      const { res, rej } = pending.get(msg.id)
      pending.delete(msg.id)
      msg.error ? rej(new Error(`${msg.error.message} (${msg.error.code})`)) : res(msg.result)
      return
    }
    if (msg.method && listeners.has(msg.method)) listeners.get(msg.method)(msg.params, msg.sessionId)
  })

  const on = (method, fn) => listeners.set(method, fn)

  const send = (method, params = {}, sessionId) =>
    ready.then(
      () =>
        new Promise((res, rej) => {
          const id = nextId++
          pending.set(id, { res, rej })
          ws.send(JSON.stringify({ id, method, params, sessionId }))
        }),
    )

  return { send, on, close: () => ws.close(), ready }
}

const metricMap = (list, names = METRICS) =>
  Object.fromEntries(list.filter((m) => names.includes(m.name)).map((m) => [m.name, m.value]))

/** The sampler that runs inside the page: collect rAF deltas for `ms`, then report. */
const samplerSource = (ms) => `
  new Promise((resolve) => {
    const deltas = []
    let last = performance.now()
    const start = last
    function tick(now) {
      deltas.push(now - last)
      last = now
      if (now - start < ${ms}) requestAnimationFrame(tick)
      else resolve(deltas)
    }
    requestAnimationFrame(tick)
  })
`

const quantile = (sorted, q) => sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * q))]

async function measureOne(chromePath, file, ms, label) {
  const url = pathToFileURL(resolve(HERE, file)).href
  const { proc, browserWs } = await launch(chromePath, url)
  const browser = connect(browserWs)

  try {
    // Attach to the page target that Chrome opened for our URL.
    const { targetInfos } = await browser.send('Target.getTargets')
    const page = targetInfos.find((t) => t.type === 'page')
    if (!page) throw new Error('no page target')
    const { sessionId } = await browser.send('Target.attachToTarget', {
      targetId: page.targetId,
      flatten: true,
    })

    await browser.send('Page.enable', {}, sessionId)
    await browser.send('Runtime.enable', {}, sessionId)
    await browser.send('Performance.enable', {}, sessionId)

    // Chrome attaches the target while it is still on about:blank and navigates afterwards, so a
    // naive evaluate here dies with "Execution context was destroyed". Poll until the document we
    // asked for is the one loaded, swallowing the destroyed-context errors that the swap throws.
    const deadline = Date.now() + 15000
    for (;;) {
      try {
        const { result } = await browser.send('Runtime.evaluate', {
          expression: 'location.href + "|" + document.readyState',
          returnByValue: true,
        }, sessionId)
        const [href, state] = result.value.split('|')
        if (href === url && state === 'complete') break
      } catch (err) {
        if (!/context was destroyed|Cannot find context/i.test(err.message)) throw err
      }
      if (Date.now() > deadline) throw new Error(`page never finished loading: ${url}`)
      await new Promise((r) => setTimeout(r, 100))
    }

    // Let the page settle before sampling: first paint costs are not what we are comparing.
    await browser.send('Runtime.evaluate', {
      expression: 'new Promise(r => setTimeout(r, 600))',
      awaitPromise: true,
    }, sessionId)

    // Page.screencastFrame fires once per COMPOSITED frame, which is the only signal available
    // here for work that never touches the main thread — raster, and therefore filters. Kept at a
    // tiny size and lowest quality so the capture itself is not what we end up measuring.
    let presentedFrames = 0
    browser.on('Page.screencastFrame', async (params, sid) => {
      presentedFrames++
      try {
        await browser.send('Page.screencastFrameAck', { sessionId: params.sessionId }, sid)
      } catch { /* the run may already be tearing down; a dropped ack is not a result */ }
    })
    await browser.send('Page.startScreencast', {
      format: 'jpeg', quality: 1, maxWidth: 160, maxHeight: 90, everyNthFrame: 1,
    }, sessionId)

    const wallStart = Date.now()
    const before = metricMap((await browser.send('Performance.getMetrics', {}, sessionId)).metrics)

    const { result, exceptionDetails } = await browser.send('Runtime.evaluate', {
      expression: samplerSource(ms),
      awaitPromise: true,
      returnByValue: true,
    }, sessionId)
    if (exceptionDetails) throw new Error(`page threw: ${exceptionDetails.text}`)

    const wallSeconds = (Date.now() - wallStart) / 1000
    await browser.send('Page.stopScreencast', {}, sessionId)
    const afterMetrics = (await browser.send('Performance.getMetrics', {}, sessionId)).metrics
    const after = metricMap(afterMetrics)
    const gauges = metricMap(afterMetrics, GAUGES)

    // Drop the first delta: it measures the gap to the sampler starting, not a rendered frame.
    const deltas = result.value.slice(1)
    const sorted = [...deltas].sort((a, b) => a - b)
    const sum = deltas.reduce((a, b) => a + b, 0)
    const seconds = sum / 1000

    return {
      label: label ?? basename(file, '.html'),
      frames: deltas.length,
      fps: +(deltas.length / seconds).toFixed(1),
      meanMs: +(sum / deltas.length).toFixed(2),
      p50Ms: +quantile(sorted, 0.5).toFixed(2),
      p95Ms: +quantile(sorted, 0.95).toFixed(2),
      worstMs: +sorted[sorted.length - 1].toFixed(2),
      over16_7: deltas.filter((d) => d > 16.7).length,
      // Per second of animation, so windows of different length stay comparable.
      recalcStylePerSec: +((after.RecalcStyleCount - before.RecalcStyleCount) / seconds).toFixed(1),
      layoutPerSec: +((after.LayoutCount - before.LayoutCount) / seconds).toFixed(1),
      styleMsPerSec: +(((after.RecalcStyleDuration - before.RecalcStyleDuration) * 1000) / seconds).toFixed(2),
      layoutMsPerSec: +(((after.LayoutDuration - before.LayoutDuration) * 1000) / seconds).toFixed(2),
      scriptMsPerSec: +(((after.ScriptDuration - before.ScriptDuration) * 1000) / seconds).toFixed(2),
      taskMsPerSec: +(((after.TaskDuration - before.TaskDuration) * 1000) / seconds).toFixed(2),
      presentedFps: +(presentedFrames / wallSeconds).toFixed(1),
      nodes: gauges.Nodes,
      layoutObjects: gauges.LayoutObjects,
      heapMb: +(gauges.JSHeapUsedSize / 1048576).toFixed(1),
    }
  } finally {
    browser.close()
    proc.kill()
  }
}

async function main() {
  const args = process.argv.slice(2)
  const msArg = args.indexOf('--ms')
  const ms = msArg !== -1 ? Number(args[msArg + 1]) : 4000
  const labelArg = args.indexOf('--label')
  const label = labelArg !== -1 ? args[labelArg + 1] : undefined
  const chromePath = findChrome()

  let files = args.filter((a) => a.endsWith('.html'))
  if (args.includes('--all')) {
    const dir = resolve(HERE, 'prototypes')
    files = (await readdir(dir)).filter((f) => f.endsWith('.html')).sort()
      .map((f) => `prototypes/${f}`)
  }
  if (files.length === 0) {
    console.error('usage: node measure.mjs <prototype.html> [--ms 4000] [--label name]')
    console.error('       node measure.mjs --all')
    process.exit(2)
  }

  const version = await new Promise((res) => {
    const p = spawn(chromePath, ['--version'])
    let out = ''
    p.stdout.on('data', (d) => (out += d))
    p.on('exit', () => res(out.trim()))
  })

  console.log(`browser: ${version}`)
  console.log(`sample:  ${ms}ms per prototype, headless, software rasterisation`)
  console.log('')

  const rows = []
  for (const f of files) {
    process.stderr.write(`measuring ${f} ...\n`)
    rows.push(await measureOne(chromePath, f, ms, files.length === 1 ? label : undefined))
  }

  const cols = process.env.GAUGES
    ? ['label', 'nodes', 'layoutObjects', 'heapMb', 'layoutPerSec', 'styleMsPerSec', 'taskMsPerSec']
    : ['label', 'fps', 'presentedFps', 'p95Ms', 'over16_7',
       'recalcStylePerSec', 'layoutPerSec', 'styleMsPerSec', 'taskMsPerSec']
  const width = Object.fromEntries(
    cols.map((c) => [c, Math.max(c.length, ...rows.map((r) => String(r[c]).length))]),
  )
  const line = (values) => cols.map((c) => String(values[c]).padEnd(width[c])).join('  ')
  console.log(line(Object.fromEntries(cols.map((c) => [c, c]))))
  console.log(cols.map((c) => '-'.repeat(width[c])).join('  '))
  for (const r of rows) console.log(line(r))

  if (process.env.JSON) console.log('\n' + JSON.stringify(rows, null, 2))
}

main().catch((err) => {
  console.error(err.message)
  process.exit(1)
})
