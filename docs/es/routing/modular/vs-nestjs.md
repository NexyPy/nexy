# Nexy y NestJS

El enrutador modular está inspirado en NestJS: controladores, módulos e inyección de constructor. es un
capa delgada sobre FastAPI, por lo que no intenta reproducir todo NestJS. Esta página enumera ambos lados.

## ¿Qué coincide?

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` con los mismos cuatro atributos de clase |
| `@Injectable()` | `@Injectable()` |
| Inyección de constructor | `__init__` parámetros resueltos a partir de anotaciones de tipo |
| Ámbitos singleton, de solicitud y transitorios | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (una dependencia FastAPI) |
| `@ApiOperation`, `@ApiResponse` (Swagger) | `@UseRoute`, `@UseResponse` (OpenAPI, servido en `/docs`) |
| Puertas de enlace WebSocket | `async def SOCKET(...)` en un controlador |
| Validación DTO (`class-validator`) | Modelos Pydantic, nativos de FastAPI |
| Detección de dependencia circular | `RecursionError` nombrando la clase |

## ¿Qué difiere?

- Los controladores son métodos que llevan el nombre del verbo HTTP (`get`, `post`...), uno por controlador.
- Los guardias y decoradores de middleware son FastAPI `Depends`, no clases con `canActivate`.
- Los parámetros (`@Body`, `@Param`, `@Query`) son parámetros FastAPI: anotaciones de tipo, `Query`, `Path`,
  `Body`.
- Las canalizaciones son validación de Pydantic y dependencias de FastAPI.

## Lo que falta

| Función NestJS | Estado en Nexy |
|---|---|
| Proveedores personalizados (`useValue`, `useFactory`, `useClass`, tokens de cadena) | no disponibles: solo `@Injectable()` clases |
| Inyectar por interfaz o clase abstracta | no disponible |
| Encapsulación del módulo | no se aplica: el contenedor abarca todo el proceso, `exports` solo controla la resolución ansiosa |
| Módulos dinámicos y globales (`forRoot`, `@Global`) | no disponibles |
| Ganchos de ciclo de vida (`onModuleInit`, `onApplicationShutdown`) | no disponibles |
| Los interceptores | utilizan middleware ASGI (`useMiddlewares`) o dependencias |
| Los filtros de excepción | usan controladores de excepciones FastAPI |
| Módulo de prueba con anulaciones del proveedor | sin API pública; utilizar FastAPI `dependency_overrides` y `TestClient` |
| Módulo de configuración, programación, colas, CQRS, microservicios, almacenamiento en caché | no forma parte de Nexy; utilizar el ecosistema Python |

## Cuándo elegirlo

Elija el enrutador modular cuando desee una estructura basada en clases con inyección para una API más grande.
Elija el enrutador basado en archivos cuando la estructura de URL sea el principio organizador. Ambos están andamiados
por `nx new`, se ejecuta en la misma aplicación FastAPI y puede coexistir.

> [!NOTA]
> los elementos que faltan arriba son la brecha honesta. Si necesitas `useFactory` proveedores
> o proveedores reemplazables en las pruebas actuales, mantenga la lógica en funciones simples y FastAPI
> `Depends`, que componen y anulan de forma natural.

## Próximos pasos

- [Inyección de dependencia](dependency-injection.md)
- [Guardias y metadatos](guards-and-metadata.md)
- [Pruebas](../../guides/testing.md)