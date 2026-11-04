# Modulares Routing

Modulares Routing verwendet Klassen mit Dekoratoren anstelle von Dateien unter `src/routes/`: Controllern
Anfragen werden verarbeitet, Module gruppieren sie und Anbieter werden eingefügt. Montieren Sie das resultierende `APIRouter`
mit `useRouter` in `nexyconfig.py`.

**Bevor Sie beginnen:** ein Nexy-Projekt und eine Arbeitsseite. Der modulare Router ersetzt den
Wenn Sie sich noch nicht für einen Router entschieden haben, lesen Sie bitte zuerst [Routing](../README.md)].

| Seite | Was es abdeckt |
|---|---|
| Diese Seite | Ein Modul montieren, einen Controller schreiben, Controller gruppieren |
| [Abhängigkeitsinjektion](dependency-injection.md) | `@Injectable`, Bereiche, der Container |
| [Schutz und Metadaten](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [Nexy und NestJS](vs-nestjs.md) | Was zu NestJS passt und was nicht |

## Richten Sie den Router ein

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> dateibasiertes Routing funktioniert weiterhin. Wenn `src/routes/` vorhanden ist, wird es sogar gescannt
> wenn `useRouter` eingestellt ist.

## Schreiben Sie einen Controller

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Methoden werden nach Namen ohne Berücksichtigung der Groß- und Kleinschreibung abgeglichen: `get`, `post`, `put`, `patch`, `delete`, `options`,
`head`, `trace`.

Ein Controller deklariert einen Handler pro HTTP-Methode; Beim Start wird ein Duplikat ausgelöst. Fügen Sie ein Präfix mit hinzu
`@Controller(prefix="/users")` – jeder Handler ist auf `prefix/` gemountet. `async def SOCKET(...)` auf a
Der Controller registriert einen WebSocket unter demselben Pfad.

## Gruppieren Sie Controller in einem Modul

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` gibt ein `APIRouter` zurück. `controllers` ist erforderlich; `providers`, `imports`
und `exports` sind optional. Importierte Module werden als Sub-Router gemountet und ihre exportierten Provider
werden beim Start behoben.

## Ansichten von einem Controller

Ein Controller kann eine Seite zurückgeben. `useViews` rendert eine `.nexy`-Ansicht; Legen Sie sie ineinander, um sie einzuwickeln
in einem Layout:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

Siehe [Layouts](../fbr/layouts/README.md).

## Beispiel

Siehe `examples/Modular/api/minimal/`.

## Nächste Schritte

- [Abhängigkeitsinjektion](dependency-injection.md): Dienste und Bereiche
- [Schutz und Metadaten](guards-and-metadata.md): Routen schützen und dokumentieren
- [Routing](../README.md): der dateibasierte Router
- [Config](../../reference/config.md): jede Option, einschließlich `useRouter`