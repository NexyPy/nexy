# Nexy y NestJS

El enrutador modular está inspirado en NestJS: controladores, módulos e inyección de constructor. Es una capa delgada sobre FastAPI, por lo que no intenta reproducir todo NestJS. Esta página enumera ambos lados.

## que coincide

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` con los mismos cuatro atributos de clase |
| `@Injectable()` | `@Injectable()` |
| Parámetros de inyección de constructor | `__init__` resueltos a partir de anotaciones de tipo |
| Ámbitos singleton, de solicitud y transitorios | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (una FastAPI dependencia) |
| `@ApiOperation`, `@ApiResponse` (Swagger) | `@UseRoute`, `@UseResponse` (OpenAPI, servido en `/docs`) |
| WebSocket puertas de enlace | `async def SOCKET(...)` en un controlador |
| Validación DTO (`class-validator`) | Pydantic modelos, nativos de FastAPI |
| Detección de dependencia circular | `RecursionError` nombrando la clase |

## que difiere

- Los controladores son métodos que llevan el nombre del verbo HTTP (`get`, `post`...), uno por controlador.
- Los guardias y decoradores de middleware son FastAPI `Depends`, no clases con `canActivate`.
- Los parámetros (`@Body`, `@Param`, `@Query`) son parámetros FastAPI: anotaciones de tipo, `Query`, `Path`, `Body`.
- Las canalizaciones son Pydantic validación y FastAPI dependencias.

## lo que falta

| NestJS característica | Estado en Nexy |
|---|---|
| Proveedores personalizados (`useValue`, `useFactory`, `useClass`, tokens de cadena) | no disponibles: solo `@Injectable()` clases |
| Inyectar por interfaz o clase abstracta | no disponible |
| Encapsulación del módulo | no se aplica: el contenedor abarca todo el proceso, `exports` solo controla la resolución ansiosa |
| Módulos dinámicos y globales (`forRoot`, `@Global`) | no disponibles |
| Ganchos de ciclo de vida (`onModuleInit`, `onApplicationShutdown`) | no disponibles |
| Los interceptores | utilizan middleware ASGI (`useMiddlewares`) o dependencias |
| Los filtros de excepción | utilizan FastAPI controladores de excepciones |
| Módulo de prueba con anulaciones de proveedor | sin API pública; utilice FastAPI `dependency_overrides` y `TestClient` |
| Módulo de configuración, programación, colas, CQRS, microservicios, almacenamiento en caché | no forma parte de Nexy; utilizar el ecosistema Python |

## Cuando escogerlo

Elija el enrutador modular cuando desee una estructura basada en clases con inyección para una API más grande. Elija el enrutador basado en archivos cuando la estructura de URL sea el principio organizador. Ambos están estructurados por `nx new`, se ejecutan en la misma FastAPI aplicación y pueden coexistir.

> [!NOTA]
> Los elementos que faltan arriba son la brecha honesta. Si necesita proveedores `useFactory` o proveedores reemplazables en las pruebas actuales, mantenga la lógica en funciones simples y FastAPI `Depends`, que se componen y anulan de forma natural.

## Próximos pasos

- [Inyección de dependencia](dependency-injection.md)
- [Guardias y metadatos](guards-and-metadata.md)
- [Pruebas](../../guides/testing.md)
