# CSR (renderizado del lado del cliente)

## Definición

CSR entrega la navegación al navegador: después del primer documento, moverse entre páginas ya no solicita HTML al servidor. En Nexy es una decisión de **proyecto**, no de una página: `useCSR = True` convierte toda la aplicación en ruta al cliente.

## como funciona

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

El proyecto entonces cambia de forma:

| | Modo servidor (`False`) | Modo cliente (`True`) |
|---|---|---|
| Rutas | `.nexy`, `.md`, `.mdx` | `.tsx`, `.jsx`, `.vue`, `.svelte` |
| Documento | `layout.nexy` | la raíz `layout.tsx` / `.vue` / `.svelte` posee `<html>`, `<head>`, `<body>` |
| Componentes del cliente | islas dentro de una página | las páginas mismas |
| `.nexy` bajo `src/routes/` | el formato de página | rechazado antes de `nx dev`, `nx start` y `nx build` |
| Navegación | una solicitud completa por enlace | el enrutador del cliente |

`.md` y `.mdx` siguen siendo válidos: Nexy los representa en el servidor dentro del diseño del cliente, y el enrutador del cliente toma el control desde allí. `.py` controladores se sientan al lado de las rutas y son atendidos por FastAPI.

## Ciclo de vida de renderizado

1. La solicitud llega al enrutador basado en archivos, que encuentra la ruta coincidente y sus diseños.
2. El diseño raíz representa el **documento completo** en Node; la primera respuesta ya lleva el `<html>` real, no un shell vacío.
3. Nexy inyecta los activos del cliente y una descripción JSON de la página antes de `</body>`.
4. El navegador hidrata ese documento. Los diseños anidados mantienen su estado a partir de ese momento.
5. El enrutador del cliente maneja un enlace a otra ruta: no hay solicitud de documento, la página se muestra en el navegador.

En desarrollo, el documento es renderizado bajo demanda por el servidor de desarrollo Vite. En producción, se representa una vez en el momento de la compilación: una ruta estática obtiene su documento, una ruta dinámica obtiene uno por parámetro estático declarado, o un shell (los diseños alrededor de una página vacía) cuando no declara ninguno.

## cuando usar

- Paneles, editores, cualquier cosa que se comporte como una aplicación.
- Una Python API con una aplicación cliente encima.
- Una página donde cada interacción sea local y se sienta un ida y vuelta.

## Configuración

| Configuración | Valor |
|---|---|
| `useFF` | requerido: `useCSR` sin un marco de cliente es rechazado |
| `useCSR` | `True` |
| `useRouter` | debe permanecer apagado: el enrutador modular es rechazado en modo cliente |

Estas comprobaciones ignoran los archivos y carpetas que comienzan con `_` o `.`.

## Ejemplo

```tsx filename="src/rutas/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><title>My app</title></head>
      <body>{children}</body>
    </html>
  )
}
```

```tsx filename="src/rutas/index.tsx"
export default function Home() {
  return <h1>Home</h1>
}
```

## Pre-renderizar una ruta dinámica

Una ruta dinámica como `src/routes/blog/[slug].tsx` coincide con cualquier valor, por lo que la compilación no puede saber qué páginas representar. Exporte `generateStaticParams()` de la página para enumerarlos: `nexy build` genera un documento completo por entrada y `nexy start` lo sirve para esa ruta. Los nombres Next.js `getStaticPaths` y `getStaticParams` también se aceptan, y la función puede ser `async`.

```tsx filename="src/rutas/blog/[slug].tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }]
}

export default function Post({ slug }: { slug: string }) {
  return <h1>{slug}</h1>
}
```

Cada entrada es un objeto de parámetros, o `{ params: {...} }` como `getStaticPaths` los devuelve. La construcción escribe:

| Archivo en `__nexy__/client/static/` | servido para |
|---|---|
| `src/routes/blog/[slug]/blog/hello.html` | `/blog/hello` |
| `src/routes/blog/[slug]/blog/world.html` | `/blog/world` |
| `src/routes/blog/[slug].shell.html` | cualquier otro `/blog/...` |

Una ruta que la lista no nombra todavía funciona: obtiene el shell, los diseños alrededor de una página vacía y la página aparece una vez que se ha ejecutado el navegador. En `nexy dev` cada ruta se representa según demanda, esté listada o no.

## Limitaciones

- **Todo el proyecto.** No puedes mezclar una página CSR en un proyecto en modo servidor: elige el modo para la aplicación, luego usa [islas](islands.md) para las partes interactivas de una página en modo servidor.
- **No hay `.nexy` rutas.** Todo lo que escribas en `.nexy` tiene que convertirse en un componente del marco.
- **Los datos del servidor pasan por los puntos finales.** Una ruta de cliente no puede leer la base de datos en el momento del procesamiento; llama a un controlador `.py` o una [Acción](../guides/actions.md).
- **Una ruta dinámica comienza desde un shell a menos que enumere sus parámetros.** Consulte [Pre-renderizar una ruta dinámica](#pre-render-a-dynamic-route).
- **CSR no es una página en blanco, ni tampoco un SPA.** El primer documento lo procesa el servidor; es la navegación que ocurre en el navegador.

## Próximos pasos

- [Modo servidor y modo cliente](../routing/fbr/modes.md): los cheques y los archivos rechazados
- [Diseños](../routing/fbr/layouts/README.md): qué archivo posee el documento
- [SSR](ssr.md): el valor predeterminado, página por página
- [Frontend](../guides/frontend.md): el servidor de desarrollo y la compilación del cliente
