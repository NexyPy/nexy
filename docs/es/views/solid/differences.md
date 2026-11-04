# Sólido

Nexy renderiza los componentes de Solid 1.9 en el servidor y luego Solid los toma en el navegador. páginas,
Los diseños, islas y acciones son los mismos en todos los marcos: esta página cubre la configuración, luego las partes.
que difieren de los [contratos compartidos](../frontend/pages.md).

| Modo | `nexyconfig.py` | Las páginas son | El sólido es |
|---|---|---|---|
| Servidor (predeterminado) | `useCSR = False` | `.nexy` archivos | [islas](../../rendering/islands.md) dentro de esas páginas |
| Cliente | `useCSR = True` | `.tsx` archivos | toda la página, con [diseños](../frontend/layouts.md) y un enrutador cliente |

## Iniciar un proyecto

```bash
nx new my-app --template web-fbr-solid
```

La plantilla es un proyecto en modo servidor con islas Solid. Ejecute `nx new my-app` sin una plantilla para
En su lugar, responda las indicaciones: el enrutador, el tipo de proyecto, si desea utilizar el enrutamiento del lado del cliente y luego
el marco.

## Habilitar Sólido en un proyecto existente

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

En modo cliente escriba `solid({ ssr: true })`: Solid compila un componente de manera diferente para el servidor
y para el navegador, y el modo cliente necesita ambos. `nx new` escribe este archivo; Nexy escribe
`__nexy__/vite.ts` en sí, así que no lo edites.

| Paquete | Versión `nx new` escribe |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (dependencia del desarrollador) |

## Piensa en señales

Una función de componente sólido se ejecuta **una vez**. Lo que cambia después se lee a través de una señal, y sólo el
las expresiones que lo leen se actualizan:

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- Llame a la señal, `count()`, dentro del JSX, no en una variable encima de él.
- Lea los accesorios como `props.start`. La desestructuración `{ start }` lee el valor una vez y pierde las actualizaciones.
- Solid escribe atributos HTML: `class`, `for`, `charset`, no `className`.

## Reglas

- **Un marco por proyecto.** `useFF` toma exactamente un marco; `useFF = [solid(), react()]`
  detiene el servidor al inicio. Con `useFF = solid()`, cada archivo `.tsx` es Sólido.
- **Las páginas son `.tsx`.** Sólo un archivo `.tsx` bajo `src/routes/` se convierte en una página; `.jsx` está bien para un
  componente.
- **Los componentes viven fuera de `src/routes/`**, generalmente en `src/components/`, por lo que no son páginas.
- **Un proyecto en modo servidor no tiene `.tsx` página**, y un proyecto en modo cliente no tiene `.nexy` página: Nexy
  se niega a iniciar y nombra el archivo. Ver [modos](../../routing/fbr/modes.md).
- **No `.mdx` con Solid.** MDX compila en React o Preact; `.md` páginas funcionan.

## Páginas

En modo cliente (`useCSR = True`), una página es un archivo `.tsx`.

### Componente de página

Una página es la exportación predeterminada del archivo. Si no existe una exportación predeterminada, Nexy elige la primera nombrada
exportar.

```tsx filename="src/rutas/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Segmentos dinámicos

Los parámetros de URL están disponibles a través del enlace `useParams`, que devuelve un descriptor de acceso:

```tsx filename="src/rutas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## Diseños

### Implementación

El diseño raíz define el shell del documento. Los diseños anidados envuelven el contenido.

```tsx filename="src/rutas/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

No desestructurar `props.children`, como Solid lo lee con pereza.

## Islas

En modo servidor, un componente Solid importado a un archivo `.nexy` es una isla.

### Importando

Importe componentes en la portada del archivo `.nexy`:

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### Directivas de hidratación

Utilice el accesorio `directive` para controlar cuándo se hidrata la isla:

- `client:load` (predeterminado): inmediatamente
- `client:idle`: cuando el navegador está inactivo
- `client:visible`: cuando se desplaza a la vista
- `client:media`: cuando la consulta de medios coincide

## Acciones y navegación

### Llamando acciones

Utilice el gancho `useAction` para administrar el estado de una llamada a la acción. En Solid, esto devuelve accesores (llame
ellos como funciones).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### Navegación

Utilice el componente `Link` para transiciones del lado del cliente:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

Para navegación programática, use el gancho `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Acceso URL

Todos los ganchos de ubicación devuelven descriptores de acceso:

- `usePathname()`: ruta actual
- `useParams()`: segmentos dinámicos
- `useSearchParams()`: cadena de consulta
- `useLocation()`: objeto de ubicación completa

## Próximos pasos

- [Vistas](../README.md): compara los formatos que puede usar una página
- [Frontend](../../guides/frontend.md): Vite y la compilación del cliente