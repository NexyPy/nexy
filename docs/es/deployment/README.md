# Implementar

Dos comandos: `nx build` produce los artefactos, `nx start` los sirve.

**Antes de comenzar:** un proyecto que se construye localmente con `nx build` y, para las páginas del cliente, la cadena de herramientas frontend que `nx new` instaló.

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
- [ ] `__nexy__/` not committed

## Próximos pasos

- [Configuración](../reference/config.md): HTTPS, hosts confiables, sesiones
- [Frontend](../guides/frontend.md): qué construye Vite
- [Probando](../guides/testing.md): los comandos a ejecutar en CI
