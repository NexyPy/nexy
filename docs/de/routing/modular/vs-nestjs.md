# Nexy und NestJS

Der modulare Router ist inspiriert von NestJS: Controller, Module und Konstruktorinjektion. Es handelt sich um eine dünne Schicht über FastAPI, daher wird nicht versucht, alles von NestJS zu reproduzieren. Diese Seite listet beide Seiten auf.

## Was passt

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` mit den gleichen vier Klassenattributen |
| `@Injectable()` | `@Injectable()` |
| Konstruktorinjektion | `__init__` Parameter aufgelöst aus Typanmerkungen |
| Singleton-, Anforderungs- und transiente Bereiche | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (eine FastAPI Abhängigkeit) |
| `@ApiOperation`, `@ApiResponse` (Swagger) | `@UseRoute`, `@UseResponse` (OpenAPI, serviert bei `/docs`) |
| WebSocket Gateways | `async def SOCKET(...)` auf einem Controller |
| DTO-Validierung (`class-validator`) | Pydantic Modelle, nativ für FastAPI |
| Erkennung zirkulärer Abhängigkeiten | `RecursionError` Benennung der Klasse |

## Was ist anders

- Handler sind Methoden, die nach dem HTTP-Verb (`get`, `post`... benannt sind, eine pro Controller.
- Guards und Middleware-Dekoratoren sind FastAPI `Depends`, keine Klassen mit `canActivate`.
- Parameter (`@Body`, `@Param`, `@Query`) sind FastAPI Parameter: Typanmerkungen, `Query`, `Path`, `Body`.
- Pipes sind Pydantic Validierungen und FastAPI Abhängigkeiten.

## Was fehlt

| NestJS Funktion | Status in Nexy |
|---|---|
| Benutzerdefinierte Anbieter (`useValue`, `useFactory`, `useClass`, String-Tokens) | nicht verfügbar: nur `@Injectable()` Klassen |
| Injektion über Schnittstelle oder abstrakte Klasse | nicht verfügbar |
| Modulkapselung | nicht erzwungen: Der Container ist prozessweit, `exports` steuert nur die Eager-Auflösung |
| Dynamische und globale Module (`forRoot`, `@Global`) | nicht verfügbar |
| Lebenszyklus-Hooks (`onModuleInit`, `onApplicationShutdown`) | nicht verfügbar |
| Interceptoren | verwenden ASGI-Middleware (`useMiddlewares`) oder Abhängigkeiten |
| Ausnahmefilter | verwenden FastAPI Ausnahmehandler |
| Testmodul mit Anbieter überschreibt | keine öffentliche API; Verwenden Sie FastAPI `dependency_overrides` und `TestClient` |
| Konfigurationsmodul, Planung, Warteschlangen, CQRS, Microservices, Caching | nicht Teil von Nexy; das Python Ökosystem nutzen |

## Wann soll man es auswählen?

Wählen Sie den modularen Router, wenn Sie eine klassenbasierte Struktur mit Injektion für eine größere API wünschen. Wählen Sie den dateibasierten Router, wenn die URL-Struktur das Organisationsprinzip ist. Beide basieren auf `nx new`, laufen auf derselben FastAPI-Anwendung und können koexistieren.

> [!NOTE]
> Die fehlenden Elemente oben sind die ehrliche Lücke. Wenn Sie heute in Tests `useFactory` Anbieter oder überschreibbare Anbieter benötigen, behalten Sie die Logik in einfachen Funktionen und FastAPI `Depends` bei, die auf natürliche Weise zusammengesetzt und überschrieben werden.

## Nächste Schritte

- [Abhängigkeitsinjektion](dependency-injection.md)
- [Schutzmaßnahmen und Metadaten](guards-and-metadata.md)
- [Testen](../../guides/testing.md)
