Inventory = Inventory or {}

-- [serverId] = { [itemId] = qty }. The server is authoritative: nothing else writes here.
Inventory.ledger = {}

--- Credit `qty` of `itemId` to the player with server id `src`. The only way stock enters a bag.
function Inventory.give(src, itemId, qty)
  local bag = Inventory.ledger[src] or {}
  bag[itemId] = (bag[itemId] or 0) + qty
  Inventory.ledger[src] = bag
end

--- How many of `itemId` player `src` holds.
function Inventory.count(src, itemId)
  local bag = Inventory.ledger[src]
  return bag and bag[itemId] or 0
end
