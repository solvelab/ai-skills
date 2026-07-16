---
name: assettoserver-csp-lua
description: >-
  Conventions for CSP Lua online scripts served by AssettoServer (CSPServerScriptProvider) — the
  zero-install in-game UI layer of an AC server: overlays/HUDs/toasts drawn with the draw-list API
  in a single transparentWindow, DirectWrite text, ac.OnlineEvent packets mirrored byte-for-byte
  with the C# plugin, remote images and audio loaded by URL from the server, local car telemetry,
  and the mockup-first workflow for visuals you cannot render outside the game. Distilled from a
  production DriveZone server. Use when writing or reviewing a .lua online script (overlay, HUD,
  toast, in-game sound, login UI), when a CSP overlay renders wrong (empty flat box, glued or
  overlapping text, missing glyphs, sound plays only once), or when an OnlineEvent packet silently
  never arrives. Do NOT use for the C# plugin side — packet classes, config, chat commands,
  publishing (that is assettoserver-plugin), for server configuration/deploy (that is
  assettoserver-ops), for CSP apps or track scripts (different Lua contexts with different
  permissions), or for FiveM Lua (that is fivem-lua).
metadata:
  author: solvelab
  version: 1.0.0
  category: game
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

# CSP Lua online scripts (AssettoServer-served overlays)

Prescriptive conventions for the in-game UI layer of an AssettoServer: Lua scripts pushed to every
client by the server itself. Zero-install is the point — the player installs nothing; art, sound
and code all arrive over the server's HTTP port. Every rule below was paid for with an in-game
iteration; in this stack a wrong guess costs a deploy plus a human driving session to observe it.

## What an online script is

- The plugin registers it via `CSPServerScriptProvider.AddScript(script, debugFilename,
  configValues)`; the server advertises `[SCRIPT_N-...]` sections in CSP extra options pointing at
  `http://{ServerIP}:{ServerHTTPPort}/api/scripts/N`. The client downloads and runs it on join.
- `["REQUIRED"] = 1` makes CSP refuse clients that do not run the script — reserve it for gate
  flows (login). Cosmetic overlays MUST ship `["REQUIRED"] = 0`: a client without them just doesn't
  see the overlay.
- Server config reaches the script through `ac.configValues({ key = default, ... })`. Decimals
  cross this boundary as strings — the C# side must format them with InvariantCulture or a pt-BR
  host silently turns `0.7` into `"0,7"` and the script falls back to its Lua defaults with **no
  symptom** (see `assettoserver-plugin`). Keep Lua defaults equal to the C# defaults so a missing
  config degrades gracefully — but know that this same choice hides delivery failures.
- Each script is an **isolated Lua state**: no shared globals, no runtime negotiation between
  overlays. Anything two scripts must agree on (layout offsets, packet layouts) is agreed by
  convention and documented on both sides.
- If the script is embedded in the plugin DLL and mirrored in a UI repo, the copies must be
  byte-identical — gate with `cmp -s` in the rite, not with good intentions.

## Consult the SDK — never guess an API

Every CSP install ships authoritative EmmyLua stubs, one per Lua context:

```
<AC root>/extension/internal/lua-sdk/ac_online_script/lib.lua   # ~17k lines; THIS context
grep -nE "function ui\.drawRectFilled" ".../ac_online_script/lib.lua"
```

Read the signature and its doc comment before using any `ui.*` / `ac.*` function. The doc comments
carry the load-bearing details (default args, corner flags, URL support, one-shot audio semantics).

**The `withoutIO` myth.** The SDK's `rules.json` marks `withoutIO: true` only for
`ac_track_script`, `ac_car_cphys` and `ac_car_scriptable_display` — NOT for online scripts. A
server-served online script measurably has `web.*` (get/post/request/socket/loadRemoteAssets) and
`io.*`. Route identity/credential traffic through the server plugin anyway — **by decision**
(server-authoritative identity from the connection, credentials never handled client-side) — and
write that reason in the comment. A false "the API doesn't exist" claim misleads the next reader
into bad architecture the day they discover it does.

## Render doctrine

- **ONE `ui.transparentWindow` per overlay; everything inside is draw-list.** Paint order within a
  window is deterministic (first call = bottom). Overlapping transparentWindows do NOT stratify —
  the first stays on top. Symptom of getting this wrong: a flat, empty box where the overlay
  should be.
