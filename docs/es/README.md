# Documentación Nexy

**Un marco Python para aplicaciones web fullstack.**

Nexy trata sobre la unión entre un backend Python y una interfaz de navegador. En lugar de dos servidores, dos sistemas de compilación y dos tablas de rutas, obtienes un origen: FastAPI y Starlette sirven la aplicación, Vite construye el cliente y un archivo en `src/routes/` es una ruta; `.nexy` es una página, `.py` es un controlador de API.

- **Python primero.** Las páginas, los puntos finales, los formularios y las acciones son Python, y una página renderizada por el servidor no necesita un marco de interfaz.
- **Tres enrutadores, una integración.** Basado en archivos, modular o existente FastAPI `APIRouter`.
- **Un frontend cuando lo desees.** React, Vue, Svelte, Solid o Preact, por página como islas, o para todo el proyecto en modo cliente.
- **Representación, un modelo.** La representación del servidor, las páginas en caché y las islas se deciden por página; el enrutamiento del cliente es un cambio de proyecto.
- **Acciones escritas.** Una publicación de formulario y una llamada de cliente escrita llegan a la misma Python función.

Comience con un archivo en `src/routes/` y agregue estructura cuando el proyecto crezca.

## Empezando

### Primeros pasos
| Página | Qué harás |
|---|---|
| [Instalación](getting-started/installation.md) | Instale uv y Nexy CLI, luego cree su primer proyecto |
| [Inicio rápido](getting-started/quick-start.md) | Cree un proyecto, ejecútelo con recarga en vivo y constrúyalo para producción |
| [Tutorial](getting-started/tutorial.md) | Cree una página de notas con un punto final, datos compartidos y una compilación de producción en 10 minutos |

### entender el modelo
| Página | Qué harás |
|---|---|
| [Conceptos básicos](getting-started/core-concepts.md) | Obtenga el modelo mental: ruta, página, vista, componente, controlador, punto final |
| [Cómo funciona Nexy](getting-started/how-nexy-works.md) | Siga una solicitud desde la URL hasta el archivo que la responde |
| [Arquitectura](architecture.md) | Sepa qué capa hace qué y qué deja Nexy a su aplicación |
| [Estructura del proyecto](getting-started/project-structure.md) | Sepa para qué sirve cada carpeta y archivo de un proyecto |
| [Elija un enrutador](routing/README.md) | Elija el enrutador basado en archivos, modular o personalizado |
| [Elija un formato de vista](views/README.md) | Elija `.nexy`, Markdown o un marco de cliente para una página |

### Viniendo de otro lugar
| Página | Qué harás |
|---|---|
| [Procedente de otro marco](getting-started/coming-from-other-frameworks.md) | Traducir FastAPI, Next.js y expresar hábitos en Nexy |

## Enrutamiento

### Basado en archivos {fbr}
| Página | Qué harás |
|---|---|
| [Enrutamiento basado en archivos](routing/fbr/README.md) | Convertir una ruta de archivo en una URL |
| [Páginas](routing/fbr/pages/README.md) | Escribe una página |
| [Rutas dinámicas](routing/fbr/pages/dynamic-routes.md) | Utilice `[slug]`, `[...path]` y grupos de rutas |
| [Metadatos de página](routing/fbr/pages/metadata.md) | Establecer el título, la descripción y compartir imagen de una página {new} |
| [Diseños](routing/fbr/layouts/README.md) | Compartir un marco entre páginas |
| [Herencia](routing/fbr/inheritance.md) | Leer el orden de resolución de diseños, dependencias y páginas de error |
| [Modo servidor y modo cliente](routing/fbr/modes.md) | `useCSR`, y lo que permite cada modo |
| [Vincular y navegar](routing/fbr/navigation/linking-and-navigating.md) | Vincular páginas, navegar en el cliente, captar previamente |
| [Hooks](routing/fbr/navigation/hooks.md) | Leer la ruta, consulta, cookies y sesión |

### Controladores y errores {fbr}
| Página | Qué harás |
|---|---|
| [Manejadores de ruta](routing/fbr/handlers/README.md) | Agregar un Python punto final |
| [Validación y errores](routing/fbr/handlers/validation-and-errors.md) | Responda `422` y `404`, y plantee un `HTTPException` |
| [WebSocket manejadores](routing/fbr/realtime/websocket.md) | Maneja una conexión `SOCKET` |
| [Dependencias y guardias](routing/fbr/dependencies/README.md) | Ejecutar `dependencies.py` antes de un controlador y heredarlo |
| [Archivos middleware](routing/fbr/middleware/README.md) | Solicitudes empaquetadas con `middleware.py`, heredadas por el directorio |
| [Páginas de error](routing/fbr/errors/README.md) | Responder con `notfound.nexy`, `errors.nexy` y errores JSON |
| [Páginas de error por carpeta](routing/fbr/errors/folder-pages.md) | Caso extremo: errores de subcarpetas |

### Enrutador modular {modular}
Controladores y módulos.
| Página | Qué harás |
|---|---|
| [Enrutamiento modular](routing/modular/README.md) | Montaje de controladores y módulos |
| [Inyección de dependencia](routing/modular/dependency-injection.md) | Definir servicios, sus alcances y el contenedor |
| [Guardias y metadatos](routing/modular/guards-and-metadata.md) | Proteger y documentar rutas |
| [Router modular vs NestJS](routing/modular/vs-nestjs.md) | Comparación con NestJS |

