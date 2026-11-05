# Vincular y navegar

Con el enrutamiento del cliente (`useCSR = True`), un enlace entre dos páginas intercambia la página en el navegador en lugar de recargar el documento. Los diseños mantienen su estado.

## Los enlaces simples ya funcionan

Cada `<a href>` a una página de su proyecto navega en el cliente, sin componente ni marcador:

```html
<a href="/about">About</a>
```

Se deja un enlace en el navegador y se carga la página normalmente cuando:

- se mantiene presionada una tecla modificadora o el botón no es el principal;
- tiene `target` (distintos de `_self`), `download`, `rel="external"` o `data-nexy-reload`;
- el `href` es otro origen, un enlace `mailto:` o `tel:`, o sólo un `#fragment`;
- la ruta no coincide con ninguna ruta del cliente, por lo que el servidor responde.

## `Link`

`Link` es el mismo ancla con lo que uno simple no puede hacer: su `href` se compara con sus rutas, calienta la página de destino y sabe cuándo apunta a la página actual. Nexy genera el `Link` de tu framework en `__nexy__/src` cuando ejecutas `nx dev` o `nx build`.

| Marco | Importar |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| Proposición | Significado |
|---|---|
| `href` | Una ruta del proyecto (un error tipográfico es un error tipográfico), opcionalmente con `?query` o `#fragment`, o una URL externa. |
| `replace` | Reemplazar la entrada del historial en lugar de agregar una. |
| `scroll` | `false` mantiene la posición de desplazamiento después de navegar. Valor predeterminado: `true`. |
| `prefetch` | `'intent'` (predeterminado) carga la página al pasar el cursor, enfocar o tocar; `'viewport'` cuando el enlace aparece en la vista; `false` nunca. |
| `activeClassName` | Agregado a la clase mientras el enlace apunta a la página actual o a una página debajo de ella (`activeClass` en Vue y Svelte). |
| `exact` | Activo solo en la página exacta. |

El enlace que apunta a la página actual también obtiene `aria-current="page"`.

## Ganchos

La ubicación está disponible en cada marco, en el idioma de ese marco. Durante el primero, el lado del servidor procesa la respuesta de los enlaces con la URL de la solicitud, de modo que la página se hidrata sin discrepancias.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Ruta | `usePathname()` | `usePathname()` devuelve un descriptor de acceso | `usePathname()` devuelve una referencia | `$pathname` almacena |
| Parámetros de ruta | `useParams()` | `useParams()` descriptor de acceso | `useParams()` ref | `$params` store |
| Consulta | `useSearchParams()` | `useSearchParams()` descriptor de acceso | `useSearchParams()` ref | `$searchParams` tienda |
| Todo | `useLocation()` | `useLocation()` descriptor de acceso | `useLocation()` ref | `$location` tienda |
| Navegar | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

La consulta es un `URLSearchParams`. `useRouter()` y `router` dan `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` y `prefetch(href)`; `push` y `replace` aceptan `{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## `Image`

`Image` representa un `<img>` que es diferido por defecto y no cambia el diseño cuando se conoce su tamaño.

| Marco | Importación |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` es obligatorio; utilice `alt=""` para una imagen decorativa. Nexy avisa una vez cuando falta.
- Tanto con `width` como con `height`, los atributos le dan al navegador la relación de aspecto y la imagen se mantiene fluida (`height: auto; max-width: 100%`).
- `priority` carga la imagen ahora con alta prioridad, para la que es visible al llegar.
- `fill` hace que la imagen cubra su padre posicionado, ignorando `width` y `height`.
- `sizes` y `srcSet` pasan. Nexy no cambia el tamaño ni convierte las imágenes.

## Enlace desde una página `.nexy`

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` representa `<a href="/about" data-nexy-link="true">`. Cada atributo y el `href` tienen escape HTML.

## Qué hace el enrutador

En una navegación, el enrutador:

1. coincide con la ruta con las rutas del cliente (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. importa y representa la página y sus [diseños](../layouts/README.md) **primero**, y solo luego mueve la URL con `history.pushState`, de modo que la barra de direcciones nunca muestre una página que falló;
3. envía un evento `nexy:navigated` el `document`;
4. se desplaza hacia la parte superior o hacia el objetivo `#fragment`.

Una navegación más nueva cancela una anterior que aún se está procesando. Si una página no se puede representar, el navegador la solicita al servidor. Los botones de avance y retroceso muestran la página de esa entrada y restauran su posición de desplazamiento.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

El enrutador se inicia solo en un proyecto con rutas de cliente, por lo que un proyecto renderizado por el servidor mantiene el botón Atrás del navegador y la restauración de desplazamiento.

## Próximos pasos

- [Diseños](../layouts/README.md)
- [RSE](../../../rendering/csr.md)
- [Componentes](../../../views/nexy/components.md)
