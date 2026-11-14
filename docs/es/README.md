# Documentación Nexy

**Un marco Python para aplicaciones web fullstack.**

Nexy coloca sus páginas y su API en un Python proyecto, atendido por un servidor. La versión 2.2 se basa en FastAPI: cada ruta API es una ruta FastAPI, enumerada en un esquema OpenAPI que Scalar muestra en `/docs`.

- **Python primero.** Las páginas, los puntos finales, los formularios y las acciones son Python, y una página no necesita JavaScript.
- **Un frontend cuando lo desees.** React, Vue, Svelte, Solid o Preact, para un componente o para todo el sitio.
- **Un archivo, una URL.** Un archivo en `src/routes/` es una ruta: `.nexy` es una página, `.py` es un punto final API.
- **Espacio para crecer.** Comience con un archivo; pasar a módulos o conectar un enrutador FastAPI existente, cuando el proyecto crezca.

¿Nuevo aquí? Lea [¿Qué es Nexy?](getting-started/what-is-nexy.md), luego el [Inicio rápido](getting-started/quick-start.md).

## Empezando

### Primeros pasos
| Página | que haras |
|---|---|
| [¿Qué es Nexy?](getting-started/what-is-nexy.md) | Sepa qué es Nexy, en qué se basa y qué obtiene |
| [Instalación](getting-started/installation.md) | Instale uv y Nexy CLI, luego cree su primer proyecto |
| [Inicio rápido](getting-started/quick-start.md) | Cree un proyecto, ejecútelo con recarga en vivo y constrúyalo para producción |
| [Tutorial](getting-started/tutorial.md) | Cree una aplicación de notas paso a paso, una parte ejecutable a la vez |

### entender el modelo
| Página | que haras |
|---|---|
| [Conceptos básicos](getting-started/core-concepts.md) | Obtenga el modelo mental: ruta, página, vista, componente, controlador, punto final |
| [Estructura del proyecto](getting-started/project-structure.md) | Sepa para qué sirve cada carpeta y archivo de un proyecto |
| [Elija un enrutador](routing/README.md) | Elija el enrutador basado en archivos, modular o personalizado |
| [Elija un formato de visualización](views/README.md) | Elija `.nexy`, Markdown o un marco de cliente para una página |

## Tutoría

### Unidad 1: lo básico
| Página | que construiras |
|---|---|
| [1. Crea el proyecto](tutorial/create-the-project.md) | Cree el proyecto de notas y ejecútelo en el navegador. |
| [2. Páginas y diseños](tutorial/pages-and-layouts.md) | Agregue la página de notas y cambie el diseño a su alrededor. |
| [3. Rutas dinámicas y una API](tutorial/dynamic-routes.md) | Asigne a cada nota una URL y entregue las notas como JSON |
| [4. Componentes](tutorial/components.md) | Convierta cada nota en un componente `.nexy` reutilizable |

### Unidad 2: datos
| Página | que construiras |
|---|---|
| [5. Guarde las notas en SQLite](tutorial/store-the-notes.md) | Agregue un modelo, una migración y una semilla, y lea las notas de la base de datos. |
| [6. Crea una nota a partir de un formulario](tutorial/create-a-note.md) | Publicar un formulario en una acción que guarda la nota |
| [7. Mostrar errores de validación](tutorial/validation-errors.md) | Rechace una nota en blanco y diga por qué encima del formulario. |
| [8. Editar y eliminar una nota](tutorial/edit-and-delete.md) | Añade los formularios que cambian y elimina una nota. |
| [9. Paginar las notas](tutorial/paginate-the-notes.md) | Mostrar cinco notas a la vez, con enlaces entre las páginas. |

### Unidad 3: usuarios
| Página | que construiras |
|---|---|
| [10. Crea una cuenta e inicia sesión](tutorial/accounts.md) | Regístrate, inicia y cierra sesión con una cookie de sesión |
| [11. Dale a cada usuario sus propias notas](tutorial/own-notes.md) | Ata cada nota a su usuario y protege las páginas, las Acciones y la API |
| [12. Restablecer una contraseña olvidada por correo electrónico](tutorial/password-reset.md) | Envíe un enlace firmado por correo electrónico que funcione una vez, durante una hora |

