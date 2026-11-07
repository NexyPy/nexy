# Projektstruktur

Jede Datei in einem Nexy-Projekt hat eine Aufgabe, und wohin sie geht, hängt vom Router ab: `src/routes/` für dateibasiertes Routing, `src/apps/` für den modularen Router.

## Top-Niveau

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Um einen Ordner auszuwählen, fragen Sie nach der Datei:

- **Etwas, das der Browser öffnen kann** – eine Route: `src/routes/`.
- **Ein Stück, das von mehreren Routen** verwendet wird – eine Komponente oder ein Modul: `src/components/`, `src/`.
- **Eine Datei wurde so bereitgestellt, wie sie ist** - `public/`.
- **Generiert** - `__nexy__/`; Bearbeiten Sie es niemals.

> [!WARNING]
> `src/routes/` wird gescannt: Ein dort platzierter Helfer wird zur Route. Platzieren Sie einen Helfer, der keine Route ist, außerhalb von `src/routes/` oder beginnen Sie seinen Namen mit `_`.
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Um einen Ordner auszuwählen, fragen Sie nach der Datei:

- **Eine URL** – eine Methode eines Controllers in `src/apps/`, registriert von seinem Modul.
- **Eine Seite** – eine `.nexy`-Ansicht neben ihrem Controller, zurückgegeben mit `useViews`.
- **Ein von mehreren Ansichten verwendetes Stück** - `src/components/`.
- **Eine Datei wurde so bereitgestellt, wie sie ist** - `public/`.
- **Erzeugt** - `__nexy__/`; Bearbeiten Sie es niemals.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Um einen Ordner auszuwählen, fragen Sie nach der Datei:

- **Eine Route der mitgelieferten App** – wo sie bereits ist, hier `src/legacy/`.
- **Eine neue Seite oder Route** - `src/routes/`, neben dem enthaltenen Router.
- **Eine Datei wurde so bereitgestellt, wie sie ist** - `public/`.
- **Erzeugt** - `__nexy__/`; Bearbeiten Sie es niemals.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

Jede Datei wird zu einer Route, mit Ausnahme der unten aufgeführten reservierten Namen. Der Dateipfad abzüglich der Erweiterung ist die URL – siehe [dateibasiertes Routing](../routing/fbr/README.md).

| Datei | Rolle |
|---|---|
| `layout.nexy` | Umschließt Geschwister- und Kinderseiten |
| `errors.nexy` | 500 Seiten für das Verzeichnis |
| `notfound.nexy` | 404-Seite für das Verzeichnis |
| `dependencies.py` | freigegebene FastAPI Abhängigkeiten für das Verzeichnis |
| `__init__.py` | Python Paketmarkierung |
| `loading.nexy` | reserviert – von Routen ausgeschlossen, hat aber noch keinen Laufzeiteffekt |

Jeder Seitenname existiert auch pro Framework. Wenn `react()` konfiguriert ist, werden `layout.jsx` und `layout.tsx` genau wie `layout.nexy` reserviert. Die Listen sind in `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`) erstellt.

> [!NOTE]
> `notfound.nexy` und `errors.nexy` werden nur installiert, wenn eine Kopie im Routenstamm vorhanden ist. Eine Kopie in ein Unterverzeichnis verfeinert dann die Seite für dieses Präfix.
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

Ein Controller antwortet auf URLs, ein Modul gruppiert Controller und Anbieter und das Root-Modul wird mit `useRouter` in `nexyconfig.py` gemountet:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

Keine Datei in `src/apps/` ist eine Route anhand ihres Namens: Nur die Controller, die ein Modul auflistet, antworten. Siehe [modulares Routing](../routing/modular/README.md).
<!-- /router -->

## `public/`

Hier werden Dateien aus dem Stammverzeichnis der Website bereitgestellt: `/favicon.ico`, `/robots.txt`, Bilder, Schriftarten.

## `__nexy__/`

Erstellt von `nx build` (und von `nx dev` für die benötigten Teile). Es enthält:

- die kompilierten `.nexy`-Dateien als Python-Paket (`__nexy__/src/...`);
- die generierten Client-Einstiegspunkte (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` nach einem Vite Build – Assets, Manifest, vorgerendertes HTML;
- `build-cache.json`.

Behandeln Sie das gesamte Verzeichnis als Wegwerfverzeichnis: Löschen Sie es und erstellen Sie es neu. Wenn Sie es manuell bearbeiten, gehen die Änderungen beim nächsten Build verloren. Fügen Sie es zu `.gitignore` hinzu.

## Nächste Schritte

<!-- router:fbr -->
- [Dateibasiertes Routing](../routing/fbr/README.md): Wie aus einem Pfad eine URL wird
<!-- /router -->
<!-- router:modular -->
- [Modulares Routing](../routing/modular/README.md): Controller, Module und Anbieter
<!-- /router -->
<!-- router:custom -->
- [Benutzerdefiniertes Routing](../routing/custom/README.md): Einbinden eines vorhandenen FastAPI Routers
<!-- /router -->
- [Konfiguration](../reference/config.md): jede Projektoption
- [Frontend](../guides/frontend.md): Vite, Styling und der Client-Build
