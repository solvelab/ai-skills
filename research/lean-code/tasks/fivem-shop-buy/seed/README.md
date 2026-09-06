# shop

FiveM resource. Load order is explicit in `fxmanifest.lua`; shared helpers live in
`shared/helpers.lua` (`Helpers.clampNum`, `Helpers.reject`), the server-side ledger in
`server/inventory.lua` (`Inventory.give` is the only way stock enters a player). The catalogue and
per-purchase limits are in `config.lua`.
