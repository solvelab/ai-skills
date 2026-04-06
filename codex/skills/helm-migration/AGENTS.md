# Helm Migration Skill

Converts Kubernetes YAML manifests to Helm values.yaml and env.yaml following your chart template structure.

## When to use

Use when user mentions "migrate to helm", "convert yaml to helm", "generate values.yaml", "helm migration", "yaml to helm", shares a Kubernetes YAML and asks for Helm output. Always removes tolerations. Always generates both files when applicable. Requires a local charts template repository.

## Metadata

| Field | Value |
|-------|-------|
| Author | your-org |
| Version | 2.0.0 |
| Category | devops |
| License | MIT |
| Compatibility | Requires a Helm charts template repository accessible on the local filesystem |

## Instructions

@../../shared/skills/helm-migration/content.md

## Reference Examples

@../../shared/skills/helm-migration/references/examples.md
