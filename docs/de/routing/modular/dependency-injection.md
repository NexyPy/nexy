# Abhängigkeitsinjektion

Nexy löst Konstruktorabhängigkeiten für Controller und Dienste auf. Eine Klasse meldet sich mit `@Injectable()` an.

## Fügen Sie einen Dienst ein

```python filename="src/apps/users/user_service.py"
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from .user_service import UserService


@Controller(prefix="/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

Registrieren Sie den Controller in einem Modul. Durch das Auflisten des Dienstes in `providers` wird das Problem außerdem sofort beim Start behoben:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## So funktioniert die Auflösung

- Jeder `__init__`-Parameter wird aus seiner **Typanmerkung** aufgelöst. Die Annotation muss eine `@Injectable()`-Klasse sein oder der Parameter muss einen Standardwert haben; andernfalls erhöht sich die Auflösung `ValueError`.
- Controller werden beim Start mit `Container.resolve()` instanziiert.
- Ein Abhängigkeitszyklus löst `RecursionError` bei der Benennung der Klasse aus.
- Dienste können andere Dienste beliebig tief injizieren.

## Bereiche

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| Geltungsbereich | Lebensdauer |
|---|---|
| `Scope.SINGLETON` (Standard) | eine Instanz für den gesamten Prozess |
| `Scope.REQUEST` | eine Instanz pro Anforderungskontext |
| `Scope.TRANSIENT` | eine neue Instanz bei jeder Auflösung |

## Der Container

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

Wenn Sie selbst eine `@Injectable()`-Klasse erstellen, wird `TypeError` ausgelöst: Der Container besitzt seinen Lebenszyklus. Verwenden Sie `Container.resolve(...)` oder empfangen Sie die Klasse über einen anderen Konstruktor.

`Container.clear_request_scope()` löscht die Instanzen der aktuellen Anfrage.

## Routenparameter

FastAPI `Depends` funktioniert wie gewohnt für Handler-Parameter, neben der Konstruktor-Injektion:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## Grenzen

Der Container ist prozessweit. Anbieter sind nicht pro Modul isoliert, `exports` entscheidet nur, welche Anbieter ein importierendes Modul eifrig auflöst, und es gibt keine öffentliche API, um einen Anbieter in Tests auszutauschen. Den vollständigen Vergleich finden Sie unter [Nexy und NestJS](vs-nestjs.md).

## Nächste Schritte

- [Schutzmaßnahmen und Metadaten](guards-and-metadata.md)
- [Testen](../../guides/testing.md)
