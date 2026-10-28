# Databases

`nx new` can scaffold a model layer with SQLModel, SQLAlchemy or Tortoise-ORM. Nexy does not wrap
the ORM: you use it directly, from handlers and pages.

## What the scaffold adds

| File | Purpose |
|---|---|
| `src/configs/db.py` | the engine (SQLModel, SQLAlchemy) or the `TORTOISE_ORM` settings |
| `src/models/` | model classes |
| `src/services/` | functions that query the models |
| `.env` | `DATABASE_URL`, written when you give a database URL during `nx new` |

The connection string comes from the `DATABASE_URL` environment variable. When it is unset, the
scaffolded engine falls back to a local SQLite file, `dev.db`.

## Use a service in a page

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

## Use a service in an API handler

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```

## Tortoise-ORM is async

A page runs in the server's event loop and cannot wait on it, so `asyncio.run(...)` fails there with
"cannot be called from a running event loop". The scaffolded `src/configs/db.py` gives Tortoise a
loop of its own, in one thread, and two helpers that send a coroutine to it:

| Where you are | Call | Does |
|---|---|---|
| sync code, such as a page | `run(UserService.get_all())` | runs it and returns the result |
| async code, such as a handler or a controller | `await arun(UserService.get_all())` | the same, without blocking the server |

```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

Tortoise connects the first time one of them is called. Call the model from an `async def`
(`await UserModel.all()` inside a service), not at module level: a call outside a coroutine runs
before Tortoise has connected.

List every module that holds models in `TORTOISE_ORM` (the `models` entry of `src/configs/db.py`).
The scaffold lists the user model and `aerich.models`; a model in a module that is not listed is not
found.

## Migrations

`nx migrate` picks the tool for your ORM: Alembic for SQLModel and SQLAlchemy, Aerich for
Tortoise-ORM.

| Command | Does |
|---|---|
| `nx migrate --init` | initialise the migration tool for the project |
| `nx migrate -m "add users"` | create a migration from your model changes |
| `nx migrate --upgrade` | apply pending migrations |

With Aerich, the first `nx migrate` runs `aerich init-db`, which creates the first migration and the
tables together; the next ones run `aerich migrate --name "..."`, and `--upgrade` runs
`aerich upgrade`.

`nx migrate` stops with a clear message when `DATABASE_URL` is missing or the database cannot be
reached (Alembic only: Aerich reports its own errors).

### The first migration is made for you

When you choose an ORM and give a database URL, `nx new` sets the migration tool up, creates the
first migration and applies it, so the users page answers on the first `nexy dev`. The migration
tool (`alembic` or `aerich`) is installed in the project with the ORM.

If the database does not answer (a PostgreSQL server that is not running, a missing driver), `nx new`
says why, skips the migration and lists the two commands to run when it is ready:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

Until the tables exist, a page that reads the database fails with "no such table".

### Add a model

Alembic compares the database with the models that `alembic/env.py` imports. A model in a new
module is not seen until that module is imported there, next to the user model:

```python filename="alembic/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

For Tortoise-ORM, list the module in `TORTOISE_ORM` instead (see above).

## Next steps

- [Testing](testing.md): test handlers against a temporary database
- [Config](../reference/config.md)
- [Deploy](../deployment/README.md): set `DATABASE_URL` in production
