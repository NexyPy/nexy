# Cómo funciona Nexy

El modelo mental en una página: qué construye Nexy, qué construye Vite y qué sucede entre un archivo y una página en su navegador. Léelo una vez; el resto de la documentación es entonces un conjunto de detalles.

## La arquitectura Nexy

Una solicitud cruza cinco capas: Uvicorn la acepta, el middleware la decora, el enrutador selecciona un archivo, el renderizador convierte ese archivo en HTML o JSON y la capa del cliente se hace cargo si la página tiene JavaScript. Nexy posee los tres del medio; Vite y su marco son propietarios del cliente; su aplicación es propietaria de los datos, la autenticación y la autorización.

Cada capa, y lo que se niega a hacer, está en [Arquitectura](../architecture.md). Para los paquetes de Nexy, consulte `ARCHITECTURE.md` en la raíz del repositorio; está escrito para contribuyentes.

## El ciclo de vida de la aplicación

`nx dev` hace seis cosas antes de la primera solicitud:

1. valida `nexyconfig.py` y se detiene en una configuración no válida;
2. garantiza que los paquetes Python del proyecto sean importables;
3. resuelve los puertos y elimina el marcador obsoleto `__nexy__/nexy.prod`;
4. genera los archivos del cliente y compila las rutas, en paralelo;
5. inicia Vite y espera hasta que responda;
6. instala el observador de archivos y luego permite que uvicorn importe `nexy.modules.routers.app:_server`.

Esa importación ensambla la aplicación (middleware, acciones, enrutadores, controladores de errores) y ese ensamblado atiende la primera solicitud. Cuando guarda, el observador reinicia uvicorn; una página que apareció, desapareció o se movió también regenera la lista de rutas del cliente.

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

| Extensión | Activa cuando | Compilada por | Servida como |
|---|---|---|---|
| `.nexy` | modo servidor | Nexy: el frontmatter se convierte en Python, el marcado se convierte en Jinja2 | una página |
| `.md` | siempre | Nexy: con sabor a GitHub Markdown, identificadores de encabezado, tabla de contenido | una página, dentro del diseño más cercano |
| `.mdx` | siempre | Vite, con React o Preact | una ruta componente |
| `.tsx` | `useFF` es React, Solid o Preact | Vite y el marco | una ruta componente |
| `.vue` | `useFF` es Vue | Vite y Vue | una ruta componente |
| `.svelte` | `useFF` es Svelte | Vite y Svelte | una ruta componente |
| `.py` | siempre | Python | un manejador API: `GET`, `POST`, ... son los métodos |

Un archivo cuya extensión no está activa se omite con una advertencia y no se entrega. En modo cliente, `.nexy` se rechaza antes de que se inicie el servidor. Consulte [Convenciones de archivos](../reference/file-conventions.md).

## El ciclo de vida del renderizado

Tres preguntas deciden todo lo que nota el lector:

| Pregunta | Respuesta | Página |
|---|---|---|
| ¿Quién produce el HTML? | el servidor, o el navegador para una ruta de cliente | [Rendering](../rendering/README.md) |
| ¿Cuándo se leen los datos? | en cada solicitud, en cada regeneración o en el navegador | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| ¿Cuándo llega JavaScript? | solo para una isla, o para todo el documento | [Islas](../rendering/islands.md), [CSR](../rendering/csr.md) |

En el modo servidor, el servidor representa cada página, `revalidate` almacena en caché una página por URL y las islas agregan JavaScript a un componente. En el modo cliente, el primer documento se representa en Node y luego la navegación se realiza en el navegador.

`__nexy__/` contiene todo lo generado: páginas compiladas, la entrada del cliente, la salida de la compilación. Nunca lo edites, nunca lo confirmes; elimínelo para forzar una compilación limpia.

## La integración frontal

**Vite no reemplaza a Nexy.** Vite agrupa y sirve código de cliente. No enruta una solicitud, no muestra una `.nexy` página, no ejecuta una acción ni posee el origen. El navegador se comunica con un origen, el de Nexy, y en desarrollo, los puntos finales de Nexy Vite lo atraviesan, por lo que no hay CORS que configurar.

**Nexy no reemplaza a React.** Nexy decide qué componente se renderiza, cuándo y con qué accesorios; el marco posee el modelo de componente, la reactividad y el ecosistema. Una página `.nexy` importa un componente como una isla; en modo cliente una ruta *es* un componente.

Para la ruta de un componente, Python escribe solo un módulo contenedor delgado que apunta al archivo. La compilación y el renderizado del lado del servidor son trabajo de Vite.

## Desarrollo y producción

| | `nx dev` | `nx build` luego `nx start` |
|---|---|---|
| Páginas | compiladas al guardar | compiladas una vez, con anticipación |
| Código de cliente | Vite servidor de desarrollo con recarga en caliente, detrás del paquete de origen propio de Nexy | en `__nexy__/client/`, HTML prerenderizado |
| Node.js | corre al lado de Python | no es necesario para publicar |
| Errores | superposición en el navegador, barra de herramientas en cada página | páginas de estado sin detalles |
| Origen | un puerto, `3000` | un puerto |

Lo que no cambia: las mismas reglas de enrutamiento, los mismos archivos de página, los mismos `nexyconfig.py`. Una página que se comporta de manera diferente entre las dos es un error, no un modo.

## Profundizando

- [Estructura del proyecto](project-structure.md): cada carpeta de un proyecto
- [Renderizado](../rendering/README.md): SSR, ISR, CSR e islas
- [Frontend](../guides/frontend.md): Vite, estilo y compilación del cliente
- [Enrutamiento](../routing/README.md): los enrutadores personalizados, modulares y basados en archivos
