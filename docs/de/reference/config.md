# Konfig

Konfiguration ist eine Klasse in `nexyconfig.py` im Projektstamm. Nexy lädt es aus dem Verzeichnis, in dem es ausgeführt wird; Ein Projekt ohne die Datei verwendet die Standardeinstellungen.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## Server

| Feld | Standard | Bedeutung |
|---|---|---|
| `usePort` | `3000` | Port für `dev` und `start` |
| `useHost` | `"0.0.0.0"` | Bindungsadresse |
| `useSslKeyfile`, `useSslCertfile` | `None` | HTTPS direkt bereitstellen |
| `useDevTools` | `True` | die Symbolleiste `nexy dev` fügt zu jeder Seite hinzu (Seiteninformationen, Routen, Fehler, Konfiguration); `False` entfernt es. Niemals in der Produktion vorhanden |
| `useWorkers` | `0` | Prozesse `nx start` läuft; `0` ist einer pro CPU unter Linux und macOS, einer unter Windows |
| `useCSR` | `False` | Client-seitiger Routing-Modus; `.nexy` Routen sind deaktiviert |

## Routen

| Feld | Standard | Bedeutung |
|---|---|---|
| `useRouter` | `None` | eine `APIRouter`-Instanz oder -Klasse, die neben den dateibasierten Routen gemountet ist; `None` bedeutet nur dateibasiert |
| `excludeDirs` | `["templates", "extension", "docs"]` | Beim Scannen von Routen werden Verzeichnisse übersprungen |
| `useAliases` | `None` | Aliase importieren, z.B. `{"@": "src"}` (`@/components/Counter.tsx` bedeutet `src/components/Counter.tsx`); `nx new` schreibt die von Ihnen gewählte, und Vite und `tsconfig.json` folgen ihr |

## Frontend

| Feld | Standard | Bedeutung |
|---|---|---|
| `useFF` | `None` | Client-Framework-Fabrik: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | Erstellen und Bereitstellen von Client-Bundles mit Vite |
| `useMarkdownExtensions` | `[]` | Zusätzliche Erweiterungen für das Rendern von `.md`/`.mdx`. |
| `useWatchExtensions` | `None` | Zusätzliche Erweiterungen, die der Entwicklungsserver überwacht |
| `useWatchExcludePatterns` | `None` | Glob-Muster, die der Entwicklungsserver ignoriert |

> **Gut zu wissen**: `NexyConfigModel` erklärt `useVite = False`; Der Standardwert für die Laufzeit `Config` ist `True`.

## Reservierte Dateinamen

Jedes Feld fügt einer reservierten Rolle Erweiterungen hinzu. `useLayoutExtensions = ["md"]` macht `layout.md` reserviert, genau wie `layout.nexy`.

| Feld | Fügt Erweiterungen hinzu |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## API-Dokumentation

| Feld | Standard | Bedeutung |
|---|---|---|
| `useDocs` | `True` | Bereitstellung der Scalar-Referenzseite; `/openapi.json` wird in beide Richtungen serviert |
| `useDocsUrl` | `"/docs"` | Pfad der API-Referenzseite |
| `useRedocsUrl` | `"/redocs"` | deklariert, aber keine Route gemountet |
| `useTitle` | `"Nexy App"` | OpenAPI Titel und Seitentitel (`"Nexy"` in `NexyConfigModel`) |

### Kostenlos `/docs` für eine Seite des Projekts

Die API-Referenz antwortet `/docs` vor jeder Route, daher wird `src/routes/docs.nexy` oder `src/routes/docs/[[...slug]].nexy` dort nie bereitgestellt. `nx dev` und `nx start` benennen eine solche Seite beim Start. Verschieben Sie die Referenz mit `useDocsUrl`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

Oder schalten Sie es mit `useDocs = False` aus. `/openapi.json` bleibt in beiden Fällen erhalten: Halten Sie die Routen des Projekts von diesem Pfad fern.

## Middleware

| Feld | Standard | Bedeutung |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI-Middleware-Klassen |
| `useCORS` | `None` | Kwargs für `CORSMiddleware` |
| `useGZip` | `None` | Kwargs für `GZipMiddleware` |
| `useTrustedHost` | `None` | Kwargs für `TrustedHostMiddleware` |
| `useSession` | `None` | Kwargs für `SessionMiddleware` |
| `useAuth` | `None` | Authentifizierungs-Middleware-Konfiguration |
| `useHTTPSRedirect` | `False` | HTTP auf HTTPS umleiten |

## Markdown

| Feld | Standard | Bedeutung |
|---|---|---|
| `useTocDepth` | `"2-6"` | Überschriftenebenen im Inhaltsverzeichnis |
| `useTocTitle` | `"Table of Contents"` | Inhaltsverzeichnis-Titel |
| `useTocAuto` | `True` | Generieren Sie das Inhaltsverzeichnis für Markdown Seiten |

## Routen außerhalb des Dateibaums

Baue ein FastAPI `APIRouter` und montiere es mit `useRouter`. Es wird neben den dateibasierten Routen bereitgestellt:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Die oben genannten Standardwerte werden aus `nexy/core/config.py` gelesen.

## Deklariert, noch nicht gelesen

Diese Felder sind in `NexyConfigModel` vorhanden, aber kein Code nutzt sie. Das Festlegen hat keine Auswirkung:

`useViteDevUrl`, `useRTL`.

## Nächste Schritte

- [i18n](../guides/i18n.md): Internationalisierung
- [Frontend](../guides/frontend.md): `useFF` und der Client-Build
- [Deployment](../deployment/README.md): Produktionsoptionen
