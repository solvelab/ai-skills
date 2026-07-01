---
name: helm-migration
description: >-
  Converts Kubernetes YAML manifests to Helm values.yaml and env.yaml following the solvelab chart template structure — requires a local copy of that chart template repository (the template-specific fields do not exist in stock Helm charts). Use when user mentions "migrate to helm", "convert yaml to helm", "generate values.yaml", "helm migration", "yaml to helm", shares a Kubernetes YAML and asks for Helm output. Always removes tolerations. Always generates both files when applicable.
metadata:
  author: solvelab
  version: 2.1.0
  category: devops
license: MIT
compatibility: Requires a Helm charts template repository accessible on the local filesystem. Works best in Claude Code.
---

Read and follow all instructions in ~/ai-skills/skills/helm-migration/SKILL.md

Reference files are in ~/ai-skills/skills/helm-migration/references/ — read them when the skill instructions point to them.
