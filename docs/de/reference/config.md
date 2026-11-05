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
| `useSslKeyfile`, `useSslCertfile` | `None` | stellen HTTPS direkt bereit |
| `useDevTools` | `True` | Die Symbolleiste `nexy dev` fügt zu jeder Seite hinzu (Seiteninformationen, Routen, Fehler, Konfiguration); `False` entfernt es. Niemals in der Produktion vorhanden |
| `useWorkers` | `0` | Prozesse `nx start` Läufe; `0` ist eine pro CPU unter Linux und macOS, eine unter Windows |
| `useCSR` | `False` | Client-seitiger Routing-Modus; `.nexy` Routen sind deaktiviert |

## Routen

| Feld | Standard | Bedeutung |
|---|---|---|
| `useRouter` | `None` | eine `APIRouter` Instanz oder Klasse, die neben den dateibasierten Routen gemountet ist; `None` bedeutet nur dateibasiert |
| `excludeDirs` | `["templates", "extension", "docs"]` | Verzeichnisse werden beim Scannen von Routen übersprungen |
| `useAliases` | `None` | Aliase importieren, z.B. `{"@": "src"}` (`@/components/Counter.tsx` bedeutet `src/components/Counter.tsx`); `nx new` schreibt das, was Sie ausgewählt haben, und Vite und `tsconfig.json` folgen ihm |

## Frontend

| Feld | Standard | Bedeutung |
|---|---|---|
| `useFF` | `None` | Client-Framework-Fabrik: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | Erstellen und Bereitstellen von Client-Bundles mit Vite |
| `useMarkdownExtensions` | `[]` | Zusätzliche Erweiterungen für das Rendern von `.md`/`.mdx` |
| `useWatchExtensions` | `None` | Zusätzliche Erweiterungen, die der Entwicklungsserver überwacht |
| `useWatchExcludePatterns` | `None` | Glob-Muster, die der Entwicklungsserver ignoriert |

> **Gut zu wissen**: `NexyConfigModel` erklärt `useVite = False`; Der Standardwert für die Laufzeit `Config` ist `True`.

## Reservierte Dateinamen

Jedes Feld fügt einer reservierten Rolle Erweiterungen hinzu. `useLayoutExtensions = ["md"]` macht `layout.md` reserviert, genau wie `layout.nexy`.

| Feld | Fügt Erweiterungen zu | hinzu
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
| `useDocs` | `True` | dienen dem OpenAPI-Schema und seiner Skalar-Referenzseite |
| `useDocsUrl` | `"/docs"` | Pfad der API-Referenzseite |
| `useRedocsUrl` | `"/redocs"` | deklariert, aber keine Route ist gemountet |
| `useTitle` | `"Nexy App"` | OpenAPI Titel und Seitentitel (`"Nexy"` in `NexyConfigModel`) |

## Middleware

| Feld | Standard | Bedeutung |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI-Middleware-Klassen |
| `useCORS` | `None` | Kwargs für `CORSMiddleware` |
| `useGZip` | `None` | Kwargs für `GZipMiddleware` |
| `useTrustedHost` | `None` | Kwargs für `TrustedHostMiddleware` |
| `useSession` | `None` | Kwargs für `SessionMiddleware` |
| `useAuth` | `None` | Authentifizierungs-Middleware-Konfiguration |
| `useHTTPSRedirect` | `False` | HTTP zu HTTPS umleiten |

## Markdown

| Feld | Standard | Bedeutung |
|---|---|---|
| `useTocDepth` | `"2-6"` | Überschriftenebenen im Inhaltsverzeichnis |
| `useTocTitle` | `"Table of Contents"` | Inhaltsverzeichnis-Titel |
| `useTocAuto` | `True` | generiert das Inhaltsverzeichnis für Markdown Seiten |

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
- [Bereitstellen](../deployment/README.md): Produktionsoptionen
