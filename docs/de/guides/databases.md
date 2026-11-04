# Datenbanken

`nx new` kann eine Modellebene mit SQLModel, SQLAlchemy oder Tortoise-ORM aufbauen. Nexy wickelt nicht ein
das ORM: Sie verwenden es direkt, von Handlern und Seiten.

## Was das Gerüst hinzufügt

| Datei | Zweck |
|---|---|
| `src/configs/db.py` | die Engine (SQLModel, SQLAlchemy) oder die `TORTOISE_ORM` Einstellungen |
| `src/models/` | Modellklassen |
| `src/services/` | Funktionen, die die Modelle abfragen |
| `.env` | `DATABASE_URL`, geschrieben, wenn Sie während `nx new` | eine Datenbank-URL angeben

Die Verbindungszeichenfolge stammt aus der Umgebungsvariablen `DATABASE_URL`. Wenn es nicht eingestellt ist, wird die
Die Gerüst-Engine greift auf eine lokale SQLite-Datei zurück, `dev.db`.

## Verwenden Sie einen Dienst auf einer Seite

```nexy filename="src/routes/users/index.nexy"
---
from src.services.user_service import UserService
users = UserService.get_all()
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Verwenden Sie einen Dienst in einem API-Handler

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```

## Tortoise-ORM ist asynchron

Eine Seite läuft in der Ereignisschleife des Servers und kann nicht darauf warten, daher schlägt `asyncio.run(...)` dort fehl
„Kann nicht aus einer laufenden Ereignisschleife aufgerufen werden“. Das Gerüst `src/configs/db.py` gibt der Schildkröte ein
eigene Schleife in einem Thread und zwei Helfer, die eine Coroutine an ihn senden:

| Wo Sie sind | Rufen Sie an | Tut |
|---|---|---|
| Synchronisierungscode, z. B. eine Seite | `run(UserService.get_all())` | führt ihn aus und gibt das Ergebnis zurück |
| Asynchroner Code, wie ein Handler oder ein Controller | `await arun(UserService.get_all())` | derselbe, ohne den Server zu blockieren |

```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

Tortoise verbindet sich, wenn einer von ihnen zum ersten Mal aufgerufen wird. Rufen Sie das Modell von einem `async def` auf.
(`await UserModel.all()` innerhalb eines Dienstes), nicht auf Modulebene: Ein Aufruf außerhalb einer Coroutine wird ausgeführt
bevor Tortoise eine Verbindung hergestellt hat.

Listen Sie jedes Modul auf, das Modelle in `TORTOISE_ORM` enthält (der `models`-Eintrag von `src/configs/db.py`).
Das Gerüst listet das Benutzermodell und `aerich.models` auf; Ein Modell in einem Modul, das nicht aufgeführt ist, ist nicht aufgeführt
gefunden.

## Migrationen

`nx migrate` wählt das Tool für Ihr ORM aus: Alembic für SQLModel und SQLAlchemy, Aerich für
Schildkröte-ORM.

| Befehl | führt | aus
|---|---|
| `nx migrate --init` | Initialisieren Sie das Migrationstool für das Projekt |
| `nx migrate -m "add users"` | Erstellen Sie eine Migration aus Ihren Modelländerungen |
| `nx migrate --upgrade` | Ausstehende Migrationen anwenden |

Mit Aerich führt der erste `nx migrate` `aerich init-db` aus, wodurch die erste Migration entsteht und die
Tische zusammen; Die nächsten laufen `aerich migrate --name "..."` und `--upgrade` läuft
`aerich upgrade`.

`nx migrate` stoppt mit einer eindeutigen Meldung, wenn `DATABASE_URL` fehlt oder die Datenbank nicht vorhanden sein kann
erreicht (nur Alembic: Aerich meldet eigene Fehler).

### Die erste Migration wird für Sie durchgeführt

Wenn Sie einen ORM auswählen und eine Datenbank-URL angeben, richtet `nx new` das Migrationstool ein und erstellt das
erste Migration und wendet sie an, sodass die Benutzerseite auf die erste `nexy dev` antwortet. Die Migration
Das Tool (`alembic` oder `aerich`) ist im Projekt mit dem ORM installiert.

Wenn die Datenbank nicht antwortet (ein PostgreSQL-Server, der nicht läuft, ein fehlender Treiber), `nx new`
sagt den Grund, überspringt die Migration und listet die beiden Befehle auf, die ausgeführt werden sollen, wenn sie bereit ist:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

Bis die Tabellen vorhanden sind, schlägt eine Seite, die die Datenbank liest, mit „keine solche Tabelle“ fehl.

### Fügen Sie ein Modell hinzu

Alembic vergleicht die Datenbank mit den Modellen, die `alembic/env.py` importiert. Ein Modell im Neuen
Das Modul wird erst angezeigt, wenn das Modul dort neben dem Benutzermodell importiert wird:

```python filename="alembic/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Listen Sie für Tortoise-ORM das Modul stattdessen in `TORTOISE_ORM` auf (siehe oben).

## Nächste Schritte

- [Testen](testing.md): Testhandler anhand einer temporären Datenbank
- [Konfiguration](../reference/config.md)
- [Bereitstellen](../deployment/README.md): `DATABASE_URL` in der Produktion festlegen