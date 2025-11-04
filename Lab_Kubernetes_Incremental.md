# Laboratorio incremental de Kubernetes
> Obxectivo: partir dun **Hello World** e evolucionar cara a un despregue web completo engadindo **Services**, **Volumes**, **ConfigMaps/Secrets**, **Probes** e **Ingress**, todo en Minikube. Cada etapa inclúe explicacións e o código listo para executar.

---

## 0) Requisitos e preparación do entorno

1) **Minikube + kubectl** instalados (ver apuntamentos).  
2) Arrincar Minikube empregando Docker como driver (ou o que uses normalmente):

```bash
minikube delete || true
minikube start --driver=docker
```

3) (Recomendado) Activar **addons** que imos usar máis tarde:
```bash
minikube addons enable metrics-server
minikube addons enable ingress
```

4) Namespace de traballo:
```bash
kubectl create namespace lab-k8s || true
kubectl config set-context --current --namespace=lab-k8s
```

> Podes volver ao *namespace* por defecto con `kubectl config set-context --current --namespace=default`.

---

## 1) Hello World imperativo (Deployment + Service NodePort)

Nesta primeira etapa lanzamos un **echoserver** que devolve información da petición. Facémolo con comandos *imperativos* para ver resultados rápidos.

### 1.1 Crear o Deployment
```bash
kubectl create deployment hello-world \
  --image=registry.k8s.io/echoserver:1.10 \
  --port=8080
```

**Que fai?**  
- Crea un **Deployment** chamado `hello-world` que xestiona Pods co contedor `echoserver` escoitando en `8080`.
- O Deployment garante que sempre exista o número de réplicas desexado (por defecto 1).

### 1.2 Expor o Service tipo NodePort
```bash
kubectl expose deployment hello-world \
  --type=NodePort \
  --port=8080 \
  --target-port=8080
```

**Que fai?**  
- Crea un **Service** que publica o Deployment via **NodePort** (un porto alto no nodo).  
- Útil en Minikube para acceder dende o host.

### 1.3 Probar acceso
```bash
minikube service hello-world
```

**Verificación alternativa**
```bash
kubectl get svc hello-world
# Obter o nodo:porto e facer curl manualmente
```

**Limpar (opcional)**
```bash
kubectl delete svc hello-world
kubectl delete deploy hello-world
```

---

## 2) Despregue web declarativo (Nginx + Service ClusterIP)

Agora pasamos a **YAML declarativos**. Lanzaremos Nginx e o exporemos internamente (ClusterIP).

**Ficheiro:** `02-web-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25-alpine
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: "100m"
              memory: "64Mi"
            limits:
              cpu: "250m"
              memory: "128Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```

**Aplicar e verificar**
```bash
kubectl apply -f 02-web-deployment.yaml
kubectl get deploy,po,svc -l app=web
```

**Acceso en Minikube (tunel temporal)**
```bash
kubectl port-forward deploy/web 8080:80
# Noutro terminal:
curl -I http://localhost:8080
```

---

## 3) Engadir contido co ConfigMap montado como Volume

Queremos servir unha páxina personalizada en Nginx. Usamos un **ConfigMap** cun `index.html` e montámolo como **volume** de só lectura.

**Ficheiro:** `03-web-configmap.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-content
data:
  index.html: |
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>K8s Lab</title>
        <style>
          body { font-family: sans-serif; max-width: 60ch; margin: 3rem auto; }
          h1 { margin-bottom: .5rem; }
          code { background: #f3f3f3; padding: .1rem .3rem; border-radius: .25rem; }
        </style>
      </head>
      <body>
        <h1>Benvido ao Laboratorio K8s</h1>
        <p>Esta páxina lévase servindo dende un <code>ConfigMap</code> montado como volume nun contedor Nginx.</p>
      </body>
    </html>
```
**Ficheiro:** `03-web-deployment-cm.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25-alpine
          ports:
            - containerPort: 80
          volumeMounts:
            - name: web-root
              mountPath: /usr/share/nginx/html
      volumes:
        - name: web-root
          configMap:
            name: web-content
            items:
              - key: index.html
                path: index.html
```
> Nota: ao montar o ConfigMap en `/usr/share/nginx/html`, o contido por defecto da imaxe substitúese polo do ConfigMap.

**Aplicar e probar**
```bash
kubectl apply -f 03-web-configmap.yaml
kubectl apply -f 03-web-deployment-cm.yaml
kubectl rollout status deploy/web
kubectl port-forward deploy/web 8080:80
# Noutro terminal:
curl http://localhost:8080
```

---

## 4) Persistencia con PVC (PersistentVolumeClaim)

Para contido editable (logs, subida de ficheiros, etc.) usaremos un **PVC**. En Minikube adoita existir un *storage class* por defecto que provisiona PVs dinámicos.

**Ficheiro:** `04-web-pvc.yaml`
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: web-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

**Ficheiro:** `04-web-deployment-pvc.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25-alpine
          ports:
            - containerPort: 80
          volumeMounts:
            - name: web-data
              mountPath: /usr/share/nginx/html
      volumes:
        - name: web-data
          persistentVolumeClaim:
            claimName: web-pvc
```

**Aplicar e poblar contido**  
Para escribir un `index.html` no volume compartido, lanzamos un **Pod auxiliar** temporal que monte o mesmo PVC:

