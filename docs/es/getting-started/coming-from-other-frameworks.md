# Procedente de otro framework

Nexy es FastAPI más enrutamiento basado en archivos, páginas renderizadas por servidor y React, Vue, Svelte, opcionales.
Islas sólidas o Preact. Esta página mapea lo que ya sabes.

## De FastAPI

| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` en un módulo que importas | `GET` función en `src/routes/users.py` |
| `app.include_router(router)` | la ruta del archivo es la URL; nada que registrar |
| Parámetro de ruta `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | todavía `Depends(...)`: los controladores son controladores FastAPI |
| Jinja2 `TemplateResponse` | una página `.nexy` al lado del punto final |
| Ejecutar con `uvicorn main:app` | `nx dev`, luego `nx build && nx start` |

Todo lo que hay en `src/routes/*.py` es FastAPI normal: dependencias, modelos Pydantic, middleware
y `/docs` seguir trabajando.

## De Next.js

| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` o `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (posee `<html>`) | `src/routes/layout.tsx` con `useCSR = True` (React), o `src/routes/layout.nexy` en modo servidor |
| anidado `layout.tsx` | anidado `layout.tsx` / `layout.vue` / `layout.svelte` en modo cliente, anidado `layout.nexy` en modo servidor |
| `use client` componentes en una página de servidor | [islas](../rendering/islands.md) en modo servidor |
| Controladores de ruta `route.ts` | `src/routes/api/x.py`, escritos en Python |
| `(group)` carpetas | iguales: `(group)/` |
| Acciones del servidor | [`@Action`](../guides/actions.md) funciones llamadas desde un formulario o como funciones de cliente escritas |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

El backend es Python, por lo que su API comparte código con sus datos y su trabajo de ML. Componentes del cliente
hidratarse como islas en lugar de un árbol de React de página completa.

## Desde los backends Express o Node

| Expreso | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` con `async def GET(id)` |
| `app.use(middleware)` | Middleware FastAPI, registrado desde `nexyconfig.py` |
| `res.json(obj)` | devuelve un dict o un modelo Pydantic |
| Vistas de EJS / Pug | `.nexy` páginas (Jinja2) |
| `npm run dev` | `nx dev` |

## Elegir un enrutador

| Utilice | cuando |
|---|---|
| Enrutador basado en archivos | páginas y puntos finales mapeados a partir de archivos; el valor predeterminado |
| Enrutador modular | controladores, módulos e inyección de dependencia, estilo NestJS |

Ambos están respaldados por `nx new` y cubiertos por las mismas pruebas de un extremo a otro. Ver
[Enrutamiento](../routing/README.md) y [Enrutamiento modular](../routing/modular/README.md).

## ¿Dónde sigue?

- [Inicio rápido](quick-start.md): crea un proyecto y ejecútalo
- [Estructura del proyecto](project-structure.md): dónde pertenece cada archivo
- [Enrutamiento](../routing/README.md): elige el enrutador