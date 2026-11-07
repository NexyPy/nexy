# Enrutamiento

Nexy tiene dos enrutadores nativos. Puedes elegir uno por función; pueden coexistir en la misma aplicación.

**¿No estás seguro? Utilice enrutamiento basado en archivos.** Cubre páginas y puntos finales API sin configuración. Agregue el enrutador modular cuando un backend necesite controladores, servicios inyectados o guardias.

| tu estas construyendo | uso |
|---|---|
| Páginas, contenido, un sitio con algunos puntos finales. | Basado en archivos |
| Una gran API con servicios compartidos entre rutas | modulares |
| Ambos: páginas para personas, una API estructurada para máquinas | Basado en archivos y modular juntos |

<!-- router:fbr,custom -->
```diagram filename="El enrutador basado en archivos, de un vistazo"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```
<!-- /router -->

<!-- router:modular -->
```diagram filename="El enrutador modular, de un vistazo"
@Controller()             class AppController   →  /
@Controller("/about")     class AboutController →  /about/
@Controller("/api/users") class UserController  →  /api/users/  (get, post, …)
@Module()                 class AppModule       →  lists the controllers
useRouter = AppModule     nexyconfig.py         →  mounts the module
```
<!-- /router -->

| Enrutador | Fuente | Habilitado por |
|---|---|---|
| [Basado en archivos (FBR)](fbr/README.md) | cada archivo bajo `src/routes/` | el directorio existe |
| [Modulares](modular/README.md) | controladores y módulos | `useRouter = AppModule` en `nexyconfig.py` |

FBR se escanea siempre que existe `src/routes/`, incluso con un enrutador modular montado.

## Convivencia y prioridades

Puede combinar FBR, Modular e integración personalizada. Nexy registra estas rutas en el orden en que se descubren. Si dos enrutadores definen la misma ruta URL, gana el primero registrado. 

*Nota: Nexy actualmente no proporciona un diagnóstico de colisiones de URL; la primera ruta que reclama un camino simplemente sigue a las demás.*

<!-- router:fbr,custom -->
## Enrutamiento basado en archivos

Una ruta es un archivo. La URL es su ruta en `src/routes/`, menos la extensión. Al igual que Next.js, un proyecto está en uno de dos modos, elegidos con `useCSR`:

| | `useCSR = False` (predeterminado) | `useCSR = True` |
|---|---|---|
| paginas | `.nexy`, `.md`, `.mdx` | archivos de su marco de cliente |
| Diseño de raíz | `layout.nexy` | `layout.tsx` (React) |
| Componentes del cliente | permitido, como islas dentro de las páginas | las páginas mismas |
| Rutas API | `.py` | `.py` |

Consulte [Modo servidor y modo cliente](fbr/modes.md).

| Sección | lo que cubre |
|---|---|
| [fbr/páginas](fbr/pages/README.md) | páginas, [rutas dinámicas](fbr/pages/dynamic-routes.md) y grupos de rutas |
| [fbr/diseños](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/controladores](fbr/handlers/README.md) | `.py` manejadores de ruta, [validación y errores](fbr/handlers/validation-and-errors.md) |
| [fbr/dependencias](fbr/dependencies/README.md) | `dependencies.py` y guardias, heredados por directorio |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, heredado por directorio |
| [fbr/errores](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, errores JSON |
| [fbr/navegación](fbr/navigation/linking-and-navigating.md) | vinculación, navegación del cliente, [ganchos](fbr/navigation/hooks.md) |
| [fbr/tiempo real](fbr/realtime/websocket.md) | WebSocket manejadores |
| [fbr/herencia](fbr/inheritance.md) | cómo se heredan los diseños, las dependencias y las páginas de error |
<!-- /router -->

## Enrutamiento modular

Controladores, módulos e inyección de dependencias, al estilo de NestJS. Consulte [Enrutamiento modular](modular/README.md) y [Nexy y NestJS](modular/vs-nestjs.md).

<!-- router:modular -->
| Sección | lo que cubre |
|---|---|
| [modulares](modular/README.md) | `@Controller`, `@Module`, importaciones y exportaciones |
| [modular/inyección de dependencia](modular/dependency-injection.md) | `@Injectable`, alcances y el contenedor |
| [modular/protecciones-y-metadatos](modular/guards-and-metadata.md) | `@UseGuard`, `@UseResponse` y los metadatos OpenAPI |

Un controlador devuelve una vista `.nexy` con `useViews`, y la pasa a su diseño manualmente: no hay ningún `layout.nexy` aplicado por carpeta.
<!-- /router -->

## Integración personalizada

También puede integrar un enrutador FastAPI existente en su proyecto Nexy. Consulte [Integración de enrutamiento personalizado](custom/README.md).

## Próximos pasos

<!-- router:fbr,custom -->
- [Enrutamiento basado en archivos](fbr/README.md)
<!-- /router -->
<!-- router:modular -->
- [Enrutamiento modular](modular/README.md)
<!-- /router -->
- [Representación](../rendering/README.md)
- [Vistas](../views/README.md): qué va dentro de los archivos