**Ficheiro:** `04-writer-pod.yaml`
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: writer
spec:
  restartPolicy: Never
  containers:
    - name: writer
      image: alpine:3.20
      command: ["/bin/sh", "-c"]
      args:
        - echo '<h1>Contido persistente en PVC</h1>' > /data/index.html && sleep 2;
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: web-pvc
```

**Aplicación e proba**
```bash
kubectl apply -f 04-web-pvc.yaml
kubectl apply -f 04-web-deployment-pvc.yaml
kubectl apply -f 04-writer-pod.yaml
kubectl wait --for=condition=Ready pod -l app=web --timeout=120s || true
kubectl port-forward deploy/web 8080:80
# Noutro terminal:
curl http://localhost:8080
```

> Explicación: agora o contido vive nun volume persistente, polo que as recreacións dos Pods **non** borran a páxina.

---

## 5) Engadir Probes (liveness, readiness, startup)

Para mellorar a dispoñibilidade, engadimos **probes**. En Nginx podemos sondar `/` por HTTP. Para exemplos máis realistas, as apps adoitan expor `/healthz` ou `/ready`.

**Ficheiro:** `05-web-probes.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25-alpine
          ports:
            - containerPort: 80
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 5
          startupProbe:
            httpGet:
              path: /
              port: 80
            failureThreshold: 30
            periodSeconds: 5
```

**Aplicar e observar**
```bash
kubectl apply -f 05-web-probes.yaml
kubectl describe pod -l app=web | less
```

> Se a *readiness* falla, o Pod non recibe tráfico; se a *liveness* falla, o contedor reiníciase; a *startup* dá marxe ao arranque.

---

## 6) Publicación externa con Ingress

Exporemos o servizo Nginx fóra do clúster usando **Ingress** (co *Ingress Controller* de Minikube).

1) Comprobar que o addon está activo:
```bash
minikube addons enable ingress
```

2) Crear un **Service** *estable* (por se modificaches antes):
**Ficheiro:** `06-web-svc.yaml`
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```

3) Crear o **Ingress**:
**Ficheiro:** `06-web-ingress.yaml`
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: lab.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 80
```

4) Resolver o DNS local cara ao Ingress (en Linux/macOS):
```bash
# Obter a IP do Ingress Controller (xeralmente a de minikube)
MINIKUBE_IP=$(minikube ip)
echo "$MINIKUBE_IP lab.local" | sudo tee -a /etc/hosts
```

5) Probar acceso:
```bash
curl -I http://lab.local/
```

> Explicación: o Ingress define regras HTTP nun único punto de entrada; o Controller programa o *routing* cara ao Service.

---

## 7) Variables de configuración (ConfigMap) e credenciais (Secret)

Agora engadimos configuración vía **env vars** e un **Secret** para ilustrar acceso a credenciais (p.ex., BBDD).

**Ficheiro:** `07-app-config.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_MESSAGE: "Ola dende ConfigMap"
```

**Ficheiro:** `07-app-secret.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  USERNAME: YWRtaW4=    # admin
  PASSWORD: c2VjcmV0    # secret
```

Para Nginx non as imos usar activamente, pero quedarán dispoñibles no contedor (útil se cambias a unha imaxe de app propia):

**Ficheiro:** `07-web-env.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25-alpine
          ports:
            - containerPort: 80
          envFrom:
            - configMapRef:
                name: app-config
            - secretRef:
                name: app-secret
```

**Aplicar**
```bash
kubectl apply -f 07-app-config.yaml
kubectl apply -f 07-app-secret.yaml
kubectl apply -f 07-web-env.yaml
kubectl exec -it deploy/web -- sh -c 'env | grep -E "APP_MESSAGE|USERNAME|PASSWORD" || true'
```

---

## 8) Escalado e actualizacións (HPA + Rolling Update)

### 8.1 Escalado manual
```bash
kubectl scale deployment web --replicas=4
kubectl get deploy web
```

### 8.2 Escalado automático con HPA
```bash
kubectl autoscale deployment web --min=2 --max=6 --cpu-percent=50
kubectl get hpa
```

> Requírese `metrics-server`. O HPA observa o uso de CPU/memoria e axusta réplicas.

### 8.3 Rolling Update e rollback
```bash
kubectl set image deployment/web nginx=nginx:1.27-alpine
kubectl rollout status deployment/web
# Se algo vai mal:
kubectl rollout undo deployment/web
```

---

## 9) Probas rápidas e utilidades

- **Logs**
```bash
kubectl logs -l app=web --tail=100
```

- **Acceso interactivo a un Pod**
```bash
kubectl exec -it deploy/web -- sh
```

- **Descrición detallada**
```bash
kubectl describe deploy web
kubectl describe svc web
kubectl describe ingress web
```

- **Limpieza final do laboratorio**
```bash
kubectl delete ns lab-k8s --wait=false
kubectl config set-context --current --namespace=default
```

---

## Árbore de ficheiros suxerida

```
lab-k8s/
├─ 02-web-deployment.yaml
├─ 03-web-configmap.yaml
├─ 03-web-deployment-cm.yaml
├─ 04-web-pvc.yaml
├─ 04-web-deployment-pvc.yaml
├─ 04-writer-pod.yaml
├─ 05-web-probes.yaml
├─ 06-web-svc.yaml
├─ 06-web-ingress.yaml
├─ 07-app-config.yaml
├─ 07-app-secret.yaml
├─ 07-web-env.yaml
└─ README.md  (este documento)
```

---

### Notas pedagóxicas (para clase)
- Alterna **imperativo** (comandos rápidos) con **declarativo** (YAML versionable).
- Introduce erros controlados (p.ex. romper a Readiness) para observar efectos no Service/Ingress.
- Amosa o reconcilio de Kubernetes: cambia `replicas` ou o `index.html` e observa os *rollouts*.
- Se queres ir máis alá: substitúe Nginx por unha pequena API (p.ex. `hashicorp/http-echo` ou unha imaxe propia) con rutas `/health` e `/ready` dedicadas.
