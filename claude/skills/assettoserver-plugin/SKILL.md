---
name: assettoserver-plugin
description: >-
  Conventions for writing C#/.NET plugins for the AssettoServer runtime (compujuckel/AssettoServer,
  the CSP-aware Assetto Corsa dedicated server), distilled from a production DriveZone plugin. Use
  when creating or reviewing an AssettoServer plugin — AssettoServerModule entrypoint, plugin YAML
  config, Qmmands chat commands (ACModuleBase), ChatMessage packets, IHostedService lifecycle,
  calling an external backend from inside the runtime, or publishing for the plugin
  AssemblyLoadContext. Covers the runtime's forbidden constructs (command-module DI,
  System.Threading.Lock) and the bug-hunter gate that enforces them. Do NOT use for stock acServer
  configuration or server operation (that is assettoserver-ops), FiveM/CitizenFX resources (that is
  fivem-lua), or general .NET services.
metadata:
  author: solvelab
  version: 1.1.0
  category: game
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/assettoserver-plugin/SKILL.md

Reference files are in ~/ai-skills/skills/assettoserver-plugin/references/ — read them when the skill instructions point to them.