### Integración de enrutador personalizado {custom}
| Página | Qué harás |
|---|---|
| [Ruta personalizada](routing/custom/README.md) | Incluir una aplicación FastAPI existente |

## Interfaz

### Contratos compartidos
| Página | Qué define |
|---|---|
| [Páginas de inicio](views/frontend/pages.md) | Un archivo, una ruta: accesorios, renderizado, metadatos |
| [Diseños de interfaz](views/frontend/layouts.md) | La estructura del documento, el anidamiento y lo que un diseño no puede hacer |
| [Acciones y navegación](views/frontend/actions-and-navigation.md) | Llamar una acción escrita, vincular páginas, leer la URL |

### Vistas nexy
| Página | Qué harás |
|---|---|
| [archivos .nexy](views/nexy/README.md) | Escribe una página con Python, Jinja2 y accesorios |
| [Componentes](views/nexy/components.md) | Utilice `Image`, `Link`, `Audio`, `Video` y `Import` |
| [layout.nexy](views/nexy/layouts.md) | Escribe el diseño en modo servidor |
| [Markdown y MDX](views/nexy/markdown.md) | Escribir páginas de contenido |

### Diferencias marco
| Página | Qué cambia |
|---|---|
| [React diferencias](views/react/differences.md) | Componentes, ganchos y `layout.tsx` {new} |
| [Vue diferencias](views/vue/differences.md) | SFC, referencias y `layout.vue` {new} |
| [Svelte diferencias](views/svelte/differences.md) | Runas, tiendas y `layout.svelte` {new} |
| [Solid diferencias](views/solid/differences.md) | Señales, accesores y `layout.tsx` {new} |
| [Preact diferencias](views/preact/differences.md) | Ganchos, señales y `layout.tsx` {new} |

## Representación

### Modos
| Página | Lo que decidirás |
|---|---|
| [Renderizado](rendering/README.md) | Qué modo de renderizado se ajusta a una página |
| [SSR](rendering/ssr.md) | Representación del servidor, el valor predeterminado |
| [ISR](rendering/isr.md) | Caché de páginas con estado obsoleto mientras se revalida |
| [CSR](rendering/csr.md) | Enrutamiento del lado del cliente |
| [Islas](rendering/islands.md) | Hidratar en inactividad, visible o consulta de medios |

## Guías

### Formularios y datos
| Página | Qué harás |
|---|---|
| [Acciones](guides/actions.md) | Llamar a una función Python desde un formulario o una función TypeScript escrita |
| [Bases de datos](guides/databases.md) | Elija un ORM y ejecute migraciones |

### Seguridad e implementación
| Página | Qué harás |
|---|---|
| [Middleware y seguridad](guides/middleware-and-security.md) | Configurar CORS, GZip, hosts y sesiones confiables |
| [Implementar](deployment/README.md) | Construir, crear contenedores y servir |
| [Rendimiento](deployment/performance.md) | Medir y ajustar los valores predeterminados |

### Construir y probar
| Página | Qué harás |
|---|---|
| [Vite y estilo](guides/frontend.md) | Configuración Vite, estilo y compilación del cliente |
| [Probando](guides/testing.md) | Prueba con pytest, `TestClient` y vitest |

### Herramientas y ayuda
| Página | Qué harás |
|---|---|
| [Barra de herramientas de desarrollo](guides/devtools.md) | Utilice la barra de herramientas de `nexy dev` y apáguela |
| [Agentes codificadores](guides/ai-agents.md) | Entrega a Claude Code, Codex y OpenCode las reglas de tu proyecto |
| [Solución de problemas](guides/troubleshooting.md) | Solucionar los primeros problemas que encuentran las personas |

## Referencia

### Comandos y configuración
| Página | Qué enumera |
|---|---|
| [CLI](reference/cli.md) | Comandos, indicadores, mensajes y códigos de salida |
| [Config](reference/config.md) | Cada campo `nexyconfig.py` y su | predeterminado

### Python API y errores
| Página | Qué enumera |
|---|---|
| [Python API](reference/python-api.md) | Cada nombre que Nexy exporta, por módulo |
| [Excepciones y errores](reference/exceptions.md) | Cada falla, su estado y el archivo que la responde |

### Convenciones y conceptos
| Página | Qué harás |
|---|---|
| [Convenciones de archivos](reference/file-conventions.md) | Archivos reservados y reglas de enrutamiento |
| [Glosario](reference/glossary.md) | Las palabras que utilizan estos documentos |
| [Seguridad](reference/security.md) | Pisos de versiones, reglas que sigue Nexy, auditorías |

## Diseño
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
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

| Página | Qué harás |
|---|---|
| [Actualizar a 2.2](getting-started/upgrading.md) | Migrar de 2.1 a 2.2 |
| [Internacionalización (i18n)](guides/i18n.md) | Agregue traducciones con la biblioteca que elija |
| [Recetas](guides/recipes.md) | Ejemplos y patrones, no un tutorial |

*Estas páginas no forman parte de la ruta de lectura predeterminada. Un enlace "Toda la documentación" le permite verlo todo.*
