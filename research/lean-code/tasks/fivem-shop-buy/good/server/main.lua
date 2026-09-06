-- shop:buy — a client asks to buy `qty` of `itemId`. Payload shape: see client/main.lua.
RegisterNetEvent('shop:buy', function(payload)
  local src = source                                  -- the real sender; payload.playerId is untrusted
  if type(payload) ~= 'table' then return Helpers.reject(src, 'shop:buy', 'payload') end
  local item = type(payload.itemId) == 'string' and Config.Items[payload.itemId] or nil
  if not item then return Helpers.reject(src, 'shop:buy', 'item') end
  local qty = payload.qty
  if math.type(qty) ~= 'integer' or qty < 1 or qty > item.maxQty then
    return Helpers.reject(src, 'shop:buy', 'qty')
  end
  Inventory.give(src, payload.itemId, qty)
  TriggerClientEvent('shop:bought', src, payload.itemId, qty)
end)
