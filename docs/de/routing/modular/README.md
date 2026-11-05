# Modulares Routing

Modulares Routing verwendet Klassen mit Dekoratoren anstelle von Dateien unter `src/routes/`: Controller verarbeiten Anfragen, Module gruppieren sie und Anbieter werden injiziert. Montieren Sie das resultierende `APIRouter` mit `useRouter` in `nexyconfig.py`.

**Bevor Sie beginnen:** ein Nexy-Projekt und eine Arbeitsseite. Der modulare Router ersetzt den dateibasierten Router. Lesen Sie daher zuerst [Routing](../README.md), wenn Sie sich noch nicht für einen Router entschieden haben.

| Seite | Was es abdeckt |
|---|---|
| Diese Seite | Ein Modul montieren, einen Controller schreiben, Controller gruppieren |
| [Abhängigkeitsinjektion](dependency-injection.md) | `@Injectable`, Bereiche, der Container |
| [Schutzvorrichtungen und Metadaten](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [Nexy und NestJS](vs-nestjs.md) | Was passt zu NestJS und was nicht zu |

## Richten Sie den Router ein

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> Das dateibasierte Routing funktioniert weiterhin. Wenn `src/routes/` vorhanden ist, wird es gescannt, auch wenn `useRouter` eingestellt ist.

## Schreiben Sie einen Controller

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Methoden werden nach Namen ohne Berücksichtigung der Groß- und Kleinschreibung abgeglichen: `get`, `post`, `put`, `patch`, `delete`, `options`, `head`, `trace`.

Ein Controller deklariert einen Handler pro HTTP-Methode; Beim Start wird ein Duplikat ausgelöst. Fügen Sie ein Präfix mit `@Controller(prefix="/users")` hinzu – jeder Handler wird auf `prefix/` gemountet. `async def SOCKET(...)` auf einem Controller registriert einen WebSocket auf demselben Pfad.

## Gruppieren Sie Controller in einem Modul

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` gibt ein `APIRouter` zurück. `controllers` ist erforderlich; `providers`, `imports` und `exports` sind optional. Importierte Module werden als Sub-Router gemountet und ihre exportierten Provider werden beim Start aufgelöst.

## Ansichten von einem Controller

Ein Controller kann eine Seite zurückgeben. `useViews` rendert eine `.nexy`-Ansicht; verschachteln Sie sie ineinander, um sie in ein Layout einzubinden:

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
- [Konfiguration](../../reference/config.md): jede Option, einschließlich `useRouter`
