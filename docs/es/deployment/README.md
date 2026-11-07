# Implementar

Dos comandos: `nx build` produce los artefactos, `nx start` los sirve.

**Antes de comenzar:** un proyecto que se compila localmente con `nx build` y, para las páginas del cliente, la cadena de herramientas frontend que `nx new` instaló.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

El tiempo de ejecución solo necesita Python. Uvicorn sirve la aplicación compilada y los activos estáticos; no hay ningún proceso de Nodo ni ningún proceso Vite involucrado.

## Lo que produce la construcción

`__nexy__/` contiene los módulos de ruta compilados, el paquete de cliente en `__nexy__/client/` y el HTML pre-renderizado para las rutas del marco. Copie el proyecto (fuente más `__nexy__/`) o constrúyalo dentro de la imagen.

## Docker

La etapa de compilación necesita Node (para Vite) y Python (para el compilador). La etapa de tiempo de ejecución solo necesita Python.

```dockerfile filename="archivo acoplable"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

`uv` recupera un Python administrado cuando la imagen base no tiene ninguno, razón por la cual la etapa de construcción puede comenzar desde una imagen de Nodo.

## Detrás de un proxy inverso

Ejecute `nx start` en localhost y deje que Nginx, Caddy o el proxy de la plataforma finalicen TLS:

```bash
nx start --host 127.0.0.1 --port 8000
```

Asegúrese de que el proxy reenvíe WebSocket actualizaciones si utiliza `SOCKET` controladores, y que reenvíe el host original; FastAPI genera URL absolutas a partir de él.

## control de salud

<!-- router:fbr,custom -->
Agregue un archivo de controlador, `src/routes/api/health.py` y pruebe `/api/health`, en lugar de una página que puede procesarse lentamente:

```python filename="src/rutas/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
Agregue un controlador y pruebe `/health/`, en lugar de una vista que pueda renderizarse lentamente:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

Indíquelo en el `controllers` del módulo raíz.
<!-- /router -->

### Puntos finales integrados

Un equilibrador de carga o Kubernetes plantea dos preguntas: ¿está activo el proceso y puede recibir tráfico? Configure `useHealth` y Nexy responde a ambos, sin archivo de controlador ni controlador:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useHealth = True
```

| Punto final | Respuestas 200 | Respuestas 503 |
|---|---|---|
| `GET /health/live` | mientras el proceso responde | nunca |
| `GET /health/ready` | una vez iniciada la aplicación | mientras se inicia, y una vez que el servidor le pide que se detenga |

Nexy garantiza que `/health/ready` sigue el inicio y el apagado del servidor.

Nexy garantiza que ambos puntos finales permanezcan fuera del registro de acceso y fuera del esquema OpenAPI.

Nexy garantiza que ambos puntos finales respondan antes de `useTrustedHost` y `useHTTPSRedirect`, por lo que no se rechaza una sonda enviada a través de HTTP a la dirección de un pod.

Por convención, mantienes tus propias rutas fuera de `/health/live` y `/health/ready` mientras `useHealth` está activada: los puntos finales de Nexy responden primero. `useHealth` es `False` de forma predeterminada, por lo que un proyecto que no lo establece mantiene ambas rutas.

Tu aplicación es responsable de comprobar de qué depende: `/health/ready` informa el ciclo de vida del servidor, no el estado de una base de datos.

Apunte las sondas de un Kubernetes `Deployment` hacia ellos:

```yaml filename="k8s/despliegue.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: registry.example.com/app:1.0
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            periodSeconds: 5
```

## Alojamiento estático

Cada página es HTML, pero Nexy asume un servidor para el enrutamiento y para los controladores API.

> [!NOTE]
> no hay modo de compilación `--static`. Se debe generar una exportación puramente estática en su canalización a partir de la salida `nx build`.

## Lista de verificación

- [ ] `nx build` en CI, no hay advertencias para las rutas que espera representar en el servidor
- [ ] `nx start` sale con el código 1 y no inicia nada cuando un archivo de ruta no se puede cargar
- [ ] `NEXY_ACTION_SECRET` establecido, o `__nexy__/action.key` mantenido con la compilación
- [ ] `useDocs = False` en producción si el esquema de API no debe ser público
- [ ] `useTrustedHost` y `useHTTPSRedirect` configurados para implementaciones públicas
- [ ] `useHealth = True` cuando un balanceador de carga o Kubernetes prueba la aplicación
- [ ] `__nexy__/` no comprometido

## Próximos pasos

- [Configuración](../reference/config.md): HTTPS, hosts confiables, sesiones
- [Frontend](../guides/frontend.md): qué construye Vite
- [Probando](../guides/testing.md): los comandos a ejecutar en CI