### Unidad 4: interactividad
| Página | que construiras |
|---|---|
| [13. Busca las notas mientras escribes](tutorial/search-the-notes.md) | Filtra cada nota en el navegador con una isla React |
| [14. Marca una nota sin recargar la página](tutorial/tick-a-note.md) | Marcar una nota hecha con un formulario que unas pocas líneas de JavaScript envían en su lugar |

## Enrutamiento

### Basado en archivos {fbr}
| Página | que haras |
|---|---|
| [Enrutamiento basado en archivos](routing/fbr/README.md) | Convertir la ruta de un archivo en una URL |
| [Páginas](routing/fbr/pages/README.md) | escribir una pagina |
| [Rutas dinámicas](routing/fbr/pages/dynamic-routes.md) | Utilice `[slug]`, `[...path]` y grupos de rutas |
| [Metadatos de la página](routing/fbr/pages/metadata.md) | Establecer el título, la descripción y compartir imagen de una página {new} |
| [Diseños](routing/fbr/layouts/README.md) | Compartir un marco entre páginas |
| [Herencia](routing/fbr/inheritance.md) | Leer el orden de resolución de diseños, dependencias y páginas de error. |
| [Modo servidor y modo cliente](routing/fbr/modes.md) | `useCSR`, y lo que permite cada modo |
| [Vincular y navegar](routing/fbr/navigation/linking-and-navigating.md) | Vincular páginas, navegar en el cliente, captar previamente |
| [Ganchos](routing/fbr/navigation/hooks.md) | Leer la ruta, consulta, cookies y sesión. |

### Controladores y errores {fbr}
| Página | que haras |
|---|---|
| [Controladores de ruta](routing/fbr/handlers/README.md) | Agregar un punto final Python |
| [Validación y errores](routing/fbr/handlers/validation-and-errors.md) | Responda `422` y `404`, y plantee un `HTTPException` |
| [WebSocket manejadores](routing/fbr/realtime/websocket.md) | Manejar una conexión `SOCKET` |
| [Dependencias y guardias](routing/fbr/dependencies/README.md) | Ejecute `dependencies.py` antes de un controlador y heredéelo |
| [Archivos de middleware](routing/fbr/middleware/README.md) | Envolver solicitudes con `middleware.py`, heredadas por directorio |
| [Páginas de error](routing/fbr/errors/README.md) | Responda con errores `notfound.nexy`, `errors.nexy` y JSON |
| [Páginas de error por carpeta](routing/fbr/errors/folder-pages.md) | Caso extremo: errores de subcarpetas |

### Enrutador modular {modular}
Controladores y módulos.
| Página | que haras |
|---|---|
| [Enrutamiento modular](routing/modular/README.md) | Montar controladores y módulos |
| [Inyección de dependencia](routing/modular/dependency-injection.md) | Definir servicios, sus alcances y el contenedor. |
| [Guardias y metadatos](routing/modular/guards-and-metadata.md) | Proteger y documentar rutas |
| [Enrutador modular frente a NestJS](routing/modular/vs-nestjs.md) | Comparación con NestJS |

### Integración de enrutador personalizado {custom}
| Página | que haras |
|---|---|
| [Enrutamiento personalizado](routing/custom/README.md) | Incluir una aplicación FastAPI existente |

## Interfaz

### Contratos compartidos
| Página | lo que define |
|---|---|
| [Acciones y navegación](views/frontend/actions-and-navigation.md) | Llame a una acción escrita, vincule páginas, lea la URL |
| [Obtener datos en un componente](views/frontend/fetch-data.md) | `useFetch`: lee JSON de una ruta, lo comparte, lo actualiza |

### Vistas nexy
| Página | que haras |
|---|---|
| [Archivos .nexy](views/nexy/README.md) | Escribe una página con Python, Jinja2 y accesorios. |
| [Componentes](views/nexy/components.md) | Utilice `Image`, `Link`, `Audio`, `Video` y `Import` |

