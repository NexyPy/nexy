# Cómo funciona Nexy

El modelo mental en una página: qué construye Nexy, qué construye Vite y qué sucede entre un archivo
y una página en su navegador. Léelo una vez; el resto de la documentación es entonces un conjunto de detalles.

## La arquitectura Nexy

Una solicitud cruza cinco capas: Uvicorn la acepta, el middleware la decora, el enrutador selecciona un archivo,
el renderizador convierte ese archivo en HTML o JSON, y la capa del cliente se hace cargo si la página tiene
JavaScript. Nexy posee los tres del medio; Vite y su marco son dueños del cliente; tu aplicación
es propietaria de los datos, de la autenticación y de la autorización.

Cada capa, y lo que se niega a hacer, está en [Arquitectura](../architecture.md). Para los paquetes de
Nexy en sí, consulte `ARCHITECTURE.md` en la raíz del repositorio; está escrito para contribuyentes.

## El ciclo de vida de la aplicación

`nx dev` hace seis cosas antes de la primera solicitud:

1. valida `nexyconfig.py` y se detiene en una configuración no válida;
2. garantiza que los paquetes Python del proyecto sean importables;
3. resuelve los puertos y elimina el marcador obsoleto `__nexy__/nexy.prod`;
4. genera los archivos del cliente y compila las rutas, en paralelo;
5. inicia Vite y espera hasta que responda;
6. instala el observador de archivos y luego permite que uvicorn importe `nexy.modules.routers.app:_server`.

Esa importación ensambla la aplicación (middleware, acciones, enrutadores, controladores de errores) y el
la primera solicitud es atendida por esa asamblea. Cuando guarda, el observador reinicia uvicorn; una página que
apareció, desapareció o se movió también regenera la lista de rutas del cliente.

## El sistema de enrutamiento

Una ruta bajo `src/routes/` se convierte en una URL según cuatro reglas:

| Archivo | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

La extensión nunca aparece; `index` es la ruta de su carpeta; una carpeta entre paréntesis grupos
archivos sin agregar un segmento.

Cuando dos cosas pueden responder a la misma URL, **gana la primera registrada**, y Nexy siempre
se registra en este orden:

1. el punto final de Acciones;
2. archivos estáticos: `/public`, `/assets`, `/favicon.ico`;
3. a modular `APIRouter` (`useRouter`);
4. rutas de archivos, las más específicas primero: rutas estáticas, luego rutas dinámicas con los segmentos más fijos,
   luego lo general.

Se registran dos rutas de archivos de igual especificidad en orden alfabético, por lo que `[id].nexy`
respuestas antes de `[slug].nexy`. Por lo tanto, una ruta modular supera a una página con el mismo camino. Este es un
orden de precedencia en el que puede confiar, no una regla de desempate con la que jugar: asigne una URL a un archivo.

## El sistema de visualización

La extensión de un archivo decide qué es y la configuración del proyecto decide qué extensiones son
activo.

| Extensión | Activo cuando | Compilado por | Servido como |
|---|---|---|---|
| `.nexy` | modo servidor | Nexy: frontmatter se convierte en Python, el marcado se convierte en Jinja2 | una página |
| `.md` | siempre | Nexy: Markdown con sabor a GitHub, identificadores de encabezado, tabla de contenido | una página, dentro del diseño más cercano |
| `.mdx` | siempre | Vite, con React o Preact | una ruta componente |
| `.tsx` | `useFF` es React, Solid o Preact | Vite y el framework | una ruta de componentes |
| `.vue` | `useFF` es Vue | Vite y Vue | una ruta de componentes |
| `.svelte` | `useFF` es Svelte | Vite y Svelte | una ruta componente |
| `.py` | siempre | Python | un controlador API: `GET`, `POST`, ... son los métodos |

Un archivo cuya extensión no está activa se omite con una advertencia y no se entrega. En modo cliente, `.nexy`
es rechazado antes de que se inicie el servidor. Consulte [Convenciones de archivos](../reference/file-conventions.md).

## El ciclo de vida del renderizado

Tres preguntas deciden todo lo que nota el lector:

| Pregunta | Respuesta | Página |
|---|---|---|
| ¿Quién produce el HTML? | el servidor, o el navegador para una ruta de cliente | [Rendering](../rendering/README.md) |
| ¿Cuándo se leen los datos? | en cada solicitud, en cada regeneración o en el navegador | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| ¿Cuándo llega JavaScript? | solo para una isla, o para todo el documento | [Islas](../rendering/islands.md), [CSR](../rendering/csr.md) |

En el modo servidor, el servidor representa cada página, `revalidate` almacena en caché una página por URL y las islas agregan
JavaScript a un componente. En modo cliente, el primer documento se representa en Nodo y navegación.
luego sucede en el navegador.

`__nexy__/` contiene todo lo generado: páginas compiladas, la entrada del cliente, la salida de la compilación. nunca
edítelo, nunca lo confirme; elimínelo para forzar una compilación limpia.

## La integración frontend

**Vite no reemplaza a Nexy.** Vite agrupa y ofrece código de cliente. No enruta una solicitud,
renderizar una página `.nexy`, ejecutar una acción o poseer el origen. El navegador habla con un origen: el de Nexy.
y en desarrollo, Nexy representa los puntos finales de Vite a través de él, por lo que no hay CORS que configurar.

**Nexy no reemplaza a React.** Nexy decide qué componente se renderiza, cuándo y con qué accesorios;
el marco posee el modelo de componente, la reactividad y el ecosistema. Una página `.nexy` importa un
componente como una isla; en modo cliente una ruta *es* un componente.

Para la ruta de un componente, Python escribe solo un módulo contenedor delgado que apunta al archivo. el
La compilación y el renderizado del lado del servidor son trabajo de Vite.

## Desarrollo y producción

| | `nx dev` | `nx build` luego `nx start` |
|---|---|---|
| Páginas | compiladas al guardar | compiladas una vez, con anticipación |
| Código de cliente | Servidor de desarrollo Vite con recarga en caliente, detrás del paquete de origen propio de Nexy | en `__nexy__/client/`, HTML prerenderizado |
| Node.js | se ejecuta junto a Python | no es necesario para servir |
| Errores | superposición en el navegador, barra de herramientas en cada página | páginas de estado sin detalles |
| Origen | un puerto, `3000` | un puerto |

Lo que no cambia: las mismas reglas de enrutamiento, los mismos archivos de página, los mismos `nexyconfig.py`. una pagina
que se comporte de manera diferente entre los dos es un error, no un modo.

## Profundizando

- [Estructura del proyecto](project-structure.md): cada carpeta de un proyecto
- [Renderizado](../rendering/README.md): SSR, ISR, CSR e islas
- [Frontend](../guides/frontend.md): Vite, estilo y compilación del cliente
- [Enrutamiento](../routing/README.md): los enrutadores personalizados, modulares y basados en archivos