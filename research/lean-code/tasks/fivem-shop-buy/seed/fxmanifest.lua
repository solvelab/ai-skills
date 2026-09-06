fx_version 'cerulean'
game 'gta5'
lua54 'yes'

description 'shop — buy items from the server-side catalogue'

shared_scripts {
  'config.lua',
  'shared/helpers.lua',
}

server_scripts {
  'server/inventory.lua',
  'server/main.lua',
}

client_scripts {
  'client/main.lua',
}