### Páginas y diseños en archivos {fbr,custom}
| Página | lo que define |
|---|---|
| [Páginas frontales](views/frontend/pages.md) | Un archivo, una ruta: accesorios, renderizado, metadatos |
| [Diseños de interfaz](views/frontend/layouts.md) | La estructura del documento, el anidamiento y lo que un diseño no puede hacer |
| [diseño.nexy](views/nexy/layouts.md) | Escribir el diseño en modo servidor |
| [Markdown y MDX](views/nexy/markdown.md) | Escribir páginas de contenido |

### Diferencias marco
| Página | que cambia |
|---|---|
| [React diferencias](views/react/differences.md) | Componentes, ganchos y `layout.tsx` {new} |
| [Vue diferencias](views/vue/differences.md) | SFC, referencias y `layout.vue` {new} |
| [Svelte diferencias](views/svelte/differences.md) | Runas, tiendas y `layout.svelte` {new} |
| [Solid diferencias](views/solid/differences.md) | Señales, accesores y `layout.tsx` {new} |
| [Preact diferencias](views/preact/differences.md) | Ganchos, señales y `layout.tsx` {new} |

## Representación

### Modos
| Página | que decidiras |
|---|---|
| [Representación](rendering/README.md) | ¿Qué modo de renderizado se ajusta a una página? |
| [RSS](rendering/ssr.md) | Representación del servidor, la opción predeterminada |
| [Islas](rendering/islands.md) | Hidratar en inactividad, visible o consulta de medios |

### Modos de páginas de archivos {fbr,custom}
| Página | que decidiras |
|---|---|
| [ISR](rendering/isr.md) | Caché de páginas con estado obsoleto mientras se revalida |
| [RSE](rendering/csr.md) | Enrutamiento del lado del cliente |

## Guías

### Formularios y datos
| Página | que haras |
|---|---|
| [Acciones](guides/actions.md) | Llamar a una función Python desde un formulario o una función TypeScript escrita |
| [Bases de datos](guides/databases.md) | Elija un ORM y ejecute migraciones |

### Seguridad e implementación
| Página | que haras |
|---|---|
| [Middleware y seguridad](guides/middleware-and-security.md) | Configure CORS, GZip, hosts y sesiones confiables |
| [Implementar](deployment/README.md) | Construir, colocar en contenedores y servir |
| [Rendimiento](deployment/performance.md) | Mida y ajuste los valores predeterminados |

### Construir y probar
| Página | que haras |
|---|---|
| [Vite y estilo](guides/frontend.md) | Configurar Vite, diseñar y crear el cliente |
| [Pruebas](guides/testing.md) | Prueba con pytest, `TestClient` y vitest |

### Herramientas y ayuda
| Página | que haras |
|---|---|
| [Barra de herramientas de desarrollo](guides/devtools.md) | Utilice la barra de herramientas de `nexy dev` y apáguela. |
| [Agentes codificadores](guides/ai-agents.md) | Dale a Claude Code, Codex y OpenCode las reglas de tu proyecto |
| [Solución de problemas](guides/troubleshooting.md) | Solucionar los primeros problemas a los que se enfrenta la gente |

## Bases de datos

### bases de datos SQL
| Página | que haras |
|---|---|
| [SQLite](databases/sqlite.md) | Utilice un archivo, ningún servidor: motor, pragmas, migraciones y pruebas |
| [PostgreSQL](databases/postgresql.md) | Conéctese con psycopg, use JSONB, matrices, búsqueda y upserts |
| [Neón](databases/neon.md) | Utilice serverless PostgreSQL: host agrupado, suspensión automática y sucursales |
| [MySQL y MariaDB](databases/mysql-mariadb.md) | Conéctese con pymysql, use utf8mb4, upserts y búsqueda de texto completo |

## viniendo de

Las mismas tareas, escritas en el framework que conoces y luego en Nexy.

### Descripción general
| Página | que haras |
|---|---|
| [Procedente de otro marco](getting-started/coming-from-other-frameworks.md) | Traducir FastAPI, Next.js y expresar hábitos a Nexy |

