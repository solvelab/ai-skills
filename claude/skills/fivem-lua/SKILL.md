---
name: fivem-lua
description: Conventions for writing FiveM (CitizenFX) server/client Lua resources. Use when working on FiveM/FXServer Lua — RegisterNetEvent/RegisterNUICallback handlers, fxmanifest, exports, NUI (SendNUIMessage/SetNuiFocus), threads/CreateThread, StateBags, or natives. Enforces the client-is-never-trusted boundary (validate payload + derive actor from `source`), explicit fxmanifest order, no busy `while true` loops, module-per-global pattern, and NUI focus/disconnect cleanup. Do NOT use for react-three-fiber or non-FiveM Lua.
metadata:
  author: your-org
  version: 1.0.0
  category: fivem
license: MIT
compatibility: Works in any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/fivem-lua/SKILL.md
