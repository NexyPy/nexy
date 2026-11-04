# Ganchos

Los ganchos leen la solicitud HTTP actual desde dentro de una página `.nexy`, un controlador API o un módulo
controlador. Sus nombres coinciden con los ganchos del enrutador del cliente (`@nexy/client`) donde hacen lo mismo
cosa.

> [!NOTA]
> los ganchos solo funcionan mientras se maneja una solicitud. Llamar a uno a cualquier otro lugar
> sube `RuntimeError`.

## Los ganchos

| Gancho | Devuelve |
|---|---|
| `usePathname()` | ruta de solicitud, p. `"/blog/post-1"` |
| `useSearchParams()` | cadena de consulta como `dict[str, str]`, primer valor por clave |
| `useParams()` | parámetros de ruta dinámica, p.e. `{"slug": "post-1"}` |
| `useQuery()` | el nombre original de `useParams()`, conservado para las páginas existentes |
| `useRequest()` | la petición de Starlette, por lo que los demás ganchos no cubren |
| `useHeaders()` | los encabezados de solicitud como `dict[str, str]`, nombres en minúsculas |
| `useUrl()` | la URL completa: `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | si `href` es la página actual o una de sus padres |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | todas las cookies como `dict[str, str]` |
| `useSession()` | el dictado de la sesión, `{}` cuando las sesiones no están habilitadas |
| `useToc(depth_range="2-6")` | tabla de contenidos HTML de la página actual, `""` cuando ninguna |
| `useViews(path, context=None)` | renderiza otra vista y devuelve un `HTMLResponse` |

## Leer la solicitud

```nexy filename="src/rutas/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## Un enlace activo en una barra de navegación

`useIsActive` sigue la misma regla que en el cliente: la cadena de consulta, el fragmento y un final
se ignoran las barras diagonales, un enlace a un padre está activo en sus hijos a menos que se establezca `exact` y `/`
sólo activo en `/`.

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## Notas

- `useQuery()` devuelve los parámetros **ruta**, no la cadena de consulta, razón por la cual `useParams()`
  existe. La cadena de consulta es `useSearchParams()`.
- `useRouter()` aquí está el enlace de solicitud. No es el campo de configuración `useRouter` el que monta un
  `APIRouter`.
- `useSession()` necesita `useSession = {...}` en `nexyconfig.py`; sin él, el dictado está vacío.
- `useViews("about.tsx", {"title": "About"})` devuelve HTML: una vista `.nexy` se representa por su
  módulo compilado, una vista `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` se convierte en un contenedor de montaje del cliente.

## Próximos pasos

- [Pages](../pages/README.md): segmentos y diseños dinámicos
- [Recetas](../../../guides/recipes.md): un flujo de inicio de sesión probado construido sobre `useSession()`
- [Config](../../../reference/config.md): habilita sesiones y configuraciones regionales
- [archivos .nexy](../../../views/nexy/README.md): donde normalmente se llaman los ganchos