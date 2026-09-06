-- /buy <itemId> [qty]
RegisterCommand('buy', function(_, args)
  local itemId = args[1]
  local qty = tonumber(args[2]) or 1
  TriggerServerEvent('shop:buy', {
    itemId = itemId,
    qty = qty,
    playerId = GetPlayerServerId(PlayerId()),
  })
end, false)

RegisterNetEvent('shop:bought', function(itemId, qty)
  print(('bought %d x %s'):format(qty, itemId))
end)
