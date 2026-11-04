# Implementar

Dos comandos: `nx build` produce los artefactos, `nx start` los sirve.

**Antes de comenzar:** un proyecto que se construye localmente con `nx build` y, para páginas de clientes, el
cadena de herramientas frontend que `nx new` instaló.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

El tiempo de ejecución solo necesita Python. Uvicorn sirve la aplicación compilada y los activos estáticos; sin nodo
proceso y ningún proceso Vite están involucrados.

## Lo que produce la compilación

`__nexy__/` contiene los módulos de ruta compilados, el paquete de cliente en `__nexy__/client/` y el
HTML prerenderizado para rutas de marco. Copie el proyecto (fuente más `__nexy__/`) o compílelo dentro
la imagen.

## Acoplador

La etapa de compilación necesita Node (para Vite) y Python (para el compilador). La etapa de ejecución necesita Python
solamente.

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

`uv` recupera un Python administrado cuando la imagen base no tiene ninguno, razón por la cual la etapa de compilación puede comenzar
desde una imagen de nodo.

## Detrás de un proxy inverso

Ejecute `nx start` en localhost y permita que Nginx, Caddy o el proxy de la plataforma finalicen TLS:

```bash
nx start --host 127.0.0.1 --port 8000
```

Asegúrese de que el proxy reenvíe las actualizaciones de WebSocket si utiliza controladores `SOCKET` y que reenvíe
el host original: FastAPI crea URL absolutas a partir de él.

## Control de salud

Agregue un archivo de controlador, `src/routes/api/health.py` y sondee `/api/health`, en lugar de una página que pueda
renderizar lentamente:

```python filename="src/rutas/api/health.py"
async def GET():
    return {"status": "ok"}
```

## Hospedaje estático

Cada página es HTML, pero Nexy asume un servidor para el enrutamiento y para los controladores API.

> [!NOTA]
> no hay `--static` modo de construcción. Se debe generar una exportación puramente estática en
> tu canalización desde la salida `nx build`.

## Lista de verificación

- [ ] `nx build` en CI, no hay advertencias para las rutas que espera representar en el servidor
- [ ] `nx start` sale con el código 1 y no inicia nada cuando un archivo de ruta no se puede cargar
- [ ] `NEXY_ACTION_SECRET` establecido, o `__nexy__/action.key` mantenido con la compilación
- [ ] `useDocs = False` en producción si el esquema de API no debe ser público
- [ ] `useTrustedHost` y `useHTTPSRedirect` configurados para implementaciones públicas
- [ ] `__nexy__/` no comprometido

## Próximos pasos

- [Config](../reference/config.md): HTTPS, hosts confiables, sesiones
- [Frontend](../guides/frontend.md): qué construye Vite
- [Testing](../guides/testing.md): los comandos a ejecutar en CI