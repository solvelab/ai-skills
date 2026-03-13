---
name: helm-migration
description: Converts Kubernetes YAML manifests to Helm values.yaml and env.yaml following your chart template structure. Use when user mentions "migrate to helm", "convert yaml to helm", "generate values.yaml", "helm migration", "yaml to helm", shares a Kubernetes YAML and asks for Helm output. Always removes tolerations. Always generates both files when applicable. Requires a local charts template repository.
metadata:
  author: your-org
  version: 1.0.0
  category: devops
license: MIT
compatibility: Requires a Helm charts template repository accessible on the local filesystem. Works best in Claude Code.
---

# Helm Migration Skill

You are a Helm chart expert. When asked to migrate a Kubernetes YAML file to Helm, follow the workflow and conventions below. These are derived from real your-org production charts.

---

## CRITICAL: Always Follow This Workflow

1. Ask the user for (if not already provided):
   - Path to the charts template repository
   - Path to the source YAML-file to migrate
   - Destination path to save the generated files

2. Read the charts template structure from the provided path
3. Read the source YAML-file carefully
4. Generate TWO files:
   - `values.yaml` — workload definition (daemonset, deployment, statefulset, cronjob, containers, ports, etc.)
   - `env.yaml` — environment resources (secrets, configmaps, PVCs)
5. Save both files to the destination path

NEVER mix workload config into env.yaml.
NEVER mix secrets/configmaps/PVCs into values.yaml.
If the source YAML has no secrets, configmaps or PVCs, do not generate env.yaml.

---

## Chart Template Conventions

These are your-org-specific conventions that differ from standard Kubernetes YAML.
Always apply them when generating values.yaml.

### Section Headers

Use comment blocks to separate major sections:
```yaml
##############################
# Section Name
```

### Workload Types

Detect from the source YAML kind and use the correct key:

| Source YAML kind | values.yaml key |
|---|---|
| DaemonSet | `daemonset:` |
| Deployment | `deployment:` |
| StatefulSet | `statefulset:` |
| CronJob | `cronjob:` |

### your-org-specific fields

These fields are specific to the your-org chart template — NOT standard Kubernetes:

| Field | Where | Description |
|---|---|---|
| `fixedNameImage: true` | containers, initContainers | Keeps the image name fixed — do not change |
| `affinity` | daemonset/deployment | Custom format: `- apps: base`. Do NOT convert to standard Kubernetes affinity format |
| `component` | root | Logical component label (e.g. telemetry, api, worker) |
| `version` | root | App version label — always include if present in source YAML |
| `ports[].number` | containers | Use `number` instead of `containerPort` |
| `ports[].name` | containers | Always include port name |
| `ports[].protocol` | containers | TCP or UDP — always explicit |
| `deployment.strategy` | deployment | Recreate or RollingUpdate — preserve exactly |
| `deployment.sendlogs` | deployment | your-org-specific flag for log shipping |
| `deployment.stack` | deployment | your-org-specific stack label |
| `deployment.lbtype` | deployment | Load balancer type (internal/external) |
| `deployment.podAntiAffinity` | deployment | Custom format with app + topologyKey |
| `deployment.hostAliases` | deployment | Preserve exactly — includes ip and hostnames |
| `deployment.imagePullSecrets` | deployment | Preserve exactly — list of secret names |
| `containers[].livenessProbe` | containers | Preserve exactly — tcpSocket, httpGet, or exec |
| `containers[].resources` | containers | Preserve requests. Keep commented-out limits as YAML comments |

### Ports format

`ports` can be a single object or a list — detect from source YAML and preserve the format:
```yaml
# Single port (object)
ports:
  name: "http"
  number: 3001

# Multiple ports (list)
ports:
  - name: "compact"
    number: 5775
    protocol: UDP
  - name: "binary"
    number: 6831
    protocol: UDP
```

### Resources with commented-out limits

When the source YAML has resource limits commented out, preserve the comments exactly:
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "50m"
  # limits:
  #   memory: "512Mi"
  #   cpu: "1"
```

Do NOT uncomment or remove limits. Preserve the commented block as-is.

### Tolerations

NEVER include tolerations in the generated values.yaml, even if present in the source YAML.
No exceptions. No comments. Just remove them entirely.

### Comments in values.yaml

Always add explanatory comments above each section:
```yaml
##############################
# App Definition
app: my-app
component: api

##############################
# Definition of the Deployment
deployment:
  # Reloader: reinicia o pod automaticamente quando ConfigMap ou Secret for alterado
  annotations:
    reloader.stakater.com/auto: "true"
```

### initContainers

Always preserve initContainers exactly as-is from the source YAML.
Keep `fixedNameImage`, `image`, `command`, `args`, and `env` intact.

### envFrom

Preserve all `envFrom` references (configMapRef, secretRef) exactly as they appear.
Do not inline the values — keep the reference.

---

## env.yaml Conventions

The `env.yaml` file stores environment resources separately from the workload definition.

### Structure
```yaml
##############################
# Definition of the Secret
secret:
  - name: my-app
    namespace: your-namespace
    labels:
      app: my-app
      component: api
    type: Opaque
    data:
      MY_SECRET_KEY: base64encodedvalue