- `ui.transparentWindow(id, pos, size, noPadding, inputs, fn)` — 4th arg `noPadding` (`true` →
  coordinates start at 0,0), 5th `inputs` (`false` = non-interactive overlay).
- **Rounded corners + accent bar:** never draw two boxes with opposite `ui.CornerFlags` — the
  straight corners of one are never covered by the curved corners of the other, leaving square
  "teeth". Draw the full rounded panel, then re-draw the same rounded rect in the accent color
  inside a clip — the CSS `overflow: hidden` equivalent:

  ```lua
  ui.drawRectFilled(vec2(0, 0), vec2(w, h), panelColor, 12)
  ui.pushClipRect(vec2(0, 0), vec2(4, h), true)   -- 4px accent column
  ui.drawRectFilled(vec2(0, 0), vec2(w, h), accentColor, 12)
  ui.popClipRect()
  ```

  `ui.CornerFlags`: None 0 · TopLeft 1 · TopRight 2 · BottomLeft 4 · BottomRight 8 · Top 3 ·
  Bottom 12 · Left 5 · Right 10 · All 15.
- **Images by URL:** `ui.drawImage(src, p1, p2, color)` accepts URLs (documented); serve brand art
  from the server's static hosting and let CSP download + cache. Zero-install.
- **`pcall` around every overlay draw.** Decoration must never kill the script — a dead script
  means no overlays at all, including the required ones.
- **Colors vs a web mockup:** CSP renders more vivid than CSS — expect to tune saturated accents
  slightly down. Panels meant to look solid need near-opaque alpha (≈0.98); semi-transparent
  panels leak gameplay and read as "the background color is wrong".

## DirectWrite text — the trap table

Exact pixel sizes come from `ui.pushDWriteFont("Segoe UI;Weight=Bold")` + `ui.dwriteText(text,
sizePx, color)` + `ui.measureDWriteText(text, sizePx)`. The font attribute string accepts only
`Weight` / `Style` / `Stretch` — nothing else.

| Symptom | Cause | Fix |
|---|---|---|
| Segments glue together (`LABEL:value`, `unit0`) | DWrite discards the **trailing** space at measure AND draw; leading and inner spaces survive | Never encode separation as a trailing space — advance x by an explicit px gap |
| Letter-spacing/tracking has no effect | No native tracking | Draw char-by-char advancing x by measured width + spacing; a space measures 0 alone — measure it as `measure("A A") - measure("AA")` |
| Stacked lines overlap | A glyph box is ≈1.33× the font size (ascent+descent), not 1× | Derive every line y and the panel height from `ui.measureDWriteText(...).y`; cache the metrics (sizes are constants) |
| `JOSé`, broken glyph after truncation | `string.upper`/`string.sub` are ASCII/byte-wise; LuaJIT ships no `utf8` lib | Iterate codepoints; Latin-1 Supplement uppercase = lead byte 0xC3, second 0xA0–0xBE minus 0x20, skipping 0xB7 (÷); truncate on codepoint boundaries |
| Glyph renders as `?` | Built-in font lacks the glyph (★ and friends) | Ship a PNG and `ui.drawImage` it |
| Accented literals garbled | Source encoding drift | Explicit UTF-8 escapes in literals: `"m\195\169dia"` = "média", `"\194\183"` = "·" |

Copy-paste helpers for all of these: `references/snippets.lua`.

## OnlineEvent packets

- The Lua layout (`ac.StructItem.key(...)` + named/sized fields) must match the C# `OnlineEvent<T>`
  **byte-for-byte** — enforce it with a static parity gate over the published DLL (see
  `bug-hunter` → `references/track-dotnet-plugin.md`), not by review.
- **Never name a field `key`.** It collides with the `ac.StructItem.key` mechanism and the packet
  is silently never delivered — while every static gate passes, because the layouts do match.
- Two scripts that register the **exact same layout both receive the event**. Reuse an existing
  server→client packet in a second overlay instead of minting a new one.
- Pass `{ processPostponed = true }` (5th arg) when the message may arrive before your listener
  registers (login/session responses at connect time): CSP replays buffered TCP messages on the
  next frame. Without it the packet raced your registration and is simply gone.
- `sender == nil` → from the server; `sender.index == 0` → from this client. Client→server sends
  always use `target = 255` — fail-closed: a layout drift kills your own connection instead of
  broadcasting the payload to every player.
