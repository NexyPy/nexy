# Arquitectura

## Definición

Nexy tiene cinco capas y cada una tiene un trabajo que los demás no hacen. Conocer el límite responde a la mayoría de las preguntas de "¿por qué funciona así?": una página lenta es una pregunta del renderizador, una página incorrecta es una pregunta del enrutador, una página que nunca aparece es una pregunta del cliente.

Esta página es para personas que escriben una solicitud. Los paquetes de Nexy y los mecanismos detrás de ellos se describen en `ARCHITECTURE.md` en la raíz del repositorio, para contribuyentes.

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

| Capa | Responsabilidad | No |
|---|---|---|
| Uvicorn | aceptar la conexión, hablar ASGI | saber qué es una página |
| Middleware | decora la solicitud: sesión, CORS, gzip, hosts confiables, redireccionamiento HTTPS, tuyo | elige una ruta |
| El enrutador | relaciona la URL con un archivo, con sus diseños, dependencias y páginas de error | produce contenido |
| El renderizador | ejecuta la página y convierte su resultado en HTML o JSON | recupera sus datos |
| Cliente | Vite y su marco: paquetes, hidratación, navegación del cliente | responden a una solicitud del servidor |

## ¿Quién construye qué?

| Actor | Posee | No posee |
|---|---|---|
| Nexy | enrutamiento, renderizado del servidor, acciones, `.nexy` compilación, componentes de un origen | reactividad, datos |
| Vite | paquetes de clientes, el servidor de desarrollo, recarga en caliente | enrutamiento, renderizado del servidor, acciones |
| Los componentes de su marco | la reactividad, el ecosistema | el enrutamiento, el documento (Nexy solicita su diseño) |
| Su aplicación | datos, autenticación, autorización, reglas de negocio | transporte, renderizado |

La regla detrás de la tabla: **Nexy construye lo que posee y nunca compila lo que Vite compila.** Para una ruta de componente, Python escribe un módulo contenedor delgado que apunta al archivo.

## Donde se decide una solicitud

1. El middleware se ejecuta y puede cambiar la solicitud o detenerla.
2. El enrutador elige un archivo y los diseños que lo rodean.
3. El renderizador ejecuta ese archivo con los datos que él mismo lee.
4. La respuesta regresa y la capa del cliente toma el control si la página tiene JavaScript.

Cada paso, con la precedencia exacta entre enrutadores y el orden de `nx dev`, se encuentra en [Cómo funciona Nexy](getting-started/how-nexy-works.md). Esta página no lo repite.

## Desarrollo y producción

Las mismas cinco capas, ensambladas dos veces:

| Capa | `nx dev` | `nx build` luego `nx start` |
|---|---|---|
| El compilador | se ejecuta cuando guarda | se ejecuta una vez, antes de tiempo |
| Vite | servidor de desarrollo, recarga en caliente, proxy a través del paquete de origen de Nexy | escrito en `__nexy__/client/`, sin servidor de desarrollo |
| El nodo | procesa los documentos del cliente a pedido | los procesa en el momento de la compilación, no mientras se entregan |
| Watcher | reinicia uvicorn al cambiar | ausente |
| Origen | un puerto | un puerto |

Lo que cambia es *cuándo* se trabaja, no *quién* lo hace. Una página que se comporta de manera diferente entre las dos es un error en la página, no una propiedad del modo.

## Límites

Nexy se detiene en el borde de tu aplicación, a propósito:

| Preocupación | Qué proporciona Nexy | Qué escribes |
|---|---|---|
| Autenticación | middleware de sesión, `AuthenticationMiddleware` cuando está habilitado | el inicio de sesión, la búsqueda de usuarios, la política de cookies |
| Autorización | `dependencies.py`, guardias, herencia por carpeta | la regla misma |
| Base de datos | nada: sin ORM, sin migraciones | la capa del modelo ([Bases de datos](guides/databases.md)) |
| Internacionalización | nada para sus páginas; solo se traduce la CLI | la biblioteca y los mensajes ([i18n](guides/i18n.md)) |
| Trabajos en segundo plano | nada: sin cola, sin programador | un proceso de trabajo |
| Correo electrónico, pagos, búsqueda | nada | el servicio que elijas |

La razón es la misma para los seis: un marco que elige su ORM o su biblioteca de autenticación decide cosas que sólo su aplicación puede decidir. El costo es explícito: no hay nada cableado para usted y las páginas de guía anteriores indican dónde enchufar cada uno.

## Próximos pasos

- [Cómo funciona Nexy](getting-started/how-nexy-works.md): una solicitud, paso a paso
- [Estructura del proyecto](getting-started/project-structure.md): dónde vive cada capa en un proyecto
- [Enrutamiento](routing/README.md): los tres enrutadores y cómo elegir
- [Renderizado](rendering/README.md): de donde viene el HTML
