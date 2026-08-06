---
name: k8s-tune-resources
description: >-
  Bulk-edit Kubernetes resource requests/limits across many git repos discovered from the pods running
  on nodes with a given label. For each pod it derives the repo name from the image, clones it, checks
  out a target branch, patches the chart values files with a sed pair, then commits and pushes. Use
  when the user asks to "tune", "reduce", "scale down" or "ajustar resources" of pods on nodes selected
  by a label across multiple repos. This skill pushes to many repositories at once — it runs dry by
  default and requires an explicit opt-in to push. Do NOT use for editing a single repo (edit it
  directly) or for live `kubectl patch` changes that bypass GitOps.
metadata:
  author: solvelab
  version: 2.0.0
  category: devops
license: MIT
compatibility: Requires kubectl with a context on the target cluster, git, and push access to the repos.
---

Read and follow all instructions in ~/ai-skills/skills/k8s-tune-resources/SKILL.md
