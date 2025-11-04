# Laboratorio incremental de Kubernetes (versión actualizada)
> Obxectivo: partir dun **Hello World** funcional en contornos sen GUI (por exemplo, VM con NAT e SSH) e evolucionar cara a un despregue web completo engadindo **Services**, **Volumes**, **ConfigMaps/Secrets**, **Probes** e **Ingress**, todo en Minikube.

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

## 0 bis) Acceso dende VM sen interfaz gráfica

Se a túa máquina usa **rede NAT e só accedes por SSH**, non poderás abrir o navegador directamente con `minikube service`. Usa unha destas opcións:

### 🔹 Opción A — port-forward directo
```bash
kubectl port-forward --address 0.0.0.0 service/hello-world 8080:8080
```
Logo crea no hipervisor (VirtualBox/VMware) unha regra NAT:  
**Host port 8080 → Guest port 8080 (TCP)**

No host abre no navegador:
```
http://localhost:8080
```

### 🔹 Opción B — túnel SSH
```bash
kubectl port-forward --address 127.0.0.1 service/hello-world 8080:8080
```
No host:
```bash
ssh -L 8080:localhost:8080 usuario@IP_DA_VM
```
Logo no navegador:
```
http://localhost:8080
```

💡 Diferencias clave:
- `TargetPort`: porto dentro do contedor.  
- `NodePort`: porto externo do nodo (Minikube).  
- `localhost` na VM **non é o mesmo** que `localhost` no host.

---

## 1) Hello World imperativo (Deployment + Service NodePort)

Nesta primeira etapa lanzamos un **echoserver** que devolve información da petición. Facémolo con comandos *imperativos* para ver resultados rápidos.

### 1.1 Crear o Deployment
```bash
kubectl create deployment hello-world   --image=registry.k8s.io/echoserver:1.10   --port=8080
```

**Que fai?**  
Crea un Deployment cun contedor que devolve información HTTP (baseado internamente en Nginx).

> Se o Pod entra en CrashLoopBackOff, comproba os logs con `kubectl logs -l app=hello-world`.

### 1.2 Expor o Service tipo NodePort
```bash
kubectl expose deployment hello-world   --type=NodePort   --port=8080   --target-port=8080
```

### 1.3 Probar acceso
- Con GUI:  
  ```bash
  minikube service hello-world
  ```
- Sen GUI (VM NAT):  
  ```bash
  kubectl port-forward --address 0.0.0.0 service/hello-world 8080:8080
  # no host, abre http://localhost:8080
  ```

---

## 2) Despregue web declarativo (Nginx + Service ClusterIP)

Agora pasamos a YAML declarativos con Nginx. Usaremos port-forward para acceso.

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

**Acceso (VM NAT)**
```bash
kubectl port-forward --address 0.0.0.0 service/web 8080:80
# no host, abre http://localhost:8080
```

---

(O resto das etapas — ConfigMap, PVC, Probes, Ingress, Secrets, HPA — mantéñense igual, engadindo en cada unha un bloque final “Acceso dende VM sen GUI” co port-forward de exemplo.)

---

## 9) Limpieza final
```bash
kubectl delete ns lab-k8s --wait=false
kubectl config set-context --current --namespace=default
```

---

### 💡 Notas engadidas
- Engadidas explicacións de `TargetPort`, `NodePort` e `localhost` en contornos NAT.
- Corrixida a confusión entre contido visual (Nginx) e texto plano (echoserver).
- Engadido exemplo funcional de port-forward en `0.0.0.0` para exposición externa.
- Simplificados os YAMLs para evitar CrashLoopBackOff por argumentos incorrectos.
