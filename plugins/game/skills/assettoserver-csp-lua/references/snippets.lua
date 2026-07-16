-- Copy-paste helpers for CSP online scripts (ac_online_script context).
-- Each block names the trap it defuses; see SKILL.md for the full doctrine.
-- All snippets are context-free: paste, rename, wire your own config/colors.

-- ===========================================================================
-- UTF-8 (trap: string.upper/string.sub are ASCII/byte-wise; LuaJIT has no utf8 lib)
-- ===========================================================================

-- Split into UTF-8 codepoints. Byte-wise iteration cuts accents in half.
local function utf8chars(s)
  local out, i, n = {}, 1, #s
  while i <= n do
    local b = string.byte(s, i)
    local size = 1
    if b >= 240 then size = 4
    elseif b >= 224 then size = 3
    elseif b >= 192 then size = 2 end
    out[#out + 1] = string.sub(s, i, i + size - 1)
    i = i + size
  end
  return out
end

-- Uppercase covering Latin-1 Supplement: lowercase à..þ are 0xC3 0xA0..0xBE and
-- uppercase À..Þ are 0xC3 0x80..0x9E — subtract 0x20, skipping 0xB7 (÷, not a letter).
-- Plain string.upper would produce "JOSé".
local function upperUtf8(s)
  local out = {}
  for _, ch in ipairs(utf8chars(s)) do
    if #ch == 1 then
      out[#out + 1] = string.upper(ch)
    elseif #ch == 2 then
      local b1, b2 = string.byte(ch, 1, 2)
      if b1 == 195 and b2 >= 160 and b2 <= 190 and b2 ~= 183 then
        out[#out + 1] = string.char(b1, b2 - 32)
      else
        out[#out + 1] = ch
      end
    else
      out[#out + 1] = ch
    end
  end
  return table.concat(out)
end

-- ===========================================================================
-- DirectWrite text with letter-spacing
-- (traps: no native tracking; trailing space discarded at measure AND draw;
--  measuring " " alone returns 0)
-- ===========================================================================

-- Draw with per-character tracking. With `color` nil it only measures (returns width).
-- Spacing in px = mockup's letter-spacing em × font size.
local function spacedText(x, y, s, color, size, spacing)
  ui.pushDWriteFont("Segoe UI;Weight=Bold")
  local blank = ui.measureDWriteText("A A", size).x - ui.measureDWriteText("AA", size).x
  local cx = x
  for _, ch in ipairs(utf8chars(s)) do
    if ch == " " then
      cx = cx + blank + spacing
    else
      if color ~= nil then
        ui.setCursor(vec2(cx, y))
        ui.dwriteText(ch, size, color)
      end
      cx = cx + ui.measureDWriteText(ch, size).x + spacing
    end
  end
  ui.popDWriteFont()
  return math.max(0, cx - x - spacing)
end

local function spacedWidth(s, size, spacing)
  return spacedText(0, 0, s, nil, size, spacing)
end

-- Ellipsis truncation on CODEPOINT boundaries (byte-wise sub breaks accents mid-glyph).
local function fitSpaced(s, maxW, size, spacing)
  if spacedWidth(s, size, spacing) <= maxW then return s end
  local chars = utf8chars(s)
  while #chars > 1 do
    table.remove(chars)
    local candidate = table.concat(chars) .. "..."
    if spacedWidth(candidate, size, spacing) <= maxW then return candidate end
  end
  return "..."
end

-- ===========================================================================
-- Metric line: big bold numbers + small muted units, base-aligned
-- (trap: segments separated by embedded trailing spaces glue together — use px gaps)
-- ===========================================================================

local GAP_NUM_UNIT, GAP_UNIT_SEP, GAP_SEP_NUM = 3, 6, 5  -- from the mockup's flex margins

local function drawMetric(x, y, bigSize, smallSize, numColor, unitColor, distText, unitText, avgText)
  ui.pushDWriteFont("Segoe UI;Weight=Bold")
  -- base-align small text against big text (glyph boxes differ in height)
  local dy = ui.measureDWriteText("0", bigSize).y - ui.measureDWriteText("0", smallSize).y
  local cx = x
  local function seg(text, big, gapAfter)
    local size = big and bigSize or smallSize
    ui.setCursor(vec2(cx, big and y or (y + dy)))
    ui.dwriteText(text, size, big and numColor or unitColor)
    cx = cx + ui.measureDWriteText(text, size).x + (gapAfter or 0)
  end
  seg(distText, true, GAP_NUM_UNIT)
  seg(unitText, false, GAP_UNIT_SEP)
  seg("\194\183 m\195\169dia", false, GAP_SEP_NUM)  -- "· média" via explicit UTF-8 escapes
  seg(avgText, true, GAP_NUM_UNIT)
  seg("km/h", false)
  ui.popDWriteFont()
end

-- ===========================================================================
-- Layout derived from REAL font metrics
-- (trap: a 30px "0" occupies ~40px of height — fixed stacked y offsets overlap)
-- ===========================================================================

local metrics = nil
local function layout(sizeLabel, sizeNum, sizePilot, padTop, padBottom, gapA, gapB)
  if metrics ~= nil then return metrics end
  ui.pushDWriteFont("Segoe UI;Weight=Bold")
  local hLabel = ui.measureDWriteText("0", sizeLabel).y
  local hNum   = ui.measureDWriteText("0", sizeNum).y
  local hPilot = ui.measureDWriteText("0", sizePilot).y
  ui.popDWriteFont()
  if hNum <= 0 then return nil end  -- font not ready this frame: retry next, don't cache zeros
  local m = {}
  m.yLabel = padTop
  m.yNum   = m.yLabel + hLabel + gapA
  m.yPilot = m.yNum + hNum + gapB
  m.height = m.yPilot + hPilot + padBottom
  metrics = m
  return m
end

-- ===========================================================================
-- Single-window toast skeleton: rounded panel + clipped accent bar
-- (traps: stacked transparentWindows don't stratify — the empty-box bug;
--  opposite CornerFlags leave square "teeth" — clip instead)
-- ===========================================================================

local function drawToast(pos, w, h, accent, panel, drawContent)
  ui.transparentWindow("my_toast", pos, vec2(w, h), true, false, function()
    ui.drawRectFilled(vec2(0, 0), vec2(w, h), panel, 12)
    ui.pushClipRect(vec2(0, 0), vec2(4, h), true)          -- overflow:hidden equivalent
    ui.drawRectFilled(vec2(0, 0), vec2(w, h), accent, 12)  -- accent follows the corner curve
    ui.popClipRect()
    pcall(drawContent)  -- decoration never kills the script
  end)
end

-- ===========================================================================
-- One-shot audio by URL
-- (traps: loop=false emitter is INVALID after one play — dispose + recreate;
--  the FILE stays cached, only the emitter is rebuilt; sound must degrade to silence)
-- ===========================================================================

local emitters = {}
local function playSound(baseUrl, fileName, volume)
  pcall(function()
    local spent = emitters[fileName]
    if spent ~= nil then
      emitters[fileName] = nil
      pcall(function() spent:dispose() end)  -- "stop and remove"
    end
    local event = ac.AudioEvent.fromFile({
      filename = baseUrl .. fileName,  -- URL accepted (measured; docs only promise it for images)
      use3D = false,                   -- UI sound: no world position, no doppler
      loop = false,
    }, false)
    if event == nil or not event:isValid() then return end
    event.volume = math.max(math.min(volume or 0.6, 1), 0)
    emitters[fileName] = event
    event:start()
  end)
end

-- ===========================================================================
-- Probe pattern: report capability/results to the server log
-- (trap: "the player saw/heard nothing" cannot distinguish rule-failure from
--  render-failure — make the client tell the server what it could do)
-- ===========================================================================

-- NEVER name a field `key` (collides with ac.StructItem.key: packet silently undelivered).
local sendProbe = ac.OnlineEvent({
  ac.StructItem.key("myplugin.audio.probe"),
  data = ac.StructItem.string(192),
}, function() end)

local function reportProbe(result)          -- result: short "k=v|k=v" string
  pcall(function() sendProbe({ data = result }, nil, 255) end)  -- 255 = server, fail-closed
end

-- ===========================================================================
-- Own car + collision hook
-- (traps: sim.focusedCar is the CAMERA, wrong under spectator; register collisions
--  with -1 and filter, so boot-time index resolution can't race the hook)
-- ===========================================================================

local ownIndex = -1
local function ownCar()
  if ownIndex >= 0 then
    local cached = ac.getCar(ownIndex)
    if cached ~= nil and cached.isUserControlled then return cached end
    ownIndex = -1
  end
  local sim = ac.getSim()
  if sim == nil then return nil end
  for i = 0, math.max(sim.carsCount, 1) - 1 do
    local car = ac.getCar(i)
    if car ~= nil and car.isUserControlled and not car.isRemote then
      ownIndex = i
      return car
    end
  end
  return nil
end

ac.onCarCollision(-1, function(carIndex)
  if ownIndex < 0 or carIndex ~= ownIndex then return end
  -- your reset-on-collision logic here (mirror the server's exact rules)
end)
