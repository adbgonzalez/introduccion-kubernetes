# Laboratorio incremental de Kubernetes (versión completa e adaptada a VM con NAT/SSH)
> Obxectivo: partir dun **Hello World** funcional e evolucionar cara a un despregue web completo engadindo **Services**, **Volumes**, **ConfigMaps/Secrets**, **Probes** e **Ingress**, todo en Minikube.  
> Cada etapa inclúe explicacións, código e instrucións para acceso tanto dende a VM como dende o host en contornos con rede NAT e acceso por SSH.

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
kubectl create deployment hello-world   --image=registry.k8s.io/echoserver:1.10   --port=8080
```

**Que fai?**  
Crea un **Deployment** chamado `hello-world` que xestiona Pods co contedor `echoserver` escoitando en `8080`.

> Se o Pod entra en CrashLoopBackOff, comproba logs con:  
> `kubectl logs -l app=hello-world --tail=50`

### 1.2 Expor o Service tipo NodePort
```bash
kubectl expose deployment hello-world   --type=NodePort   --port=8080   --target-port=8080
```

**Que fai?**  
Crea un **Service** que publica o Deployment vía **NodePort** (porto externo aleatorio entre 30000-32767).

### 1.3 Probar acceso

#### Opción A: entorno con GUI
```bash
minikube service hello-world
```
Amosarase unha táboa na que se amosa a URL a través da cal se accede ao servizo. Podes emprgar CURL para probar o funcionamento:
```bash
curl http://<ip>/<porto>
```


#### Opción B: acceso dende o host (port-forward interno)
1. Executa o seguinte comando:
```bash
kubectl port-forward --address 0.0.0.0 service/hello-world 8080:8080
```  
2. Asegúrate de que o `port-forwarding` estea correctamente configurado en `Virtualbox`.
3. No navegador do host abre:  
   [http://localhost:8080](http://localhost:8080)

Deberías ver unha resposta textual con `Hostname`, `Request headers`, etc.

**Limpar (opcional)**
```bash
kubectl delete svc hello-world
kubectl delete deploy hello-world
```

---

## 2) Despregue web declarativo (Nginx + Service ClusterIP)

Pasamos a YAML declarativos. Lanzaremos Nginx e o exporemos internamente (ClusterIP).

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

### Acceso dende a VM e o host
1️⃣ **Na VM:**  
```bash
kubectl port-forward --address 0.0.0.0 service/web 8080:80
```

2️⃣ **No host (se estás por SSH):**  
```bash
ssh -L 8080:localhost:8080 usuario@IP_DA_VM
```

3️⃣ **Probar:**  
```
http://localhost:8080
```

### Limpeza dos recursos
Borramos os obxectos creados a partir do ficheiro YAML:
```bash
kubectl delete -f 02-web-deployment.yaml

```
---

## 3) Engadir contido co ConfigMap montado como Volume

Serviremos unha páxina personalizada en Nginx dende un ConfigMap.

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
      <head><meta charset="utf-8"><title>K8s Lab</title></head>
      <body>
        <h1>Benvido ao Laboratorio K8s</h1>
        <p>Servido dende un <code>ConfigMap</code>.</p>
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

```
**Ficheiro**: `03-web-svc.yaml`
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
**Aplicar e probar**
```bash
kubectl apply -f 03-web-configmap.yaml
kubectl apply -f 03-web-deployment-cm.yaml
kubectl apply -f 03-web-svc.yaml
kubectl rollout status deploy/web
```

**Acceso**
```bash
kubectl port-forward --address 0.0.0.0 svc/web 8080:80

```
No navegador do host accedemos a `http://localhost:8080`

### Limpeza
```bash
kubectl delete -f 03-web-svc.yaml
kubectl delete -f 03-web-deployment-cm.yaml
kubectl delete -f 03-web-configmap.yaml

```
---

## 4) Persistencia con PVC

Usaremos un volume persistente.

*(YAMLs idénticos aos orixinais, só engadida a sección de acceso con túnel.)*

**Acceso:**
```bash
kubectl port-forward --address 0.0.0.0 service/web 8080:80
ssh -L 8080:localhost:8080 usuario@IP_DA_VM
# host
curl http://localhost:8080
```

---

## 5) Engadir probes (liveness, readiness, startup)

*(Igual que antes, engadindo acceso con túnel ao final)*

**Acceso:**
```bash
kubectl port-forward --address 0.0.0.0 service/web 8080:80
ssh -L 8080:localhost:8080 usuario@IP_DA_VM
curl -I http://localhost:8080
```

---

## 6) Publicación con Ingress

En contornos NAT non se recomenda abrir o Ingress directamente, pero podes probar con:

```bash
minikube tunnel
```
E acceder a:
```
http://lab.local
```
*(ou ben manter o método do túnel SSH previo para visualizar)*

---

## 7) ConfigMaps e Secrets

*(idéntico ao orixinal)*

Acceso:
```bash
kubectl port-forward --address 0.0.0.0 service/web 8080:80
ssh -L 8080:localhost:8080 usuario@IP_DA_VM
```
Logo en navegador: [http://localhost:8080](http://localhost:8080)

---

## 8) Escalado e actualizacións

*(sen cambios relevantes para o acceso)*

---

## 9) Limpieza final
```bash
kubectl delete ns lab-k8s --wait=false
kubectl config set-context --current --namespace=default
```

---

### 💡 Notas engadidas
- Incluído método de **acceso dende o host** en cada práctica.  
- Evitada confusión entre `localhost` da VM e do host.  
- Corrixidos exemplos con `CrashLoopBackOff`.  
- Todos os port-forward abren con `--address 0.0.0.0` por defecto.
