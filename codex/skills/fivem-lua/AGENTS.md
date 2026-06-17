# FiveM Lua Skill

Conventions for FiveM (CitizenFX) server/client Lua resources: client-never-trusted boundary,
explicit fxmanifest order, no busy loops, module-per-global, NUI focus/cleanup, natives.

## When to use

FiveM/FXServer Lua work — RegisterNetEvent/RegisterNUICallback, fxmanifest, exports, NUI, threads,
StateBags, natives. Not for react-three-fiber or non-FiveM Lua.

## Instructions

@../../shared/skills/fivem-lua/content.md
