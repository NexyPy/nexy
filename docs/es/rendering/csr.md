# CSR (renderizado del lado del cliente)

## Definición

CSR transfiere la navegación al navegador: después del primer documento, ya no es necesario moverse entre páginas
el servidor para HTML. En Nexy es una decisión de **proyecto**, no de una página: `useCSR = True` convierte el
toda la aplicación enrutada por el cliente.

## Cómo funciona

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

`.md` y `.mdx` siguen siendo válidos: Nexy los representa en el servidor dentro del diseño del cliente, y el
El enrutador del cliente toma el control desde allí. `.py` controladores se ubican junto a las rutas y son atendidos por FastAPI.

## Ciclo de vida de renderizado

1. La solicitud llega al enrutador basado en archivos, que encuentra la ruta coincidente y sus diseños.
2. El diseño raíz muestra el **documento completo** en Node: la primera respuesta ya lleva el
   real `<html>`, no un caparazón vacío.
3. Nexy inyecta los activos del cliente y una descripción JSON de la página antes de `</body>`.
4. El navegador hidrata ese documento. Los diseños anidados mantienen su estado a partir de ese momento.
5. Un enlace a otra ruta es manejado por el enrutador del cliente: no hay solicitud de documento, la página es
   renderizado en el navegador.

En desarrollo, el servidor de desarrollo de Vite procesa el documento bajo demanda. En producción es
renderizado una vez en la compilación: una ruta estática obtiene su documento, una ruta dinámica obtiene uno por declarado
parámetro estático, o un shell (los diseños alrededor de una página vacía) cuando no declara ninguno.

## Cuándo usar

- Paneles de control, editores, cualquier cosa que se comporte como una aplicación.
- Una API de Python con una aplicación cliente encima.
- Una página donde cada interacción es local y se sentiría un viaje de ida y vuelta.

## Configuración

| Configuración | Valor |
|---|---|
| `useFF` | requerido: `useCSR` sin un marco de cliente es rechazado |
| `useCSR` | `True` |
| `useRouter` | debe permanecer apagado: el router modular es rechazado en modo cliente |

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

## Limitaciones

- **El proyecto completo.** No puedes mezclar una página CSR en un proyecto en modo servidor: elige el modo para
  la aplicación, luego use [islands](islands.md) para las partes interactivas de una página en modo servidor.
- **No hay `.nexy` rutas.** Todo lo que escribas en `.nexy` tiene que convertirse en un componente del marco.
- **Los datos del servidor pasan a través de puntos finales.** Una ruta de cliente no puede leer la base de datos en el momento del procesamiento; eso
  llama a un controlador `.py` o una [Acción](../guides/actions.md).
- **Una ruta dinámica necesita un parámetro estático declarado o comienza desde un shell.** Exportar
  `getStaticParams()` de la página: los nombres de Next.js `getStaticPaths` y `generateStaticParams`
  También se aceptan - tener un documento por valor. Sin él, el caparazón lleva los diseños y
  no la página: la página aparece una vez que se ha ejecutado el navegador.
- **CSR no es una página en blanco, ni tampoco un SPA.** El primer documento lo procesa el servidor; eso
  es la navegación que ocurre en el navegador.

## Próximos pasos

- [Modo servidor y modo cliente](../routing/fbr/modes.md): los cheques y los archivos rechazados
- [Layouts](../routing/fbr/layouts/README.md): a qué archivo pertenece el documento
- [SSR](ssr.md): el valor predeterminado, página por página
- [Frontend](../guides/frontend.md): la compilación del servidor de desarrollo y del cliente