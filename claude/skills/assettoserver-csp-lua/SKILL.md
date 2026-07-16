---
name: assettoserver-csp-lua
description: >-
  Conventions for CSP Lua online scripts served by AssettoServer (CSPServerScriptProvider) — the
  zero-install in-game UI layer of an AC server: overlays/HUDs/toasts drawn with the draw-list API
  in a single transparentWindow, DirectWrite text, ac.OnlineEvent packets mirrored byte-for-byte
  with the C# plugin, remote images and audio loaded by URL from the server, local car telemetry,
  and the mockup-first workflow for visuals you cannot render outside the game. Distilled from a
  production DriveZone server. Use when writing or reviewing a .lua online script (overlay, HUD,
  toast, in-game sound, login UI), when a CSP overlay renders wrong (empty flat box, glued or
  overlapping text, missing glyphs, sound plays only once), or when an OnlineEvent packet silently
  never arrives. Do NOT use for the C# plugin side — packet classes, config, chat commands,
  publishing (that is assettoserver-plugin), for server configuration/deploy (that is
  assettoserver-ops), for CSP apps or track scripts (different Lua contexts with different
  permissions), or for FiveM Lua (that is fivem-lua).
metadata:
  author: solvelab
  version: 1.0.0
  category: game
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/assettoserver-csp-lua/SKILL.md

Reference files are in ~/ai-skills/skills/assettoserver-csp-lua/references/ — read them when the skill instructions point to them.
