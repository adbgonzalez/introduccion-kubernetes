
# 📘 Introdución a Kubernetes

## ☁️ Que é a orquestración de contedores?

No desenvolvemento actual, os **contedores** permiten empaquetar unha aplicación coas súas dependencias, asegurando que se execute igual en calquera contorno. Pero cando se usan moitos contedores á vez (por exemplo nunha arquitectura de microservizos), necesitamos automatizar a súa xestión. Isto é o que fai a **orquestración de contedores**.

### Funcionalidades principais:
- Despregue automático de contedores.
- Escalado (máis ou menos instancias segundo carga).
- Supervisión e reinicio automático.
- Balanceo de carga.
- Actualizacións sen cortes de servizo (*rolling updates*).

---

## 🚀 Que é Kubernetes?

**Kubernetes** (ou *K8s*) é unha plataforma de código aberto desenvolvida inicialmente por Google e mantida pola CNCF. Automatiza o despregue, a escalabilidade e a operación de contedores.

---

## 🎯 Características principais de Kubernetes

- Automatización do despregue e escalado.
- Auto-reparación: reinicia contedores que fallan.
- *Rolling updates* e *rollbacks*.
- Balanceo de carga interno.
- Xestión de almacenamento persistente (PVs/PVCs).
- Configuracións e segredos de forma segura (ConfigMaps e Secrets).
- Declaración de infraestrutura vía ficheiros YAML.
- Portabilidade entre provedores cloud e contornos locais.

---

# ⚙️ Arquitectura de Kubernetes

## 📌 Elementos principais

- **Control Plane (nó mestre)**:
  - `kube-apiserver`: API central de control.
  - `scheduler`: decide en que nodo vai cada Pod.
  - `controller-manager`: xestiona eventos.
- **Worker Nodes (nós de traballo)**:
  - `kubelet`: comunica co Control Plane.
  - `kube-proxy`: reenvío de tráfico.
  - *Container Runtime* (ex: Docker, containerd).

---

## 🧱 Recursos fundamentais

| Elemento | Descrición |
|----------|------------|
| `Pod` | Unidade mínima que executa contedores. |
| `Deployment` | Xestiona réplicas e actualizacións de Pods. |
| `Service` | Expón Pods como un servizo accesible. |
| `Namespace` | Aisla grupos de recursos. |
| `ConfigMap` | Gardado de configuracións non sensibles. |
| `Secret` | Gardado de datos sensibles (tokens, contrasinais). |
| `Volume` e `PersistentVolumeClaim (PVC)` | Gardan datos persistentes. |

---

# 🧪 Primeiro exemplo: Hello World

## 🔧 Requisitos

- Instalar `minikube` e `kubectl`.

```bash
minikube start
```

### 1. Crear un Deployment

```bash
kubectl create deployment hello-world --image=k8s.gcr.io/echoserver:1.4
```

### 2. Expor o servizo

```bash
kubectl expose deployment hello-world --type=NodePort --port=8080
```

### 3. Acceder ao servizo

```bash
minikube service hello-world
```

---

# 🏗️ Exemplo máis complexo: app web + backend + base de datos

## 📦 Compoñentes:

- **MySQL** como base de datos.
- **Backend API** (Flask/Express) que accede á BD.
- **Frontend** (HTML/JS) que consome a API.
- **Services** que conectan os compoñentes.
- **Volumes** para persistencia.

---

# 🧠 Introdución ás probes

## 🔎 Liveness Probe

- Comproba se o contedor está **vivo**.
- Se falla, Kubernetes **reinicia** o contedor.

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 5
```

## 🔁 Readiness Probe

- Comproba se o contedor está **listo para recibir tráfico**.
- Se falla, **non se enruta tráfico ao Pod**.

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 3
```

## 🧪 Tipos de probes soportadas

- `httpGet`
- `exec`
- `tcpSocket`

---

## ✅ Ventaxas do uso de probes

- Maior dispoñibilidade e fiabilidade.
- Despregue máis robusto.
- Detección automática de fallos.

---

💡 Continuaremos con ficheiros YAML, Dockerfiles e código base adaptado. 
