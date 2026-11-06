# Dateikonventionen

Reservierte Namen und Regeln unter `src/routes/`.

## Dateien weiterleiten

| Datei | Wird |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | die Route seines Verzeichnisses |
| `about.nexy` | `/about` |
| `[slug].nexy` | dynamisches Segment `{slug}` |
| `[...path].nexy` | Alleskönner `{path:path}` |
| `(group)/page.nexy` | `/page`: Die Gruppe erscheint nicht in der URL |
| `name.py` | API-Handler; Funktionsnamen `GET`, `POST`, ... sind die Methoden |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | Client-Route, wenn das Framework mit `useFF` aktiviert ist |

```text
src/routes/
├─ index.nexy           /
├─ about.nexy           /about
├─ (marketing)/
│  └─ pricing.nexy      /pricing
├─ blog/
│  ├─ index.md          /blog
│  └─ [slug].nexy       /blog/{slug}
├─ docs/
│  └─ [...path].nexy    /docs/{path:path}
└─ api/
   └─ users.py          GET /api/users, POST /api/users
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

## Reservierte Dateien

| Datei | Rolle | Einzelheiten |
|---|---|---|
| `layout.nexy` | Servermodus: umschließt jede Seite darunter; Der Root besitzt das HTML-Dokument | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | Client-Modus (React): Der Root besitzt das HTML-Dokument, verschachtelte Seiten umschließen | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | Client-Modus: verschachtelte Layouts | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | 404-Seite für sein Verzeichnis | [Fehlerseiten](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 Seiten für sein Verzeichnis | [Fehlerseiten](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 403-Seite für sein Verzeichnis | [Fehlerseiten pro Ordner](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401-Seite für sein Verzeichnis | [Fehlerseiten pro Ordner](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | reserviert; Noch kein Laufzeiteffekt | [Fehlerseiten](../routing/fbr/errors/README.md) |
| `middleware.py` | ein `async def middleware(request, call_next)`, der die Anforderungen des Verzeichnisses und darunter umschließt | [Middleware-Dateien](../routing/fbr/middleware/README.md) |
| `dependencies.py` | eine `dependencies = [fn, ...]`-Liste, die auf das Verzeichnis und seine untergeordneten Verzeichnisse angewendet wird | [Abhängigkeiten](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python Paketmarkierung | |
| `favicon.ico` | serviert bei `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` und `useLoadingExtensions` reservieren weitere Erweiterungen für diese Namen. Siehe [Konfiguration](config.md).

Die beiden Python Dateien der Tabelle nebeneinander in einem Ordner:

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Und eine Seite, die den 404-Fehler ihres Ordners beantwortet:

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## Ignorierte Dateien

- Eine Datei oder ein Ordner, die mit `_` oder `.` beginnt: Verwenden Sie sie für Teiltexte, Entwürfe und Hilfsdateien.
- Eine Datei, deren Erweiterung für das Projekt nicht aktiv ist: Sie wird mit einer Warnung übersprungen.

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## Eine Datei pro URL

Zwei Dateien, die zur gleichen URL aufgelöst werden, werden beide registriert. Setzen Sie `blog.nexy` nicht neben `blog/index.nexy`.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## Draußen `src/routes/`

| Ordner | Zweck |
|---|---|
| `src/components/` | Von Seiten importierte Komponenten; niemals Routen |
| `src/apps/` | Controller und Module des [modularen Routers](../routing/modular/README.md) |
| `public/` | statische Dateien, bereitgestellt im Stammverzeichnis: `public/logo.svg` ist `/logo.svg` (auch unter `/public/`) |
| `__nexy__/` | generierte Ausgabe; nicht festlegen |

```text
my-app/
├─ nexyconfig.py
├─ public/
│  └─ logo.svg          /logo.svg
├─ src/
│  ├─ routes/           the routes
│  ├─ components/
│  │  └─ Counter.tsx    imported by pages, never served on its own
│  └─ apps/             the modular router, when you use it
└─ __nexy__/            generated: add it to .gitignore
```

## Nächste Schritte

- [Routing](../routing/README.md)
- [Projektstruktur](../getting-started/project-structure.md)
