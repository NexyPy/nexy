# Representación

El renderizado responde a una pregunta: **quién produce el HTML y cuándo**. Nexy tiene cuatro respuestas y una
predeterminado.

**¿No estás seguro? Mantenga SSR.** Cambie una página solo cuando pueda indicar el motivo: contenido que rara vez cambia
(ISR), un widget que necesita el navegador (isla) o navegación similar a una aplicación (CSR).

## Cómo funciona

```diagram filename="¿Quién produce el HTML y cuándo?"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## Los cuatro modos

| | SSR | ISR | CSR | Islas |
|---|---|---|---|---|
| Los datos se leen | en cada solicitud | en cada regeneración | en el navegador | en cada solicitud |
| El HTML proviene de | el servidor | el servidor, luego un caché | el servidor para el primer documento, el navegador después | el servidor |
| JavaScript | solo para islas | solo para islas | el paquete de marco | solo la isla |
| Hidratación | ninguna | ninguna | el documento completo | la isla |
| Caché | ninguno | por URL, en memoria | ninguno | ninguno |
| Decidido por | predeterminado | `revalidate = N` en la página | `useCSR = True` en el proyecto | `directive` en el componente |
| Grano | página | página | **proyecto** | componente |

## Ciclo de vida de renderizado

Dos hechos explican la mayoría de las sorpresas.

1. **Un proyecto está en un modo.** `useCSR` elige entre modo servidor (SSR, ISR, islas, `.nexy`,
   `.md`, `.mdx` rutas) y modo cliente (rutas de marco y un enrutador cliente). Los dos no pueden ser
   mixto: consulte [modo servidor y modo cliente](../routing/fbr/modes.md).
2. **Dentro del modo servidor, el modo es por página.** Una página se puede almacenar en caché con `revalidate`, otra
   puede ocupar una isla, un tercero no puede hacer ninguna de las dos cosas.

El modo cliente todavía envía un documento real: Nexy lo representa en Node para la primera respuesta, luego el
El navegador se hace cargo de la navegación. Una página de CSR no es una página en blanco esperando un paquete.

## Cuándo usar

- **Contenido, marketing, documentación**: SSR, más ISR cuando el contenido rara vez cambia.
- **Una página mayoritariamente estática con un widget interactivo**: SSR con una isla.
- **Paneles de control, editores, navegación tipo aplicación**: CSR.
- **Una página leída constantemente y rara vez cambiada**: ISR.

## Configuración

| Modo | Donde |
|---|---|
| SSR | en ninguna parte: es el valor predeterminado |
| ISR | `revalidate = 60` en la portada de una `.nexy` página |
| CSR | `useCSR = True` en `nexyconfig.py`, con `useFF` establecido |
| Islas | `directive="client:visible"` en la etiqueta del componente |

## Ejemplo

```nexy filename="src/rutas/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

La misma página sin la primera línea es SSR.

## Limitaciones

- **No hay modo SSG.** Nexy preprocesa HTML en el momento de la compilación (componentes HTML, documentos del cliente),
  pero siempre lo lee a través del servidor: sin comando de exportación, sin carpeta independiente para alojar
  estáticamente. Para contenido congelado, utilice ISR con una ventana larga.
- **ISR no es una CDN.** El caché reside en el proceso que representa la página; varios trabajadores mantienen
  varios cachés. Véase [ISR](isr.md).
- **La CSR es una decisión del proyecto.** No se puede hacer una CSR de una página y conservar el resto de la SSR.
- **Las islas hidratan la isla, no la página.** Una página cuyas islas dependen unas de otras es una
  Página de RSC disfrazada.

## Próximos pasos

- [SSR](ssr.md): el valor predeterminado
- [ISR](isr.md): almacena en caché una página por URL
- [CSR](csr.md): navegación manual al navegador
- [Islas](islands.md): hidratar un widget
- [Rendimiento](../deployment/performance.md)