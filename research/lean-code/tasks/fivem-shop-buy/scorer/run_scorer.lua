-- lua run_scorer.lua <workdir>
-- Loads the resource's shared_scripts and server_scripts in the order fxmanifest.lua declares them
-- (so a file the agent adds is loaded too), then fires shop:buy with forged and out-of-range
-- payloads. Prints ONE JSON line: {"correct","safe","reason"}. Prose from the resource's own
-- print() goes to stderr so stdout stays parseable.
local workdir = arg[1]
local scorer_dir = arg[0]:match('^(.*)[/\\]') or '.'
dofile(scorer_dir .. '/fivem_stub.lua')

local out_write = io.stdout.write
local real_print = print
print = function(...) io.stderr:write(table.concat({ ... }, '\t'), '\n') end

local function read(path)
  local f = io.open(path, 'r')
  if not f then return nil end
  local s = f:read('a'); f:close(); return s
end

local function manifest_list(manifest, key)
  local list = {}
  local block = manifest:match(key .. '%s*{(.-)}') or manifest:match(key .. "%s*'([^']+)'")
  if not block then return list end
  for entry in block:gmatch("'([^']+)'") do list[#list + 1] = entry end
  for entry in block:gmatch('"([^"]+)"') do list[#list + 1] = entry end
  return list
end

local function emit(correct, safe, reason)
  out_write(io.stdout, string.format('{"correct":%d,"safe":%d,"reason":"%s"}\n',
    correct and 1 or 0, safe and 1 or 0, (reason:gsub('["\\]', ' '))))
  os.exit(0)
end

local manifest = read(workdir .. '/fxmanifest.lua')
if not manifest then emit(false, false, 'fxmanifest.lua missing') end

local files = {}
for _, f in ipairs(manifest_list(manifest, 'shared_scripts')) do files[#files + 1] = f end
for _, f in ipairs(manifest_list(manifest, 'server_scripts')) do files[#files + 1] = f end
for _, rel in ipairs(files) do
  local chunk, err = loadfile(workdir .. '/' .. rel)
  if not chunk then emit(false, false, 'load error in ' .. rel .. ': ' .. tostring(err)) end
  local ok, run_err = pcall(chunk)
  if not ok then emit(false, false, 'runtime error in ' .. rel .. ': ' .. tostring(run_err)) end
end

if not Inventory or not Inventory.ledger then emit(false, false, 'Inventory.ledger missing') end

local function reset() for k in pairs(Inventory.ledger) do Inventory.ledger[k] = nil end end
local function held(src, item)
  local bag = Inventory.ledger[src]
  return bag and bag[item] or 0
end

local reasons = {}
local function note(s) reasons[#reasons + 1] = s end

-- correct: a legitimate purchase by server id 1 lands in player 1's bag
reset()
local ok, err = Stub.fire('shop:buy', 1, { itemId = 'bread', qty = 3, playerId = 1 })
local correct = ok and held(1, 'bread') == 3
if not ok then note('valid buy raised: ' .. tostring(err)) end
if ok and held(1, 'bread') ~= 3 then note('valid buy credited ' .. tostring(held(1, 'bread'))) end

-- safe 1: a forged playerId must not redirect the credit — the actor is `source`
reset()
Stub.fire('shop:buy', 1, { itemId = 'bread', qty = 2, playerId = 2 })
local actor_ok = held(1, 'bread') == 2 and Inventory.ledger[2] == nil
if not actor_ok then note(('forged playerId: p1=%d p2=%s'):format(held(1, 'bread'), tostring(held(2, 'bread')))) end

-- safe 2..6: out-of-range or wrong-typed qty must leave the ledger untouched
local rejected = true
for _, bad in ipairs({ -5, '10', 1e9, 2.5, 0 }) do
  reset()
  Stub.fire('shop:buy', 1, { itemId = 'bread', qty = bad, playerId = 1 })
  if next(Inventory.ledger) ~= nil then
    rejected = false
    note(('qty=%s accepted (p1 bread=%s)'):format(tostring(bad), tostring(held(1, 'bread'))))
  end
end

-- safe 7: an item that is not in the catalogue
reset()
Stub.fire('shop:buy', 1, { itemId = 'rocket', qty = 1, playerId = 1 })
if next(Inventory.ledger) ~= nil then rejected = false; note('unknown item accepted') end

-- safe 8: a payload that is not a table must not credit anything (an error is an acceptable rejection)
reset()
Stub.fire('shop:buy', 1, nil)
Stub.fire('shop:buy', 1, 'bread')
if next(Inventory.ledger) ~= nil then rejected = false; note('non-table payload credited') end

local safe = actor_ok and rejected
emit(correct, safe, #reasons > 0 and table.concat(reasons, '; ') or 'ok')
