-- Minimal shim of the CitizenFX server runtime, enough to load a resource's server scripts under
-- plain `lua` and fire a net event with a chosen `source`. Not a FiveM emulator: no natives beyond
-- the ones listed, no scheduler, no msgpack round-trip.
Stub = { handlers = {}, clientEvents = {} }

source = 0

function RegisterNetEvent(name, fn)
  if fn then Stub.handlers[name] = fn end
end

function RegisterServerEvent(name, fn)
  if fn then Stub.handlers[name] = fn end
end

function AddEventHandler(name, fn)
  Stub.handlers[name] = fn
end

function TriggerClientEvent(name, target, ...)
  Stub.clientEvents[#Stub.clientEvents + 1] = { name = name, target = target, args = { ... } }
end

function TriggerEvent(name, ...)
  local h = Stub.handlers[name]
  if h then return h(...) end
end

function RegisterCommand() end
function CreateThread(fn) end
function SetTimeout() end
function Wait() end
function DropPlayer() end
function GetPlayerName(src) return 'player' .. tostring(src) end
function GetPlayerIdentifiers() return {} end
function GetPlayers() return {} end
function GetCurrentResourceName() return 'shop' end
function GetResourceState() return 'started' end
function GetGameTimer() return 0 end
function IsDuplicityVersion() return true end
function GetConvar(_, default) return default end

--- Fire a net event as if it came from server id `src`. Returns pcall's results.
function Stub.fire(name, src, ...)
  source = src
  local h = Stub.handlers[name]
  if not h then return false, 'no handler registered for ' .. name end
  return pcall(h, ...)
end
