# Estructura del proyecto

Cada archivo en un proyecto Nexy tiene un trabajo. Esta página dice cuál.

## Nivel superior

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Para elegir una carpeta, pregunte cuál es el archivo:

- **Algo que el navegador puede abrir** - una ruta: `src/routes/`.
- **Una pieza utilizada por varias rutas** - un componente o un módulo: `src/components/`, `src/`.
- **Un archivo servido tal como está** - `public/`.
- **Un controlador del enrutador modular** - `src/apps/`.
- **Generado** - `__nexy__/`; nunca lo edites.

> [!WARNING]
> `src/routes/` es escaneado: un ayudante colocado allí se convierte en una ruta. Coloque un ayudante que no sea una ruta fuera de `src/routes/`, o comience su nombre con `_`.

## `src/routes/`

Cada archivo se convierte en una ruta, excepto los nombres reservados a continuación. La ruta del archivo menos la extensión es la URL; consulte [enrutamiento](../routing/README.md).

| Archivo | Rol |
|---|---|
| `layout.nexy` | envuelve las páginas hermanas y secundarias |
| `errors.nexy` | 500 páginas para el directorio |
| `notfound.nexy` | 404 página para el directorio |
| `dependencies.py` | dependencias compartidas FastAPI para el directorio |
| `__init__.py` | Python marcador de paquete |
| `loading.nexy` | reservado: excluido de las rutas, pero aún no tiene efecto de tiempo de ejecución |

El nombre de cada página también existe por marco. Con `react()` configurado, `layout.jsx` y `layout.tsx` se reservan exactamente como `layout.nexy`. Las listas están construidas en `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` y `errors.nexy` solo se instalan cuando existe una copia en la raíz de las rutas. Luego, una copia en un subdirectorio refina la página para ese prefijo.

## `src/apps/`

El directorio `nexy new` se utiliza para el enrutador modular: los controladores, módulos y proveedores registran sus rutas a través de decoradores desde `nexy.decorators`, luego el agregado `APIRouter` se monta con `useRouter` en `nexyconfig.py`.

Un proyecto puede tener ambos enrutadores: `useRouter` monta el enrutador modular y `src/routes/` se escanea siempre que exista ese directorio. Consulte [enrutamiento modular](../routing/modular/README.md).

## `public/`

Los archivos aquí se sirven desde la raíz del sitio: `/favicon.ico`, `/robots.txt`, imágenes, fuentes.

## `__nexy__/`

Generado por `nx build` (y por `nx dev` para las piezas que necesita). Contiene:

- los módulos de ruta compilados, como un paquete Python (`__nexy__/src/routes/...`);
- los puntos de entrada del cliente generados (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` después de una compilación Vite - activos, manifiesto, HTML prerenderizado;
- `build-cache.json`.

Trate todo el directorio como desechable: elimínelo, reconstrúyalo. Al editarlo a mano, se pierde el cambio en la siguiente compilación. Agréguelo a `.gitignore`.

## Próximos pasos

- [Enrutamiento](../routing/README.md): cómo una ruta se convierte en una URL
- [Config](../reference/config.md): cada opción del proyecto
- [Frontend](../guides/frontend.md): Vite, estilo y compilación del cliente
