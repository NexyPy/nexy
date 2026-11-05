# ¿Qué es Nexi?

Nexy es un marco Python para aplicaciones web fullstack: sus páginas y su API viven en un proyecto y son atendidas por un servidor.

## lo que obtienes

- **Páginas en Python.** Un archivo `.nexy` es HTML con unas pocas líneas de Python en la parte superior; un archivo `.md` también es una página. No se necesita JavaScript para representar una página.
- **Una API en el mismo proyecto.** Un archivo `.py` bajo `src/routes/` responde solicitudes HTTP: una función llamada `GET` responde `GET`, una función llamada `POST` responde `POST`.
- **Documentación API gratuita.** Cada ruta API aparece en un esquema OpenAPI y Scalar la muestra como una referencia interactiva en `/docs`.
- **Formularios que llaman a Python.** Un formulario, o una llamada escrita desde el navegador, llega a la misma función Python.
- **Un framework frontend cuando lo desees.** React, Vue, Svelte, Solid o Preact, para un componente o para todo el sitio.
- **Un comando para trabajar, otro para enviar.** `nx dev` se recarga a medida que guardas; `nx build` prepara la producción.

## Sobre qué está construido

La versión actual, 2.2, incluye herramientas que quizás ya conozcas:

| parte | Construido sobre | Lo que significa para ti |
|---|---|---|
| Servidor y API | [FastAPI](https://fastapi.tiangolo.com/) | una ruta API es una ruta FastAPI: la validación Pydantic y las dependencias funcionan como de costumbre |
| Referencia API | OpenAPI y [Escalar](https://scalar.com/) | el esquema está en `/openapi.json`, la referencia en `/docs` |
| paginas | Jinja2 | una página `.nexy` utiliza etiquetas Jinja2 como `{{ title }}` |
| Interfaz (opcional) | [Vite](https://vite.dev/) | sólo con un marco de interfaz, que también necesita Node.js |

## Una primera página y un primer punto final

Una página, en `/hello`:

```nexy filename="src/rutas/hola.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Un punto final, en `GET /api/items`, listado en `/docs` sin ningún código adicional:

```python filename="src/rutas/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```

## Lo que te deja Nexy

La base de datos, el inicio de sesión y las reglas sobre quién puede hacer qué pertenecen a tu aplicación, para que tú elijas las bibliotecas. [Bases de datos](../guides/databases.md) y [Middleware y seguridad](../guides/middleware-and-security.md) muestran dónde se conecta cada uno.

## Próximos pasos

- [Instalación](installation.md): instala uv y crea un proyecto
- [Inicio rápido](quick-start.md): ejecútelo, cambie una página, constrúyala
- [Conceptos básicos](core-concepts.md): las pocas palabras que usa el resto de los documentos
