# Nexy et NestJS

Le routeur modulaire s'inspire de NestJS : contrôleurs, modules et injection de constructeur. C'est un
couche mince sur FastAPI, il n'essaie donc pas de reproduire l'intégralité de NestJS. Cette page répertorie les deux côtés.

## Qu'est-ce qui correspond

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` avec les mêmes quatre attributs de classe |
| `@Injectable()` | `@Injectable()` |
| Injection de constructeur | `__init__` paramètres résolus à partir des annotations de type |
| Portées singleton, requêtes et transitoires | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (une dépendance FastAPI) |
| `@ApiOperation`, `@ApiResponse` (Swagger) | `@UseRoute`, `@UseResponse` (OpenAPI, servi à `/docs`) |
| Passerelles WebSocket | `async def SOCKET(...)` sur un contrôleur |
| Validation DTO (`class-validator`) | Modèles Pydantic, natifs de FastAPI |
| Détection de dépendance circulaire | `RecursionError` nommer la classe |

## Ce qui diffère

- Les gestionnaires sont des méthodes nommées d'après le verbe HTTP (`get`, `post`...), une par contrôleur.
- Les gardes et les décorateurs de middleware sont des FastAPI `Depends`, pas des classes avec `canActivate`.
- Les paramètres (`@Body`, `@Param`, `@Query`) sont des paramètres FastAPI : annotations de type, `Query`, `Path`,
  `Body`.
- Les tuyaux sont des dépendances de validation Pydantic et FastAPI.

## Ce qui manque

| Fonctionnalité NestJS | Statut dans Nexy |
|---|---|
| Fournisseurs personnalisés (`useValue`, `useFactory`, `useClass`, jetons de chaîne) | non disponibles : uniquement les `@Injectable()` classes |
| Injection par interface ou classe abstraite | non disponible |
| Encapsulation du module | non appliquée : le conteneur est à l'échelle du processus, `exports` contrôle uniquement la résolution rapide |
| Modules dynamiques et globaux (`forRoot`, `@Global`) | non disponibles |
| Hooks de cycle de vie (`onModuleInit`, `onApplicationShutdown`) | non disponibles |
| Les intercepteurs | utilisent un middleware ASGI (`useMiddlewares`) ou des dépendances |
| Les filtres d'exceptions | utilisent les gestionnaires d'exceptions FastAPI |
| Module de test avec remplacements de fournisseur | pas d'API publique ; utilisez FastAPI `dependency_overrides` et `TestClient` |
| Module de configuration, planification, files d'attente, CQRS, microservices, mise en cache | ne fait pas partie de Nexy ; utiliser l'écosystème Python |

## Quand le cueillir

Choisissez le routeur modulaire lorsque vous souhaitez une structure basée sur les classes avec injection pour une API plus grande.
Choisissez le routeur basé sur des fichiers lorsque la structure de l'URL est le principe d'organisation. Les deux sont échafaudés
par `nx new`, s'exécutent sur la même application FastAPI et peuvent coexister.

> [!REMARQUE]
> les éléments manquants ci-dessus constituent l'écart honnête. Si vous avez besoin de `useFactory` fournisseurs
> ou les fournisseurs remplaçables dans les tests d'aujourd'hui, conservez la logique dans les fonctions simples et FastAPI
> `Depends`, qui composent et remplacent naturellement.

## Étapes suivantes

- [Injection de dépendances](dependency-injection.md)
- [Gardes et métadonnées](guards-and-metadata.md)
- [Tests](../../guides/testing.md)