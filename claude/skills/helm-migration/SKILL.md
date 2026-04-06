---
name: helm-migration
description: Converts Kubernetes YAML manifests to Helm values.yaml and env.yaml following your chart template structure. Use when user mentions "migrate to helm", "convert yaml to helm", "generate values.yaml", "helm migration", "yaml to helm", shares a Kubernetes YAML and asks for Helm output. Always removes tolerations. Always generates both files when applicable. Requires a local charts template repository.
metadata:
  author: your-org
  version: 2.0.0
  category: devops
license: MIT
compatibility: Requires a Helm charts template repository accessible on the local filesystem. Works best in Claude Code.
---

Read and follow all instructions in ~/ai-skills/shared/skills/helm-migration/content.md

Reference examples are in ~/ai-skills/shared/skills/helm-migration/references/examples.md — read them when generating output.
