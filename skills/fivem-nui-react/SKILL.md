---
name: fivem-nui-react
description: >-
  Conventions for FiveM/RedM NUI apps in React (CEF), distilled from a production template and 30+
  apps forked from it. Use when creating or editing a NUI — the Lua↔React bridge (useNUIEvent,
  multiplexed callback, uiReady handshake, invisible-by-default), Vite build for CEF (relative base,
  flat filenames), CEF rendering quirks (drop-shadow vs box-shadow, transparent root, zoom vs
  transform scale), tokens.css design-system law, and browser dev-mode without the game. For the
  Lua side of NUI (SetNuiFocus, callbacks, cleanup) see fivem-lua; for non-NUI React SPAs see
  react-api-client.
metadata:
  author: solvelab
  version: 1.0.0
  category: nui
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

# FiveM/RedM NUI in React (CEF)

A NUI is a React SPA rendered by the game's embedded Chromium (CEF) over the world. Everything
below exists because CEF is *not* a normal browser and the game — not the user — owns focus and
visibility.

## The bridge contract

- **Inbound (Lua → NUI)**: `SendNUIMessage({ action, data })` arrives as a window `message` event.
  One hook, `useNUIEvent(action, cb)`, filters by `action`. Never parse `event.data` ad hoc.
- **Outbound (NUI → Lua)**: `fetch("https://<resource>/<endpoint>")` POST. Multiplex EVERYTHING
  through a single endpoint (`nuiCallback`) with a `{ context: 'client'|'server', event, payload }`
  body — one `RegisterNUICallback` on the Lua side routes by `context`/`event` instead of N
  registrations drifting apart.
- **`uiReady` handshake (mandatory)**: the NUI sends `uiReady` once after mount (with a settle
  delay); Lua gates its FIRST `SendNUIMessage` on it. Without this, data sent during CEF page load
  is silently lost.
- **Invisible by default**: `App` returns `null` until a `showNUI` event arrives; `hideNUI` hides.
  The game world is the background — a NUI that renders on boot covers the screen.
- **Focus belongs to Lua**: `SetNuiFocus(show, show)` on open, `(false, false)` on EVERY close path
  (ESC included), and `onResourceStop` must force-close (rule from `fivem-lua`). In React, a
  `setFocus` event only toggles `document.body.style.pointerEvents`.

Full hook implementations + the Lua counterpart: `references/nui-bridge.md`.

## Vite build for CEF

- `base: './'` — CEF loads the page from the resource filesystem; absolute paths 404.
- Flat, hash-less output names (`entryFileNames: 'assets/[name].js'`, same for chunks/assets) —
  the fxmanifest `files { 'dist/index.html', 'dist/assets/*' }` must match stable names.
- `minify: 'terser'` with `drop_console: true` — console output costs frames in CEF and leaks
  into the game's console.
- Output `dist/` is the `ui_page`; deploy = build + copy into the resource's `client/html/`
  (or equivalent), then restart the resource.

## CEF rendering quirks (each rule earned by a real visual bug)

- **Outer `box-shadow` renders broken — use `filter: drop-shadow()`** (with `-webkit-` prefix).
  `inset` box-shadow still works and is the tool for inner highlights. Ship utility classes
  (`.drop-shadow-card`, `.drop-shadow-panel`, ...) and ban Tailwind `shadow-*` for outer shadows.
- **Transparent root**: `html, body, #root { background: transparent !important }` — the game
  must show through.
- **Scaling: `zoom`, not `transform: scale`.** On promoted layers (willChange/filter), CEF scales
  the ALREADY-RASTERIZED bitmap with `transform: scale` — the whole UI blurs. `zoom` changes
  layout size and re-rasterizes text/vectors crisp at the target size.
- **Legibility over the world**: strong `text-shadow` (CEF renders it poorly on promoted layers —
  prefer `drop-shadow` filters for that case) and glass/panel backgrounds; floating text without
  contrast dies over a bright sky.
- **Resolution independence**: `vh`/`vw` units + max-width media breakpoints for HUD scaling —
  players run 1366px to ultrawide.
- Gradient text: `background: <gradient>; -webkit-background-clip: text;
  -webkit-text-fill-color: transparent` is the CEF-safe technique.

## Design system: tokens.css is law

- All colors live as CSS vars in `styles/tokens.css`; Tailwind maps every color to a var. A new
  color is added to tokens.css — never hardcoded in a component.
- Panels/forms use the shared `.panel*` classes and `--panel-*` vars (gradient bg + drop-shadow
  outer + inset glow) — one visual identity across every NUI of the server.

## Dev without the game

- Mock the CEF global in `main.tsx`:
  `if (typeof GetParentResourceName === 'undefined') window.GetParentResourceName = () => 'dev'` —
  outbound fetches fail harmlessly in the browser.
- Simulate inbound events from DevTools:
  `window.dispatchEvent(new MessageEvent('message', { data: { action: 'showNUI', data: {...} } }))`.
- Test harness (vitest): `mockNuiEvent(action, data)` dispatches MessageEvents; stub `global.fetch`
  to record `https://<resource>/<endpoint>` calls (`getNuiCalls()`); assert the bridge contract,
  not implementation details.

## Template-fork workflow

- New NUI = GitHub **"use this template"** on the canonical template repo — never copy-paste an
  existing app (it drags app-specific code along).
- Customize `App.tsx` and add feature components; DO NOT touch the bridge (`hooks/useNUI.ts`),
  `constants/nui.ts`, the Vite config, or tokens.css structure — those update via template.
- Keep the app buildable headless (`npm run build`) — deploy scripts depend on it.

## See also

- `fivem-lua` — the Lua side: SetNuiFocus pairing, callback validation (payload is forgeable),
  disconnect/resource-stop cleanup.
- `react-api-client` — for standalone (non-CEF) React SPAs talking to a REST API.
