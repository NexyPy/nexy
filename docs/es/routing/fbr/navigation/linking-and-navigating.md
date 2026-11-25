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

| Prop | Significado |
|---|---|
| `href` | Una ruta del proyecto (un error tipográfico es un error tipográfico), opcionalmente con `?query` o `#fragment`, o una URL externa. |
| `replace` | Reemplace la entrada del historial en lugar de agregar una. |
| `scroll` | `false` mantiene la posición de desplazamiento después de navegar. Valor predeterminado: `true`. |
| `prefetch` | `'intent'` (predeterminado) carga la página al pasar el cursor, enfocar o tocar; `'viewport'` cuando el enlace aparece en la vista; `false` nunca. |
| `activeClassName` | Se agrega a la clase mientras el enlace apunta a la página actual o a una página debajo de ella (`activeClass` en Vue y Svelte). |
| `exact` | Activo sólo en la página exacta. |

El enlace que apunta a la página actual también obtiene `aria-current="page"`.

## Ganchos

La ubicación está disponible en cada marco, en el idioma de ese marco. Durante el primero, el lado del servidor procesa la respuesta de los enlaces con la URL de la solicitud, de modo que la página se hidrata sin discrepancias.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Camino | `usePathname()` | `usePathname()` devuelve un descriptor de acceso | `usePathname()` devuelve una referencia | `$pathname` tienda |
| Parámetros de ruta | `useParams()` | `useParams()` descriptor de acceso | `useParams()` referencia | `$params` tienda |
| Consulta | `useSearchParams()` | `useSearchParams()` descriptor de acceso | `useSearchParams()` referencia | `$searchParams` tienda |
| todo | `useLocation()` | `useLocation()` descriptor de acceso | `useLocation()` referencia | `$location` tienda |
| Navegar | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| Navegación en vuelo | `useTransition()` | `useTransition()` descriptor de acceso | `useTransition()` referencia | `useTransition()` tienda |
| Emparejar un camino | `useMatch(path?)` | `useMatch(path?)` descriptor de acceso | `useMatch(path?)` referencia | `useMatch(path?)` tienda |
| Pregunta antes de salir | `useBlocker(dirty)` | `useBlocker(dirty())` en `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` en `$effect` |

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

## Mostrar un estado de carga con `useTransition`

`useTransition()` indica si la navegación de un cliente está en vuelo. `pending` es `true` desde el clic hasta que se muestra la página siguiente, y `next` es la ubicación a la que se dirige. Vuelve a `{ pending: false, next: null }` una vez que se muestra la página, cuando se detiene la navegación o cuando una nueva la reemplaza.

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## Haga coincidir una ruta con `useMatch`

`useMatch(path)` indica si `path` coincide con una ruta de cliente. Devuelve `{ match, found }`, donde `match` contiene la ruta `file`, su `layouts` y su `params`, o es `null`. Sin una ruta, coincide con la página actual y sigue cada navegación. Durante el renderizado del servidor todavía no hay ningún enrutador, por lo que `match` es `null` y `found` es `false`.

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## Capte una página que falla con `ErrorBoundary`

`ErrorBoundary` muestra un respaldo en lugar de sus hijos cuando uno de ellos lanza mientras se procesa en el navegador. El respaldo recibe el error y `reset`, lo que muestra a los niños nuevamente.

| Marco | Importar | Respaldo |
|---|---|---|
| React, Preact, Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | una función `fallback` prop; los niños van en el espacio predeterminado |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | un fragmento de `fallback` |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

No atrapa:

- un error arrojado más tarde, en un controlador de eventos, un temporizador o una promesa: atraparlo donde sucede. Vue es la excepción para sus propios controladores de eventos, cuyos errores alcanzan el límite;
- una página que el enrutador no puede cargar: el navegador la solicita al servidor (consulte [Qué hace el enrutador](#what-the-router-does)).

## Preguntar antes de abandonar una página con cambios no guardados

`useBlocker(dirty, message?)` pregunta al visitante antes de irse mientras que `dirty` es cierto: un enlace, un `router.push`, los botones de avance y retroceso, una recarga y una pestaña cerrada. La navegación de un cliente muestra `message` en `confirm()`: sí continúa, no permanece en la página. Una recarga o una pestaña cerrada muestra la propia pregunta del navegador, que ninguna página puede redactar. Sin un mensaje, la pregunta es "Tienes cambios no guardados. ¿Salir de esta página?".

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

La bandera se lee donde cambia, en el idioma de cada marco:

| Marco | Sigue la bandera |
|---|---|
| React, Preact | `useBlocker(dirty)` en cada render |
| Vue | `useBlocker(dirty)` con `dirty` una referencia o un cálculo |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` también toma una función, para una decisión que depende de dónde va el visitante. Recibe la siguiente ubicación y la actual, y devuelve un motivo (una cadena) para quedarse, o nada para continuar:

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

Una función no pregunta por sí sola y no retiene una recarga; Llame al `confirm()` para preguntar.

## `Image`

`Image` representa un `<img>` que es diferido por defecto y no cambia el diseño cuando se conoce su tamaño.

| Marco | Importar |
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

El intercambio de página se ejecuta dentro de una transición de vista del navegador cuando hay una disponible: consulte [Cómo funcionan las transiciones de página](page-transitions.md).

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