##############################
# Definition of the ConfigMap
configmap:
  - name: my-app
    namespace: your-namespace
    labels:
      app: my-app
      component: api
    data:
      TZ: "America/Sao_Paulo"
      LOG_LEVEL: "info"

##############################
# Definition of the PVC
pvc:
  - name: my-app-data
    storageClassName: oci-bv
    accessModes:
      - ReadWriteOnce
    storage: 50Gi
```

### Rules for env.yaml

| Rule | Detail |
|---|---|
| Section order | Always: Secret → ConfigMap → PVC |
| Labels | Always include `app` and `component` matching the values.yaml |
| Namespace | Always explicit — never rely on defaults |
| Secret data | Keep base64 values as-is from source YAML. If plaintext, note it with a comment |
| ConfigMap data | Preserve all keys and values exactly |
| PVC | Include storageClassName, accessModes, and storage size |
| Missing sections | Only include sections that exist in the source YAML |
| Tolerations | Not applicable to env.yaml |

### What goes in each file

| Resource | File |
|---|---|
| Deployment / DaemonSet / StatefulSet / CronJob | `values.yaml` |
| Container definitions, ports, args, initContainers | `values.yaml` |
| envFrom references (configMapRef, secretRef) | `values.yaml` |
| env with secretKeyRef | `values.yaml` (reference stays) + `env.yaml` (secret entry) |
| Secret (data and type) | `env.yaml` |
| ConfigMap (data) | `env.yaml` |
| PersistentVolumeClaim | `env.yaml` |

### Secret referenced via secretKeyRef

When the source YAML references a secret inline via `secretKeyRef`:
```yaml
env:
  - name: YOUR_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: s-your-app
        key: YOUR_SECRET_KEY
```

Generate the secret entry in `env.yaml`:
```yaml
##############################
# Definition of the Secret
secret:
  - name: s-your-app
    namespace: your-namespace
    labels:
      app: my-app
      component: api
    type: Opaque
    data:
      YOUR_SECRET_KEY: "" # ⚠️ Fill in the base64 encoded value before applying
```

Rules:
- Extract secret name from `secretKeyRef.name`
- Extract key from `secretKeyRef.key` — use as field name in `secret.data`
- Set value as empty string with warning comment — never invent secret values
- Keep the `secretKeyRef` reference intact in `values.yaml`
- Group all keys under one secret entry when multiple vars reference the same secret name

---

## How to Use

Use this prompt to trigger the skill:
```
Migrate this YAML-file to Helm following the helm-migration skill.
Charts template path: [PATH_TO_CHARTS_TEMPLATE]
Source YAML-file: [PATH_TO_YAML_FILE]
Save files to: [DESTINATION_PATH]
```

Claude will generate:
- `values.yaml` — workload definition
- `env.yaml` — secrets, configmaps and PVCs (only if present in source YAML)

### Example
```
Migrate this YAML-file to Helm following the helm-migration skill.
Charts template path: /path/to/charts-template
Source YAML-file: /path/to/source/deployment.yaml
Save files to: /path/to/output/helm/
```

---

## Troubleshooting

**Problem**: Field exists in YAML but not in charts template.
**Solution**: Add to a `# Custom fields` section at the bottom of values.yaml with a comment explaining the origin.

**Problem**: Tolerations found in source YAML.
**Solution**: Always remove. No exceptions, no comments about removal.

**Problem**: Multiple containers in one YAML.
**Solution**: Generate one values.yaml covering all containers in the `containers` list. Ask user if unsure.

**Problem**: Source YAML has secrets referenced via `secretKeyRef` but no actual values.
**Solution**: Generate secret entry in env.yaml with empty values and comment `# ⚠️ Fill in the base64 encoded value before applying`. Never invent values.

**Problem**: Multiple env vars reference different secrets in the same container.
**Solution**: Generate one secret entry per unique `secretKeyRef.name`, grouping all keys correctly.

**Problem**: `ports` is a single object instead of a list.
**Solution**: Detect format from source YAML and preserve it — do not convert.

**Problem**: `resources.limits` is commented out in source YAML.
**Solution**: Preserve the commented-out block exactly. Do not uncomment or remove.

**Problem**: Source YAML has a PVC but no storage class defined.
**Solution**: Use `oci-bv` as default storageClassName and add comment `# storageClassName: verify before applying`.

**Problem**: Source YAML has both Secret and ConfigMap with the same name.
**Solution**: Valid — keep both in env.yaml, each in their own section.

**Problem**: Inline env vars mixed with secrets and configmaps.
**Solution**: Non-sensitive inline vars go to `configmap.data` in env.yaml. Sensitive values go to `secret.data`. References stay in values.yaml.

---

## References

See `references/examples.md` for complete before/after examples of:
- DaemonSet with initContainers
- Deployment with secretKeyRef and commented resource limits
- Deployment with PVC

---

## Trigger Test Cases

Should trigger on:
- "Migrate this YAML to Helm"
- "Convert this manifest to values.yaml"
- "Generate values.yaml for this deployment"
- "I need to helm-migrate this file"
- "Create env.yaml from this YAML"

Should NOT trigger on:
- "Update the README"
- "Fix this Python bug"
- "Create a docker-compose file"
- "Write documentation for this project"