- Payload style: one delimited string field (`"a|b|c|..."`) parsed in Lua. The field list INSIDE
  the string may grow freely (only the Lua parser reads it); the packet layout — key, field names,
  sizes — is the contract. Appending an optional trailing field keeps old parsers working.

## Remote audio (and the one-shot trap)

- `ac.AudioEvent.fromFile({ filename = "<URL>", use3D = false, loop = false }, false)` **accepts a
  URL** — measured in production; the docs only promise URL support for images. MP3 decodes
  natively (FMOD): no WAV conversion step.
- An emitter created with `loop = false` becomes **invalid after playing once** (the doc warns:
  "audio event will become invalid once played once"). Reusing it = sound plays exactly once, then
  silence forever. Dispose the spent emitter and create a fresh one per shot — the FILE stays
  cached ("consequent calls with the same parameters would reuse previously loaded audio file");
  only the emitter is rebuilt.
- `dispose()` means "stop and remove": re-triggering the same sound rapidly cuts the previous
  instance. Fine for UI sounds with a natural minimum interval; only pool emitters if a real
  overlap case exists.
- `event.volume` is 0..1 — clamp config input. `use3D = false` for UI sounds (no world position,
  no doppler).
- **Sound is decoration.** Wrap load AND `start()` in `pcall`; a 404, bad format or sandbox
  failure must degrade to silence — never block or delay the visual.
- Calibrate loudness by **frequency of the trigger**, not by how good the sound is in isolation:
  the event that fires on every attempt gets the softest cue; the rare summit event may be the
  dramatic one. Inverting this makes players mute the feature.

## Local telemetry

- Your own car is NOT `ac.getSim().focusedCar` — that is the **camera** (wrong under spectator or
  track cam). Scan `0 .. sim.carsCount-1` for `car.isUserControlled and not car.isRemote`, cache
  the index, re-validate on use.
- `ac.onCarCollision(carIndex, cb)` fires once per collision start, for walls AND cars. Register
  with `-1` (all cars) and filter by your own index inside the callback — avoids the boot-time
  ordering problem when your index is not resolved yet.
- Guard `speedKmh` against NaN/infinity before integrating (`v ~= v` catches NaN).
- When mirroring a server-side metric (speed floor, reset-on-collision), copy the **exact** rules
  so the live number converges to the authoritative score — and state in a comment which number is
  authoritative, because frame-rate sampling vs server-rate sampling will differ in the last digit.

## Workflow — mockup first, probes when sight is not enough

- **You cannot render CSP outside the game.** Iterate the visual in an HTML mockup first, get it
  approved, then translate to Lua taking values FROM the mockup — `em × font-size → px`, flex
  gaps/margins → explicit px gaps, exact hexes. Never translate by eye: every eyeballed value is
  one more in-game round-trip.
- **Validate Lua syntax before every deploy** with a real parser (a Python `luaparser` venv works
  when `luac` is not installed). A syntax error otherwise only manifests in-game, as a silently
  missing overlay.
- **When behavior is in doubt, ship a temporary probe:** the script reports what it could do
  (capability flags, load results, errors) to the server via a client→server packet; the plugin
  just logs it. This turns "the player saw nothing" into data that separates rule-failure (never
  pushed) from render-failure (pushed, not drawn). Config-gate the probe, default off, remove or
  disable after the investigation. Mind probe blind spots: a sticky boolean cannot prove
  repetition — count occurrences when repetition is the question.
- **Overlay stacking is a convention, not a mechanism.** Separate scripts cannot negotiate layout
  at runtime; y-offsets couple silently. Document the column (e.g. logo → live strip → toast) at
  every coupling site and re-check the whole column whenever any member's height changes — heights
  derived from font metrics move when text sizes do.
- Keep test/debug chat commands behind config flags, default **off** in production; they are how
  you validate visuals and sounds without driving laps.

## See also

- `assettoserver-plugin` — the C# side: registering scripts and configValues (InvariantCulture
  decimals), packet classes and handlers, chat commands, the publish rite.
- `assettoserver-ops` — operating the server that hosts these scripts; static assets under
  `wwwroot/` are baked into the image (rebuild + recreate, not restart).
- `bug-hunter` — `references/track-dotnet-plugin.md`: the published-DLL inspection that enforces
  Lua↔C# packet parity.
- `conventional-commit` — commit format used by these repos.