### Python marcos {fbr}
| Página | que haras |
|---|---|
| [Desde FastAPI](coming-from/fastapi.md) | Conserva tu código FastAPI: solo `@app.get` se convierte en un archivo |
| [Desde Flask](coming-from/flask.md) | Convierta vistas, planos, plantillas y formularios en rutas Nexy |
| [Desde Django](coming-from/django.md) | Asigne vistas, plantillas, modelos, formularios y configuraciones a Nexy |

### JavaScript servidores {fbr}
| Página | que haras |
|---|---|
| [Desde expreso](coming-from/express.md) | Traducir rutas, middleware y `req`/`res` en Python controladores |
| [Desde Fastify](coming-from/fastify.md) | Convierta esquemas, complementos y enlaces en modelos, carpetas y archivos |
| [De Elysia](coming-from/elysia.md) | Asigne `t` esquemas, guardias y Edén a Pydantic y acciones escritas |
| [De Hono](coming-from/hono.md) | Mapear rutas, middleware y el cliente `hc` a Nexy |

### Marcos de trabajo completos {fbr}
| Página | que haras |
|---|---|
| [Desde Next.js](coming-from/nextjs.md) | Conserve sus páginas React y mueva el código del servidor a Python |
| [Desde Remix](coming-from/remix.md) | Convierta cargadores y acciones en Python controladores y acciones |
| [Desde Nuxt](coming-from/nuxt.md) | Conserve sus Vue páginas y mueva `server/` a Python |
| [De SvelteKit](coming-from/sveltekit.md) | Conserva tus Svelte páginas y mueve cargas, acciones y enlaces a Python |
| [Desde Astro](coming-from/astro.md) | Escribe Astro páginas como `.nexy` páginas, con las mismas islas |
| [De Laravel](coming-from/laravel.md) | Mapear rutas, controladores, Blade, Eloquent y colas a Nexy |
| [De Ruby on Rails](coming-from/rails.md) | Asigne rutas, controladores, ERB, Active Record y trabajos a Nexy |

### Marcos de controlador {modular}
| Página | que haras |
|---|---|
| [Desde NestJS](coming-from/nestjs.md) | Mueva controladores, módulos, proveedores y guardias al enrutador modular |
| [Desde arranque de primavera](coming-from/spring-boot.md) | Mueva controladores, servicios y filtros al enrutador modular |

## Referencia

### Comandos y configuración
| Página | lo que enumera |
|---|---|
| [CLI](reference/cli.md) | Comandos, indicadores, mensajes y códigos de salida |
| [Configuración](reference/config.md) | Cada campo `nexyconfig.py` y su valor predeterminado |

### Python API y errores
| Página | lo que enumera |
|---|---|
| [API de Python](reference/python-api.md) | Cada nombre que Nexy exporta, por módulo |
| [Excepciones y errores](reference/exceptions.md) | Cada falla, su estado y el archivo que la responde |

### Convenciones de archivos {fbr,custom}
| Página | que haras |
|---|---|
| [Convenciones de archivos](reference/file-conventions.md) | Archivos reservados y reglas de enrutamiento |

### Convenciones y conceptos
| Página | que haras |
|---|---|
| [Glosario](reference/glossary.md) | Las palabras que usan estos médicos |
| [Seguridad](reference/security.md) | Pisos de versiones, reglas que sigue Nexy, auditorías |

## Diseño
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
├─ coming-from/         one page per framework: FastAPI, Django, Express, Next.js...
├─ databases/           one page per database: SQLite, PostgreSQL, Neon, MySQL
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## Avanzado

### Avanzado {advanced}

| Página | que haras |
|---|---|
| [Cómo funciona Nexy](getting-started/how-nexy-works.md) | Mira qué sucede entre un archivo y una página, y qué te deja Nexy |
| [Actualizando a 2.2](getting-started/upgrading.md) | Migrar de 2.1 a 2.2 |
| [Internacionalización (i18n)](guides/i18n.md) | Agregue traducciones con la biblioteca que elija |
| [Recetas](guides/recipes.md) | Ejemplos y patrones, no un tutorial. |

*Estas páginas no forman parte de la ruta de lectura predeterminada. Un enlace "Toda la documentación" le permite verlo todo.*
