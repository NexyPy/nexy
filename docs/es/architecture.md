# Arquitectura

## Definición

Nexy tiene cinco capas y cada una tiene un trabajo que los demás no hacen. Conocer los límites responde a la mayoría
Preguntas de "¿por qué funciona así?": una página lenta es una pregunta sobre el renderizador, una página incorrecta es un enrutador
pregunta, una página que nunca aparece es una pregunta de cliente.

Esta página es para personas que escriben una solicitud. Los paquetes del propio Nexy y los mecanismos.
detrás de ellos, se describen en `ARCHITECTURE.md` en la raíz del repositorio, para contribuyentes.

## Las capas

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
| Uvicorn | acepta la conexión, habla ASGI | sabe qué es una página |
| Middleware | decora la solicitud: sesión, CORS, gzip, hosts confiables, redireccionamiento HTTPS, tuyo | elige una ruta |
| El enrutador | relaciona la URL con un archivo, con sus diseños, dependencias y páginas de error | produce contenido |
| Renderizador | ejecuta la página y convierte su resultado en HTML o JSON | recupera tus datos |
| Cliente | Vite y su marco: paquetes, hidratación, navegación del cliente | responder a una solicitud del servidor |

## ¿Quién construye qué?

| Actor | Posee | No posee |
|---|---|---|
| Nexy | enrutamiento, renderizado del servidor, acciones, `.nexy` compilación, componentes de un origen | reactividad, datos |
| Paquetes de clientes Vite | el servidor de desarrollo, recarga en caliente | enrutamiento, renderizado del servidor, Acciones |
| Su marco | componentes, reactividad, el ecosistema | enrutamiento, el documento (Nexy solicita su diseño) |
| Su aplicación | datos, autenticación, autorización, reglas de negocio | transporte, renderizado |

La regla detrás de la tabla: **Nexy construye lo que posee y nunca compila lo que compila Vite.** Para
una ruta de componente, Python escribe un módulo contenedor delgado que apunta al archivo.

## Donde se decide una solicitud

1. El middleware se ejecuta y puede cambiar la solicitud o detenerla.
2. El enrutador selecciona un archivo y los diseños que lo rodean.
3. El renderizador ejecuta ese archivo con los datos que él mismo lee.
4. La respuesta regresa y la capa del cliente toma el control si la página tiene JavaScript.

Cada paso, con la precedencia exacta entre enrutadores y el orden de `nx dev`, está en
[Cómo funciona Nexy](getting-started/how-nexy-works.md). Esta página no lo repite.

## Desarrollo y producción

Las mismas cinco capas, ensambladas dos veces:

| Capa | `nx dev` | `nx build` luego `nx start` |
|---|---|---|
| El compilador | se ejecuta cuando guardas | se ejecuta una vez, antes de tiempo |
| Servidor de desarrollo Vite | recarga en caliente, proxy a través del paquete de origen | de Nexy escrito en `__nexy__/client/`, sin servidor de desarrollo |
| El nodo | procesa los documentos del cliente a pedido | los procesa en el momento de la compilación, no mientras se entregan |
| Vigilante | reinicia uvicorn al cambiar | ausente |
| Origen | un puerto | un puerto |

Lo que cambia es *cuándo* se trabaja, no *quién* lo hace. Una página que se comporta de manera diferente entre las
two es un error en la página, no una propiedad del modo.

## Límites

Nexy se detiene en el borde de tu aplicación, a propósito:

| Preocupación | Lo que Nexy proporciona | Lo que escribes |
|---|---|---|
| Autenticación | middleware de sesión, `AuthenticationMiddleware` cuando está habilitado | el inicio de sesión, la búsqueda de usuarios, la política de cookies |
| Autorización | `dependencies.py`, guardias, herencia por carpeta | la regla misma |
| Base de datos | nada: sin ORM, sin migraciones | la capa del modelo ([Bases de datos](guides/databases.md)) |
| Internacionalización | nada para tus páginas; solo se traduce la CLI | la biblioteca y los mensajes ([i18n](guides/i18n.md)) |
| Trabajos en segundo plano | nada: sin cola, sin programador | un proceso de trabajo |
| Correo electrónico, pagos, búsqueda | nada | el servicio que elijas |

La razón es la misma para los seis: un marco que elige su ORM o su biblioteca de autenticación decide
cosas que sólo su aplicación puede decidir. El costo es explícito: no se le transfiere nada y el
Las páginas de guía anteriores indican dónde conectar cada uno.

## Próximos pasos

- [Cómo funciona Nexy](getting-started/how-nexy-works.md): una solicitud, paso a paso
- [Estructura del proyecto](getting-started/project-structure.md): dónde vive cada capa en un proyecto
- [Enrutamiento](routing/README.md): los tres enrutadores y cómo elegir
- [Renderizado](rendering/README.md): de donde viene el HTML