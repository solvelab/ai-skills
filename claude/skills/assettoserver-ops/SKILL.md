---
name: assettoserver-ops
description: >-
  Operating an AssettoServer (compujuckel) dedicated Assetto Corsa server, distilled from a
  production DriveZone deployment — server_cfg.ini / entry_list.ini / extra_cfg.yml anatomy,
  checksum and CSP mismatch troubleshooting, AI traffic enablement discipline, Docker/WSL2
  orchestration, and rite-gated plugin deployment. Use when configuring or diagnosing an AC
  dedicated server, enabling AI traffic, players fail to join (checksum mismatch, track version
  mismatch, missing car/skin), exposing the server on a LAN from WSL2, or syncing a plugin DLL to
  the runtime. Do NOT use for writing the plugin itself (that is assettoserver-plugin), for the
  backend receiving events (python-rest-api), or for FiveM servers.
metadata:
  author: solvelab
  version: 1.1.0
  category: devops
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/assettoserver-ops/SKILL.md

Reference files are in ~/ai-skills/skills/assettoserver-ops/references/ — read them when the skill instructions point to them.
