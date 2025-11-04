# Introdución a Kubernetes

## Que é a orquestración de contedores?

No desenvolvemento moderno, os **contedores** permiten empaquetar unha aplicación xunto co seu sistema operativo base, dependencias e configuración. Isto garante que se execute igual en calquera contorno, sexa un portátil, un servidor físico ou unha nube.

Porén, cando se traballa con **decenas ou centos de contedores** (como ocorre nas arquitecturas de microservizos), precisase unha ferramenta que os **xestione automaticamente**: cree, escale, reinicie, actualice ou elimine contedores segundo as necesidades do sistema. A isto chámaselle **orquestración de contedores**.

### Funcionalidades principais

- Despregue automático de contedores.
- Escalado horizontal (engadir ou quitar réplicas).
- Supervisión do estado dos servizos.
- Reinicio automático ante fallos.
- Balanceo de carga interno.
- Actualizacións sen interrupción (*rolling updates*).
- Xestión de configuracións e segredos.
- Almacenamento persistente para datos.

---

## Que é Kubernetes?

**Kubernetes** (tamén coñecido como **K8s**, polas 8 letras entre o "K" e o "s") é unha plataforma **de código aberto** deseñada para automatizar o despregue, escalado e operación de contedores.

Foi creada por **Google**, baseada na súa experiencia interna con Borg, e actualmente é mantida pola **Cloud Native Computing Foundation (CNCF)**. É o estándar de facto na industria para orquestrar contedores en contornos tanto locais como en nube.

### Obxectivos principais

- Automatizar o despregue e a xestión de contedores.
- Asegurar alta dispoñibilidade e tolerancia a fallos.
- Facilitar o despregue continuo (*CI/CD*).
- Simplificar o escalado horizontal e vertical.
- Garantir portabilidade entre diferentes provedores cloud.

---

## Características principais de Kubernetes

- **Despregue automatizado** de aplicacións en contedores.
- **Auto-reparación**: reinicia contedores que fallan ou se perden.
- **Actualizacións sen interrupcións** e posibilidade de *rollback*.
- **Balanceo de carga** e resolución DNS interna.
- **Xestión de almacenamento persistente** (PVs e PVCs).
- **Configuración e segredos** centralizados (ConfigMaps e Secrets).
- **Infraestrutura declarativa** mediante ficheiros YAML.
- **Extensibilidade**: admite controladores e operadores personalizados.
- **Portabilidade**: pode executarse en local (Minikube, Kind) ou na nube (GKE, EKS, AKS).

---

# Arquitectura de Kubernetes

Kubernetes ten unha arquitectura **cliente-servidor** dividida en dous compoñentes principais: o **Control Plane** (ou plano de control) e os **nós de traballo** (*worker nodes*).

## Control Plane (nó mestre)

É o cerebro de Kubernetes: xestiona o estado desexado do clúster e toma decisións sobre onde e como se executan os contedores.

- **`kube-apiserver`** → expón a API REST de Kubernetes; é o punto central de comunicación.
- **`etcd`** → almacén chave-valor que garda todo o estado do clúster.
- **`kube-scheduler`** → decide en que nodo executar cada Pod.
- **`controller-manager`** → supervisa os recursos e aplica accións automáticas (crear, eliminar, reiniciar).
- **`cloud-controller-manager`** → integra o clúster co provedor cloud (opcional).

## Worker Nodes (nós de traballo)

Son as máquinas (físicas ou virtuais) onde realmente se executan os contedores.

- **`kubelet`** → axente que comunica co Control Plane e garante que os contedores funcionen segundo o plan.
- **`kube-proxy`** → xestiona o tráfico de rede cara aos Pods e o balanceo.
- **Container Runtime** → software que executa os contedores (ex: containerd, CRI-O, Docker).

---

# Recursos fundamentais de Kubernetes

| Elemento | Descrición | Exemplo de uso |
|-----------|-------------|----------------|
| **Pod** | Unidade mínima de execución. Pode conter un ou varios contedores. | Un microservizo web con Nginx. |
| **Deployment** | Xestiona réplicas de Pods, actualizacións e *rollbacks*. | Escalar un servizo de API REST. |
| **Service** | Expón un conxunto de Pods cunha IP estable. | Balancear tráfico entre réplicas. |
| **Namespace** | Aíllamento lóxico de recursos. | Separar dev/test/prod. |
| **ConfigMap** | Gardar configuracións non sensibles. | Variables de contorno dunha app. |
| **Secret** | Gardar datos sensibles (tokens, contrasinais). | Conexións a bases de datos. |
| **Volume / PVC** | Almacenamento persistente para datos. | Gardar logs, ficheiros ou BBDD. |
| **Ingress** | Regras HTTP externas para acceder a servizos. | Expor unha aplicación web pública. |

---

# Tipos de Services en Kubernetes

Os **Services** proporcionan un punto de acceso estable aos Pods, xa que as IP dos Pods poden cambiar cando se recrean. Hai varios tipos segundo o nivel de accesibilidade:

