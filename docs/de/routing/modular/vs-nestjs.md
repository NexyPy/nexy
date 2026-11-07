# Nexy und NestJS

Der modulare Router ist inspiriert von NestJS: Controller, Module und Konstruktorinjektion. Es handelt sich um eine dünne Schicht über FastAPI, daher wird nicht versucht, alles von NestJS zu reproduzieren. Diese Seite listet beide Seiten auf.

## Was passt

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller("/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` mit den gleichen vier Klassenattributen |
| `@Injectable()` | `@Injectable()` |
| Konstruktorinjektion | `__init__` Parameter aus Typanmerkungen aufgelöst |
| Singleton-, Anforderungs- und transiente Bereiche | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (eine FastAPI-Abhängigkeit) |
| `@ApiOperation`, `@ApiResponse` (Prahlerei) | `@UseRoute`, `@UseResponse` (OpenAPI, serviert am `/docs`) |
| WebSocket Gateways | `async def SOCKET(...)` auf einem Controller |
| DTO-Validierung (`class-validator`) | Pydantic Modelle, ursprünglich aus FastAPI |
| Erkennung zirkulärer Abhängigkeiten | `RecursionError` Benennung der Klasse |

Derselbe Controller und sein injizierter Dienst, NestJS zuerst:

```ts filename="user.controller.ts"
@Injectable()
export class UsersService {
  findAll() {
    return [{ id: 1, name: "Ada" }];
  }
}

@Controller("users")
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  findAll() {
    return this.users.findAll();
  }
}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller, Injectable


@Injectable()
class UserService:
    def find_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]


@Controller("/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## Was ist anders

- Handler sind Methoden, die nach dem HTTP-Verb (`get`, `post`... benannt sind, eine pro Controller.
- Guards und Middleware-Dekoratoren sind FastAPI `Depends`, keine Klassen mit `canActivate`.
- Parameter (`@Body`, `@Param`, `@Query`) sind FastAPI Parameter: Typanmerkungen, `Query`, `Path`, `Body`.
- Pipes sind Pydantic Validierungen und FastAPI Abhängigkeiten.

`@Query()`, ein DTO und eine Guard-Klasse werden zu einer Annotation, einem Pydantic Modell und einer Funktion:

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## Was fehlt

| NestJS-Funktion | Status in Nexy |
|---|---|
| Benutzerdefinierte Anbieter (`useValue`, `useFactory`, `useClass`, String-Tokens) | nicht verfügbar: nur `@Injectable()` Klassen |
| Injektion über eine Schnittstelle oder eine abstrakte Klasse | nicht verfügbar |
| Modulkapselung | nicht erzwungen: Der Container ist prozessweit, `exports` steuert nur die Eager-Auflösung |
| Dynamische und globale Module (`forRoot`, `@Global`) | nicht verfügbar |
| Lebenszyklus-Hooks (`onModuleInit`, `onApplicationShutdown`) | nicht verfügbar |
| Abfangjäger | Verwenden Sie ASGI-Middleware (`useMiddlewares`) oder Abhängigkeiten |
| Ausnahmefilter | Verwenden Sie FastAPI Ausnahmehandler |
| Testmodul mit Anbieterüberschreibungen | keine öffentliche API; Verwenden Sie FastAPI `dependency_overrides` und `TestClient` |
| Konfigurationsmodul, Planung, Warteschlangen, CQRS, Microservices, Caching | nicht Teil von Nexy; Nutzen Sie das Python Ökosystem |

Anstelle eines `useFactory`-Anbieters eine einfache Funktion hinter `Depends`, die ein Test mit `dependency_overrides` überschreibt:

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller("/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## Wann soll man es auswählen?

Wählen Sie den modularen Router, wenn Sie eine klassenbasierte Struktur mit Injektion für eine größere API wünschen. Wählen Sie den dateibasierten Router, wenn die URL-Struktur das Organisationsprinzip ist. Beide basieren auf `nx new`, laufen auf derselben FastAPI Anwendung und können koexistieren.

> [!NOTE]
> Die fehlenden Elemente oben sind die ehrliche Lücke. Wenn Sie heute in Tests `useFactory` Anbieter oder überschreibbare Anbieter benötigen, behalten Sie die Logik in einfachen Funktionen und FastAPI `Depends` bei, die auf natürliche Weise zusammengesetzt und überschrieben werden.

## Nächste Schritte

- [Abhängigkeitsinjektion](dependency-injection.md)
- [Guards und Metadaten](guards-and-metadata.md)
- [Testen](../../guides/testing.md)
