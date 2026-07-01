# Helm Migration — Real Examples

Reference examples of source YAML files and their expected values.yaml and env.yaml output.
Use these as ground truth when generating output for users.

---

## Example 1: DaemonSet with initContainers

### Source YAML
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: your-agent
spec:
  template:
    spec:
      tolerations:
        - key: "node-role"
          operator: "Exists"
      initContainers:
        - name: wait-for-dependency
          image: your-registry/your-app:busybox-version
          fixedNameImage: true
          command: [sh, -c]
          args:
            - 'while ! nc -z $ENDPOINT $PORT; do sleep 2; done'
          env:
            - name: ENDPOINT
              value: "your-dependency-service"
            - name: PORT
              value: "9200"
      containers:
        - name: your-app
          image: your-registry/your-app:version
          ports:
            - containerPort: 5775
              protocol: UDP
            - containerPort: 6831
              protocol: UDP
```

### Generated values.yaml
```yaml
##############################
# App Definition
app: your-agent
component: telemetry

##############################
# Definition of the DaemonSet
daemonset:
  revisionHistoryLimit: 3
  annotations:
    reloader.stakater.com/auto: "true"
  affinity:
    - apps:
        - base
  initContainers:
    - name: wait-for-dependency
      fixedNameImage: true
      image: your-registry/your-app:busybox-version
      command:
        - sh
        - -c
      args:
        - 'while ! nc -z $ENDPOINT $PORT; do sleep 2; done'
      env:
        - name: ENDPOINT
          value: "your-dependency-service"
        - name: PORT
          value: "9200"
  containers:
    - name: your-app
      fixedNameImage: true
      image: your-registry/your-app:version
      ports:
        - name: "port-one"
          number: 5775
          protocol: UDP
        - name: "port-two"
          number: 6831
          protocol: UDP
      envFrom:
        - configMapRef:
            name: cm-your-app
# Note: tolerations were removed per project standards
```

### Generated env.yaml
```yaml
##############################
# Definition of the ConfigMap
configmap:
  - name: cm-your-app
    namespace: your-namespace
    labels:
      app: your-agent
      component: telemetry
    data:
      TZ: "America/Sao_Paulo"
```

---

## Example 2: Deployment with secretKeyRef and commented resource limits

### Source YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: your-app
spec:
  replicas: 1
  template:
    spec:
      tolerations:
        - key: "dedicated"
          operator: "Exists"
      containers:
        - name: your-app
          image: your-registry/your-app:1.0.0
          ports:
            - containerPort: 3001
          resources:
            requests:
              memory: "128Mi"
              cpu: "50m"
            # limits:
            #   memory: "512Mi"
            #   cpu: "1"
          envFrom:
            - configMapRef:
                name: cm-your-app
          env:
            - name: API_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: s-your-app
                  key: API_SECRET_KEY
```

### Generated values.yaml
```yaml
##############################
# App Definition
app: your-app
component: api
version: 1.0.0

##############################
# Definition of the Deployment
deployment:
  replicas: 1
  revisionHistoryLimit: 3
  # Reloader: reinicia o pod automaticamente quando ConfigMap ou Secret for alterado
  annotations:
    reloader.stakater.com/auto: "true"
  strategy:
    type: Recreate
  containers:
    - name: your-app
      image: your-registry/your-app:1.0.0
      ports:
        name: "app"
        number: 3001
      resources:
        requests:
          memory: "128Mi"
          cpu: "50m"
        # limits:
        #   memory: "512Mi"
        #   cpu: "1"
      envFrom:
        - configMapRef:
            name: cm-your-app
      env:
        - name: API_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: s-your-app
              key: API_SECRET_KEY
# Note: tolerations were removed per project standards
```

### Generated env.yaml
```yaml
##############################
# Definition of the Secret
secret:
  - name: s-your-app
    namespace: your-namespace
    labels:
      app: your-app
      component: api
    type: Opaque
    data:
      API_SECRET_KEY: "" # ⚠️ Fill in the base64 encoded value before applying

##############################
# Definition of the ConfigMap
configmap:
  - name: cm-your-app
    namespace: your-namespace
    labels:
      app: your-app
      component: api
    data:
      TZ: "America/Sao_Paulo"
```

---

## Example 3: Deployment with PVC

### Generated env.yaml (PVC section)
```yaml
##############################
# Definition of the PVC
pvc:
  - name: your-app-data
    storageClassName: oci-bv
    accessModes:
      - ReadWriteOnce
    storage: 50Gi
```
