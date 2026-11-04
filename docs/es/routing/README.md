# Enrutamiento

Nexy tiene dos enrutadores nativos. Puedes elegir uno por función; pueden coexistir en la misma aplicación.

**¿No estás seguro? Utilice enrutamiento basado en archivos.** Cubre páginas y puntos finales API sin configuración. Agregue el enrutador modular cuando un backend necesite controladores, servicios inyectados o guardias.

| Estás construyendo | Usa |
|---|---|
| Páginas, contenido, un sitio con algunos puntos finales | Basado en archivos |
| Una gran API con servicios compartidos entre rutas | Modular |
| Ambos: páginas para personas, una API estructurada para máquinas | Basados en archivos y modulares juntos |

```diagram filename="El enrutador basado en archivos, de un vistazo"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```

| Enrutador | Fuente | Habilitado por |
|---|---|---|
| [Basado en archivos (FBR)](fbr/README.md) | cada archivo en `src/routes/` | el directorio existe |
| [Modular](modular/README.md) | controladores y módulos | `useRouter = AppModule` en `nexyconfig.py` |

FBR se escanea siempre que existe `src/routes/`, incluso con un enrutador modular montado.

## Convivencia y prioridades

Puede combinar FBR, Modular e integración personalizada. Nexy registra estas rutas en el orden en que se descubren. Si dos enrutadores definen la misma ruta URL, gana el primero registrado. 

*Nota: Nexy actualmente no proporciona un diagnóstico de colisiones de URL; la primera ruta que reclama un camino simplemente sigue a las demás.*

## Enrutamiento basado en archivos

Una ruta es un archivo. La URL es su ruta en `src/routes/`, menos la extensión. Como Next.js, un
El proyecto está en uno de dos modos, elegido con `useCSR`:

| | `useCSR = False` (predeterminado) | `useCSR = True` |
|---|---|---|
| Páginas | `.nexy`, `.md`, `.mdx` | archivos de su framework cliente |
| Diseño de raíz | `layout.nexy` | `layout.tsx` (React) |
| Componentes del cliente | permitidos, como islas dentro de las páginas | las páginas mismas |
| Rutas API | `.py` | `.py` |

Consulte [Modo servidor y modo cliente](fbr/modes.md).

| Sección | Qué cubre |
|---|---|
| [fbr/pages](fbr/pages/README.md) | páginas, [rutas dinámicas](fbr/pages/dynamic-routes.md) y grupos de rutas |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` manejadores de ruta, [validación y errores](fbr/handlers/validation-and-errors.md) |
| [fbr/dependencies](fbr/dependencies/README.md) | `dependencies.py` y guardias, heredados por directorio |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, heredado por directorio |
| [fbr/errors](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, errores JSON |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | vinculación, navegación del cliente, [hooks](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | Controladores WebSocket |
| [fbr/inheritance](fbr/inheritance.md) | cómo se heredan los diseños, las dependencias y las páginas de error |

## Enrutamiento modular

Controladores, módulos e inyección de dependencias, al estilo NestJS. Ver
[Enrutamiento modular](modular/README.md) y [Nexy y NestJS](modular/vs-nestjs.md).

## Integración personalizada

También puede integrar un enrutador FastAPI existente en su proyecto Nexy. Consulte [Integración de enrutamiento personalizado](custom/README.md).

## Próximos pasos

- [Enrutamiento basado en archivos](fbr/README.md)
- [Renderizado](../rendering/README.md)
- [Vistas](../views/README.md): qué va dentro de los archivos