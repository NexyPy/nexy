# Haken

Hooks lesen die aktuelle HTTP-Anfrage aus einer `.nexy`-Seite, einem API-Handler oder einem modularen Controller. Ihre Namen stimmen mit den Hooks des Client-Routers (`@nexy/client`) überein, wo sie dasselbe tun.

> [!NOTE]
> Hooks funktionieren nur, während eine Anfrage bearbeitet wird. Wenn man irgendwo anders anruft, wird `RuntimeError` ausgelöst.

## Die Haken

| Haken | Rückgaben |
|---|---|
| `usePathname()` | Anfragepfad, z.B. `"/blog/post-1"` |
| `useSearchParams()` | Abfragezeichenfolge als `dict[str, str]`, erster Wert pro Schlüssel |
| `useParams()` | dynamische Pfadparameter, z.B. `{"slug": "post-1"}` |
| `useQuery()` | der ursprüngliche Name von `useParams()`, der für vorhandene Seiten beibehalten wird |
| `useRequest()` | die Starlette-Anfrage, für das, was die anderen Hooks nicht abdecken |
| `useHeaders()` | die Anforderungsheader als `dict[str, str]`, Namen in Kleinbuchstaben |
| `useUrl()` | die vollständige URL: `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | ob `href` die aktuelle Seite oder eine ihrer Eltern ist |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | alle Cookies als `dict[str, str]` |
| `useSession()` | das Sitzungsdikt, `{}`, wenn Sitzungen nicht aktiviert sind |
| `useToc(depth_range="2-6")` | Inhaltsverzeichnis HTML für die aktuelle Seite, `""`, wenn keines vorhanden ist |
| `useViews(path, context=None)` | rendert eine andere Ansicht und gibt ein `HTMLResponse` zurück |

## Lesen Sie die Anfrage

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## Ein aktiver Link in einer Navigationsleiste

`useIsActive` folgt der gleichen Regel wie auf dem Client: Die Abfragezeichenfolge, das Fragment und ein abschließender Schrägstrich werden ignoriert, ein Link zu einem übergeordneten Element ist auf seinen untergeordneten Elementen aktiv, sofern nicht `exact` festgelegt ist, und `/` ist nur auf `/` aktiv.

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## Notizen

- `useQuery()` gibt die Parameter **Pfad** zurück, nicht die Abfragezeichenfolge, weshalb `useParams()` existiert. Die Abfragezeichenfolge ist `useSearchParams()`.
- `useRouter()` Hier ist der Anfrage-Hook. Es ist nicht das Konfigurationsfeld `useRouter`, das ein `APIRouter` bereitstellt.
- `useSession()` braucht `useSession = {...}` in `nexyconfig.py`; ohne es ist das Diktat leer.
- `useViews("about.tsx", {"title": "About"})` gibt HTML zurück: Eine `.nexy`-Ansicht wird von ihrem kompilierten Modul gerendert, eine `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx`-Ansicht wird zu einem Client-Mount-Container.

## Nächste Schritte

- [Seiten](../pages/README.md): dynamische Segmente und Layouts
- [Rezepte](../../../guides/recipes.md): ein getesteter Anmeldeablauf basierend auf `useSession()`
- [Konfiguration](../../../reference/config.md): Sitzungen und Gebietsschemas aktivieren
- [.nexy-Dateien](../../../views/nexy/README.md): Hier werden normalerweise Hooks aufgerufen