| Tipo | Descrición | Uso típico |
|------|-------------|------------|
| **ClusterIP** | IP interna accesible só dentro do clúster. É o valor por defecto. | Comunicación entre microservizos. |
| **NodePort** | Abre un porto no nodo (entre 30000-32767) accesible dende fóra. | Probas locais con Minikube. |
| **LoadBalancer** | Crea un balanceador externo (en cloud). | Aplicacións en produción en GKE, EKS, etc. |
| **ExternalName** | Asocia un nome DNS interno cun externo. | Redirixir servizos a outro dominio. |

### Diagrama conceptual

```
[Cliente]
   |
[Service: NodePort / LoadBalancer]
   |
[ClusterIP interno]
   |
[Pods do Deployment]
```

Exemplo de Service con NodePort:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 31000
  type: NodePort
```

---

# Tipos de Deployment e estratexias de actualización

O **Deployment** define como se crean, actualizan e manteñen os Pods dunha aplicación.

| Estratexia | Descrición | Uso recomendado |
|-------------|-------------|----------------|
| **Recreate** | Elimina todos os Pods antigos antes de crear os novos. | Cando non se poden ter dúas versións á vez (ex: BBDD). |
| **RollingUpdate** | Substitúe gradualmente os Pods antigos por novos (por defecto). | Despregue continuo sen interrupción. |
| **Blue/Green** | Dúas versións simultáneas: “blue” (actual) e “green” (nova). | Entornos con probas de integración. |
| **Canary** | Libera a nova versión só a unha parte dos usuarios. | Testeo gradual en produción. |

Exemplo básico de Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          ports:
            - containerPort: 80
```

---

# Volumes e almacenamento

Os contedores son efémeros, polo que Kubernetes emprega **Volumes** para manter datos persistentes.

## Tipos comúns

| Tipo | Descrición | Persistencia |
|------|-------------|--------------|
| **emptyDir** | Directorio temporal creado co Pod e eliminado ao borralo. | ❌ |
| **hostPath** | Usa un directorio do nodo anfitrión. | ⚠️ (dependente do nodo) |
| **configMap / secret** | Volume xerado a partir destes recursos. | ⚠️ (segundo o recurso) |
| **persistentVolumeClaim (PVC)** | Volume provisionado dinámicamente ou ligado a un PV. | ✅ |

Exemplo de PVC:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: datos-app
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Exemplo de uso no Deployment:

```yaml
volumeMounts:
  - name: datos
    mountPath: /usr/share/nginx/html
volumes:
  - name: datos
    persistentVolumeClaim:
      claimName: datos-app
```

---

# Networking e Ingress

Cada Pod ten a súa propia IP e comunícase libremente cos demais.  
Os **Servizos** proporcionan IPs estables e balanceo de carga.

### Tipos de acceso

| Tipo | Alcance | Exemplo |
|------|----------|---------|
| **ClusterIP** | Interno ao clúster | `curl http://web-service` dende outro Pod |
| **NodePort** | Porto accesible dende o exterior | `minikube service web-service` |
| **Ingress** | Regras HTTP externas | `http://app.local` |

### Exemplo de Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-service
                port:
                  number: 80
```

---

# Configuración con YAML

Kubernetes funciona de forma **declarativa**: describimos o estado desexado do sistema, e o clúster encárgase de levalo a cabo.

Exemplo completo de Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
        - name: web
          image: nginx:latest
          ports:
            - containerPort: 80
```

---

# ConfigMaps e Secrets

## ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_MODE: "production"
  TIMEOUT: "30"
```

## Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=   # admin
  password: c2VjcmV0   # secret
```

---

# Escalado e actualizacións

## Escalado manual

```bash
kubectl scale deployment webapp --replicas=5
```

## Escalado automático

```bash
kubectl autoscale deployment webapp --min=2 --max=10 --cpu-percent=70
```

## Actualizacións

```bash
kubectl set image deployment/webapp web=nginx:1.25
kubectl rollout status deployment/webapp
kubectl rollout undo deployment/webapp
```

---

# Monitorización e depuración

Comandos útiles:

```bash
kubectl get pods -o wide
kubectl logs <pod>
kubectl exec -it <pod> -- sh
kubectl top pods
kubectl describe pod <pod>
```

En Minikube:
```bash
minikube addons enable metrics-server
```

Ferramentas externas: **Prometheus**, **Grafana**, **Lens**, **K9s**.

---

# Resumo final

| Elemento | Función principal |
|-----------|-------------------|
| **Pod** | Unidade mínima de execución |
| **Deployment** | Control de réplicas e versións |
| **Service** | Comunicación estable entre Pods |
| **Ingress** | Acceso HTTP/HTTPS externo |
| **ConfigMap / Secret** | Configuración e segredos |
| **Volume / PVC** | Almacenamento persistente |
| **HPA** | Escalado automático |
| **Probe** | Control de saúde e dispoñibilidade |

---

**Autor:** Adrián Blanco  
**Centro:** CE CIFP A Carballeira  
**Data:** Novembro 2025
