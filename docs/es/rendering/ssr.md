# SSR (renderizado del servidor)

## Definición

SSR es el valor predeterminado: el servidor representa la página en HTML para cada solicitud. Nada lo habilita y ningún indicador lo desactiva: un proyecto en modo servidor se procesa en cada solicitud a menos que una página declare `revalidate`.

## como funciona

| Archivo de ruta | ¿Qué produce el HTML? | cuando |
|---|---|---|
| `.nexy` | el módulo compilado Python, hasta Jinja2 | cada solicitud |
| `.md` | Markdown, luego el diseño más cercano | cada solicitud |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | el marco, representado en Node | en la compilación cuando la ruta no tiene diseño; de lo contrario, en el navegador |
| `.py` | nada: devuelve JSON o un `Response` | - |

Una ruta componente es el único caso que necesita una segunda oración. En producción, una ruta de componente **sin** un diseño se entrega con el HTML producido en la compilación y el componente lo hidrata. Con un diseño, o en desarrollo, el contenedor está vacío y el componente se representa en el navegador; la página es entonces un caparazón que se llena solo.

## Ciclo de vida de renderizado

1. La solicitud llega al enrutador basado en archivos. La ruta coincide y los segmentos dinámicos se convierten en los tipos que declara el componente.
2. El componente se ejecuta. Uno que espera en Node (un documento de cliente) se ejecuta en un grupo de subprocesos, por lo que no detiene el bucle de eventos.
3. El cuerpo se transmite como `text/html`. Un componente que produce trozos los transmite a medida que los produce.
4. El navegador recibe HTML. Las islas se hidratan según su [directiva](islands.md).

Un error generado durante el renderizado se convierte en una página mediante `errors.nexy` cuando el proyecto tiene una: consulte [páginas de error](../routing/fbr/errors/README.md).

## cuando usar

- La página muestra algo que pertenece al lector: una sesión, una cuenta, un carrito.
- Los datos deben estar actualizados en cada carga.
- El contenido debe estar en HTML para los rastreadores que no ejecutan JavaScript.
- La página es barata de renderizar: una consulta, una plantilla.

## Configuración

Ninguno. Dos salidas y no tienen el mismo grano:

| Dejar SSR por | haz esto | grano |
|---|---|---|
| una página, con un caché | `revalidate = 60` en su introducción → [ISR](isr.md) | página |
| todo el proyecto, enrutado por el cliente | `useCSR = True` en `nexyconfig.py` → [RSE](csr.md) | proyecto |

## Ejemplo

```nexy filename="src/rutas/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` ejecuta esta plantilla una vez, con `slug` establecida en `hello`. Una segunda solicitud lo ejecuta nuevamente: no se guarda nada entre los dos. La cadena de consulta no es un accesorio; léala con los ganchos en [navegación](../routing/fbr/navigation/hooks.md).

## Limitaciones

- **Un render por solicitud.** Dos visitantes en el mismo segundo pagan cada uno por el render y por las consultas detrás de él.
- **Sin caché.** No hay un caché de respuesta compartido para calentar: [ISR](isr.md) agrega uno por URL.
- **La transmisión por secuencias solo ayuda a un componente que produce rendimiento.** Una consulta lenta en la parte superior de la página aún retrasa el primer byte.
- **Sin salida estática.** En el modo servidor, nada se congela en la compilación: no hay modo SSG ni comando de exportación. Consulte [Renderizado](README.md).
- **El escape automático está desactivado** en `.nexy` plantillas. Escapa de valores que no son de confianza con `| e`.

## Próximos pasos

- [ISR](isr.md): almacena en caché esta página por URL
- [Islas](islands.md): mantenga SSR y haga que un widget sea interactivo
- [CSR](csr.md): navegación manual al navegador
- [Rendimiento](../deployment/performance.md)
