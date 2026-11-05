# Cómo funciona Nexy

Qué sucede entre un archivo que escribes y la página en el navegador: las capas que cruza una solicitud, quién construye qué y qué deja Nexy a tu aplicación. No necesita esta página para comenzar; Responde a las preguntas de "¿por qué funciona así?" más adelante.

## las capas

```diagram filename="Una petición, cinco capas"
Browser
   │
   ▼
Uvicorn ───── ASGI transport
   │
   ▼
Middleware ── sessions, CORS, gzip, trusted hosts, your own
   │
   ▼
Router ────── FBR | Modular | Custom ── picks the file that answers
   │
   ▼
Renderer ──── HTML (Jinja2, Markdown, Node) or JSON
   │
   ▼
Response
```

| capa | Responsabilidad | no |
|---|---|---|
| Uvicorn | aceptar la conexión, hablar ASGI | saber que es una pagina |
| software intermedio | decorar la solicitud: sesión, CORS, gzip, hosts confiables, redireccionamiento HTTPS, tuyo | elige una ruta |
| Enrutador | unir la URL a un archivo, con sus diseños, dependencias y páginas de error | producir contenido |
| renderizador | ejecute la página y convierta su resultado en HTML o JSON | recuperar tus datos |
| Cliente | Vite y su marco: paquetes, hidratación, navegación del cliente | responder una solicitud del servidor |

## ¿Quién construye qué?

| Actor | posee | no posee |
|---|---|---|
| nexy | enrutamiento, renderizado del servidor, acciones, `.nexy` compilación, un origen | componentes, reactividad, datos |
| Vite | paquetes de clientes, el servidor de desarrollo, recarga en caliente | enrutamiento, renderizado del servidor, acciones |
| Tu marco | componentes, reactividad, el ecosistema | enrutamiento, el documento (Nexy solicita su diseño) |
| Tu solicitud | datos, autenticación, autorización, reglas de negocio | transporte, renderizado |

La regla detrás de la tabla: **Nexy construye lo que posee y nunca compila lo que Vite compila.**

## El sistema de enrutamiento

Una ruta bajo `src/routes/` se convierte en una URL según cuatro reglas:

| Archivo | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

La extensión nunca aparece; `index` es la ruta de su carpeta; una carpeta entre paréntesis agrupa archivos sin agregar un segmento.

Cuando dos cosas pueden responder a la misma URL, **la primera registrada gana**, y Nexy siempre se registra en este orden:

1. el punto final de Acciones;
2. archivos estáticos: `/public`, `/assets`, `/favicon.ico`;
3. un modular `APIRouter` (`useRouter`);
4. rutas de archivos, las más específicas primero: rutas estáticas, luego rutas dinámicas con los segmentos más fijos y luego las generales.

Se registran dos rutas de archivos de igual especificidad en orden alfabético, por lo que `[id].nexy` responde antes de `[slug].nexy`. Por lo tanto, una ruta modular supera a una página con el mismo camino. Este es un orden de prioridad en el que puedes confiar, no una regla de desempate con la que jugar: asigna a una URL un archivo.

## El sistema de visualización

La extensión de un archivo decide qué es y la configuración del proyecto decide qué extensiones están activas.

| Extensión | Activo cuando | Compilado por | sirvió como |
|---|---|---|---|
| `.nexy` | modo servidor | Nexy: el frontmatter se convierte en Python, el marcado se convierte en Jinja2 | una pagina |
| `.md` | siempre | Nexy: Markdown con sabor a GitHub, identificadores de encabezado, tabla de contenido | una página, dentro del diseño más cercano |
| `.mdx` | siempre | Vite, con React o Preact | una ruta componente |
| `.tsx` | `useFF` es React, Solid o Preact | Vite y el marco | una ruta componente |
| `.vue` | `useFF` es Vue | Vite y Vue | una ruta componente |
| `.svelte` | `useFF` es Svelte | Vite y Svelte | una ruta componente |
| `.py` | siempre | Python | un controlador API: `GET`, `POST`, ... son los métodos |

Un archivo cuya extensión no está activa se omite con una advertencia y no se entrega. En modo cliente, `.nexy` se rechaza antes de que se inicie el servidor. Consulte [Convenciones de archivos](../reference/file-conventions.md).

## El ciclo de vida del renderizado

Tres preguntas deciden todo lo que nota el lector:

