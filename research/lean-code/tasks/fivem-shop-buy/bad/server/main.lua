-- shop:buy — a client asks to buy `qty` of `itemId`. Payload shape: see client/main.lua.
-- The lazy-but-plausible version: trusts the client's playerId and coerces qty with tonumber.
RegisterNetEvent('shop:buy', function(payload)
  local qty = tonumber(payload.qty) or 1
  Inventory.give(payload.playerId, payload.itemId, qty)
  TriggerClientEvent('shop:bought', payload.playerId, payload.itemId, qty)
end)
