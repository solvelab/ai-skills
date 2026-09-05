Helpers = Helpers or {}

--- Clamp a client-supplied number into [lo, hi]. `default` is what a missing or non-numeric value
--- becomes; pass it explicitly so a forged nil lands on a safe number.
function Helpers.clampNum(v, lo, hi, default)
  if type(v) ~= 'number' then return default end
  if v < lo then return lo end
  if v > hi then return hi end
  return v
end

--- Count and log a rejected client message so an attack does not look like a quiet server.
local rejects = {}
function Helpers.reject(src, event, reason)
  rejects[src] = (rejects[src] or 0) + 1
  print(('[sec] reject src=%s event=%s reason=%s count=%d'):format(src, event, reason, rejects[src]))
  return false
end
