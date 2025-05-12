
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
# 📂 Descrición dos ficheiros YAML do proxecto Kubernetes

Esta sección recolle cada ficheiro necesario para despregar unha arquitectura web de tres capas (base de datos, backend e frontend), indicando a súa función e como se aplica en Kubernetes.

---

## 1️⃣ `mysql-pvc.yaml`

Solicita un volume persistente de 1GiB para garantir que os datos da base de datos MySQL non se perdan se o Pod se reinicia.

```bash
kubectl apply -f mysql-pvc.yaml
```

---

## 2️⃣ `mysql-deployment.yaml`

Crea un `Deployment` cun contedor de MySQL que utiliza o volume persistente. Define o contrasinal de root e o nome da base de datos mediante variables de contorno.

```bash
kubectl apply -f mysql-deployment.yaml
```

---

## 3️⃣ `mysql-service.yaml`

Crea un `Service` interno para que o backend poida comunicarse co Pod de MySQL usando o nome DNS `mysql`.

```bash
kubectl apply -f mysql-service.yaml
```

---

## 4️⃣ `backend-deployment.yaml`

Despregue da API (en Flask, por exemplo) que accede á base de datos. Inclúe:

- Variables de contorno para a conexión á BD.
- `livenessProbe` para saber se o contedor está vivo.
- `readinessProbe` para saber se está preparado para recibir tráfico.

```bash
kubectl apply -f backend-deployment.yaml
```

---

## 5️⃣ `backend-service.yaml`

Permite que outros Pods (coma o frontend) accedan ao backend mediante o nome DNS `backend`.

```bash
kubectl apply -f backend-service.yaml
```

---

## 6️⃣ `frontend-deployment.yaml`

Despregue dunha páxina web servida por Nginx que realiza chamadas ao backend.

```bash
kubectl apply -f frontend-deployment.yaml
```

---

## 7️⃣ `frontend-service.yaml`

Expón o frontend ao exterior mediante un `NodePort`, accesible dende o navegador.

```bash
kubectl apply -f frontend-service.yaml
```

---

# 🧪 Comprobación do estado do clúster

Comprobar os Pods e os Servizos:

```bash
kubectl get pods
kubectl get services
```

Acceder ao frontend:

```bash
minikube service frontend
# ou se usas NodePort:
minikube ip
# E visitar http://<IP>:30080 no navegador
```

---

# ✅ Despregue completo

```bash
kubectl apply -f mysql-pvc.yaml
kubectl apply -f mysql-deployment.yaml
kubectl apply -f mysql-service.yaml

kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```
# 📦 Dockerfiles para o proxecto Kubernetes

Este documento contén os `Dockerfile` para o backend (API en Flask) e o frontend (Nginx servindo HTML estático).

---

## 🖥️ Backend – API Flask

### 📁 Estrutura

```
backend/
├── app.py
├── requirements.txt
└── Dockerfile
```

### `Dockerfile`

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

### `requirements.txt`

```
Flask==2.2.5
mysql-connector-python==8.0.33
```

### `app.py` (resumo)

```python
from flask import Flask, jsonify
import os, mysql.connector

app = Flask(__name__)

@app.route('/health')
def health(): return "OK", 200

@app.route('/ready')
def ready():
    try:
        mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "appdb")
        ).close()
        return "Ready", 200
    except: return "Not ready", 500

@app.route('/data')
def get_data():
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "appdb")
        )
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS visitas (id INT AUTO_INCREMENT PRIMARY KEY)")
        c.execute("INSERT INTO visitas () VALUES ()")
        db.commit()
        c.execute("SELECT COUNT(*) FROM visitas")
        return jsonify({"visitas": c.fetchone()[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

---

## 🌐 Frontend – HTML estático con Nginx

### 📁 Estrutura

```
frontend/
├── index.html
└── Dockerfile
```

### `Dockerfile`

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
```

### `index.html` (exemplo)

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Frontend</title></head>
<body>
  <h1>Visitas á API</h1>
  <p id="contador">Cargando...</p>
  <script>
    fetch("/data")
      .then(r => r.json())
      .then(d => {
        document.getElementById("contador").innerText =
          d.visitas ? `Visitas: ${d.visitas}` : `Erro: ${d.error}`;
      })
      .catch(() => {
        document.getElementById("contador").innerText = "Erro ao conectar coa API";
      });
  </script>
</body>
</html>
```

---

## 🏗️ Construír as imaxes

```bash
# Backend
cd backend
docker build -t tuusuario/backend-app .

# Frontend
cd ../frontend
docker build -t tuusuario/frontend-app .
```

Logo podes subir as imaxes a Docker Hub para usalas en Kubernetes.
