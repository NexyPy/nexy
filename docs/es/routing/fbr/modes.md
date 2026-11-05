# Modo servidor y modo cliente

Un proyecto Nexy es **renderizado por el servidor** o **enrutado por el cliente**, como un proyecto Next.js son páginas renderizadas en el servidor o una aplicación cliente. `useCSR` en `nexyconfig.py` elige.

## Modo servidor (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- Las páginas son archivos `.nexy`, `.md` o `.mdx` en `src/routes/`.
- La raíz `layout.nexy` posee `<!DOCTYPE html>`, `<html>`, `<head>` y `<body>`.
- Los componentes del cliente (React, Vue, Svelte, Solid o Preact) se permiten como **islas**: importas una desde una página `.nexy` y se hidrata en el navegador. Ver [Islas](../../rendering/islands.md).
- Un componente de cliente nunca es una ruta. Guárdelos en `src/components/`.
- Un marco de cliente a la vez.

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## Modo cliente (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- Las páginas son los archivos de su marco de cliente: `.tsx` para React, `.vue`, `.svelte`.
- Los archivos `.md` y `.mdx` siguen siendo rutas válidas: Nexy los representa en el servidor dentro del diseño del cliente, y el enrutador del cliente se hace cargo de la navegación desde allí.
- El diseño raíz de cualquier marco (`layout.tsx`, `layout.vue`, `layout.svelte`) posee `<!DOCTYPE html>`, `<html>`, `<head>` y `<body>`, al igual que el diseño raíz del Next.js App Router. Nexy lo renderiza en Node para la primera respuesta y el marco hidrata todo el documento. Consulte [layout.tsx](../../views/react/differences.md).
- Los archivos `.py` son ​​controladores API servidos por FastAPI, junto a las rutas del cliente.
- No hay ningún archivo `.nexy` ni `layout.nexy`.
- La navegación entre páginas se produce en el navegador.

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## lo que se rechaza

Nexy revisa el proyecto antes de `nx dev`, `nx start` y `nx build` y se detiene con la lista de archivos:

| Modo | Rechazado | Mensaje |
|---|---|---|
| servidor | `.tsx`, `.jsx`, `.vue` o `.svelte` en `src/routes/` | mueva componentes a `src/components/`, o establezca `useCSR = True` |
| cliente | cualquier `.nexy` archivo en `src/routes/` | escríbalos como componentes del marco o establezca `useCSR = False` |
| ambos | más de un framework frontend en `useFF` | `useFF must configure exactly one frontend framework` |
| cliente | `useRouter` (enrutador modular) | `useCSR requires file-based routing` |
| cliente | no `useFF` | `useCSR requires a client framework` |

Esta verificación ignora los archivos y carpetas que comienzan con `_` o `.`.

## cual

- **Contenido, marketing, documentos, sitios SEO**: modo servidor con islas.
- **Paneles y aplicaciones con navegación de cliente enriquecida**: modo cliente.
- **Una API Python con una aplicación cliente en la parte superior**: modo cliente, con `.py` controladores al lado de las páginas.

## Próximos pasos

- [Diseños](layouts/README.md)
- [Representación](../../rendering/README.md)
- [Configuración](../../reference/config.md)