| Pregunta | respuesta | Página |
|---|---|---|
| ¿Quién produce el HTML? | el servidor o el navegador para una ruta de cliente | [Representación](../rendering/README.md) |
| ¿Cuándo se leen los datos? | en cada solicitud, en cada regeneración o en el navegador | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| ¿Cuándo llega JavaScript? | solo para una isla, o para todo el documento | [Islas](../rendering/islands.md), [RSC](../rendering/csr.md) |

En el modo servidor, el servidor representa cada página, `revalidate` almacena en caché una página por URL y las islas agregan JavaScript a un componente. En el modo cliente, el primer documento se representa en Node y luego la navegación se realiza en el navegador.

`__nexy__/` contiene todo lo generado: páginas compiladas, la entrada del cliente, la salida de la compilación. Nunca lo edites, nunca lo confirmes; elimínelo para forzar una compilación limpia.

## La integración frontal

**Vite no reemplaza a Nexy.** Vite agrupa y sirve código de cliente. No enruta una solicitud, no muestra una página `.nexy`, no ejecuta una acción ni posee el origen. El navegador se comunica con un origen, el de Nexy, y en el desarrollo, los servidores proxy de Nexy Vite se comunican a través de él, por lo que no hay CORS que configurar.

**Nexy no reemplaza a React.** Nexy decide qué componente se renderiza, cuándo y con qué accesorios; el marco posee el modelo de componente, la reactividad y el ecosistema. Una página `.nexy` importa un componente como una isla; en modo cliente una ruta *es* un componente.

Para una ruta de componente, Python escribe solo un módulo contenedor delgado que apunta al archivo. La compilación y el renderizado del lado del servidor son trabajo de Vite.

## Desarrollo y producción

`nx dev` verifica `nexyconfig.py`, compila las páginas, inicia Vite cuando el proyecto tiene un marco frontend y reinicia el servidor cuando guarda. `nx build` hace el mismo trabajo una vez, antes de tiempo, y `nx start` sirve el resultado.

| | `nx dev` | `nx build` luego `nx start` |
|---|---|---|
| paginas | compilado al guardar | compilado una vez, antes de tiempo |
| código de cliente | Vite servidor de desarrollo con recarga en caliente, detrás del propio origen de Nexy | paquete en `__nexy__/client/`, HTML prerenderizado |
| Node.js | corre al lado de Python | no es necesario para servir |
| Errores | superposición en el navegador, barra de herramientas en cada página | páginas de estado sin detalles |
| Origen | un puerto, `3000` | un puerto |

Lo que no cambia: las mismas reglas de enrutamiento, los mismos archivos de página, los mismos `nexyconfig.py`. Una página que se comporta de manera diferente entre las dos es un error, no un modo.

## Lo que te deja Nexy

Nexy se detiene en el borde de tu aplicación, a propósito:

| Preocupación | Qué ofrece Nexy | lo que escribes |
|---|---|---|
| Autenticación | middleware de sesión, `AuthenticationMiddleware` cuando está habilitado | el inicio de sesión, la búsqueda de usuarios, la política de cookies |
| Autorización | `dependencies.py`, guardias, herencia por carpeta | la regla misma |
| Base de datos | sin ORM propio; `nx new` puede hacer scaffolding SQLModel, SQLAlchemy o Tortoise, `nx migrate` ejecuta Alembic o Aerich | los modelos y las consultas ([Bases de datos](../guides/databases.md)) |
| Internacionalización | nada para tus páginas; sólo se traduce la CLI | la biblioteca y los mensajes ([i18n](../guides/i18n.md)) |
| Trabajos en segundo plano | nada: sin cola, sin planificador | un proceso de trabajo |
| Correo electrónico, pagos, búsqueda | nada | el servicio que elijas |

La razón es la misma para los seis: un marco que elige su ORM o su biblioteca de autenticación decide cosas que sólo su aplicación puede decidir. El costo es explícito: no hay nada cableado para usted y las guías vinculadas en la tabla indican dónde enchufar cada uno.

## Próximos pasos

- [Estructura del proyecto](project-structure.md): donde cada parte vive en un proyecto
- [Enrutamiento](../routing/README.md): los enrutadores personalizados, modulares y basados en archivos
- [Renderizado](../rendering/README.md): SSR, ISR, CSR e islas
- [Frontend](../guides/frontend.md): Vite, estilo y compilación del cliente
