# Preacto

Nexy renderiza los componentes de Preact 10 en el servidor y luego Preact los toma en el navegador. páginas,
Los diseños, islas y acciones son los mismos en todos los marcos: esta página cubre la configuración, luego las partes.
que difieren de los [contratos compartidos](../frontend/pages.md).

| Modo | `nexyconfig.py` | Las páginas son | Preact es |
|---|---|---|---|
| Servidor (predeterminado) | `useCSR = False` | `.nexy` archivos | [islas](../../rendering/islands.md) dentro de esas páginas |
| Cliente | `useCSR = True` | `.tsx` archivos | toda la página, con [diseños](../frontend/layouts.md) y un enrutador cliente |

## Iniciar un proyecto

```bash
nx new my-app --template web-fbr-preact
```

La plantilla es un proyecto en modo servidor con islas Preact. Ejecute `nx new my-app` sin una plantilla para
En su lugar, responda las indicaciones: el enrutador, el tipo de proyecto, si desea utilizar el enrutamiento del lado del cliente y luego
el marco.

## Habilitar Preact en un proyecto existente

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` escribe este archivo; Nexy escribe `__nexy__/vite.ts` por sí mismo, así que no lo edites.

| Paquete | Versión `nx new` escribe |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (dependencia del desarrollador) |
| `preact-render-to-string` | `^6.7.0` (dependencia del desarrollador, renderizado en el servidor) |

## Escribir Preact

Un componente de Preact es una función de estilo React. Las diferencias que importan aquí:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- Los ganchos provienen de `preact/hooks`, tipos como `ComponentChildren` de `preact`.
- Escribir atributos HTML: `class`, `for`, `charset`. `Link` lee sus clases de `class`.

## Reglas

- **Un marco por proyecto.** `useFF` toma exactamente un marco; `useFF = [preact(), react()]`
  detiene el servidor al inicio. Con `useFF = preact()`, cada archivo `.tsx` es Preact.
- **Las páginas son `.tsx`.** Sólo un archivo `.tsx` bajo `src/routes/` se convierte en una página; `.jsx` está bien para un
  componente.
- **Los componentes viven fuera de `src/routes/`**, generalmente en `src/components/`, por lo que no son páginas.
- **Un proyecto en modo servidor no tiene `.tsx` página**, y un proyecto en modo cliente no tiene `.nexy` página: Nexy
  se niega a iniciar y nombra el archivo. Ver [modos](../../routing/fbr/modes.md).
- **Una página `.mdx` se importa desde `"preact"`.** Nexy compila un archivo `.mdx` con Preact solo cuando
  ve esa importación, por ejemplo `import { h } from "preact"`, y con React lo contrario. Ver
  [Markdown y MDX](../nexy/markdown.md).

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

Los parámetros de URL están disponibles a través del enlace `useParams`:

```tsx filename="src/rutas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Diseños

### Implementación

El diseño raíz define el shell del documento. Los diseños anidados envuelven el contenido.

```tsx filename="src/rutas/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## Islas

En modo servidor, un componente de Preact importado a un archivo `.nexy` es una isla.

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

Utilice el gancho `useAction` para administrar el estado de una llamada a la acción:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### Navegación

Utilice el componente `Link` para transiciones del lado del cliente. Tenga en cuenta que Preact utiliza `class` en lugar de
`className`:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

Para navegación programática, use el gancho `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Acceso URL

- `usePathname()`: ruta actual
- `useParams()`: segmentos dinámicos
- `useSearchParams()`: cadena de consulta
- `useLocation()`: objeto de ubicación completa

## Próximos pasos

- [Vistas](../README.md): compara los formatos que puede usar una página
- [Frontend](../../guides/frontend.md): Vite y la compilación del cliente