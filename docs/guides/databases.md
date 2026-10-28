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

`nx migrate` stops with a clear message when `DATABASE_URL` is missing or the database cannot be
reached.

> **Good to know**: a new project has models but no tables. Until you run
> `nx migrate -m "create tables"` and then `nx migrate --upgrade`, the users page fails with
> "no such table". `nx new` prints these two steps for a project with an ORM.

## Next steps

- [Testing](testing.md): test handlers against a temporary database
- [Config](../reference/config.md)
- [Deploy](../deployment/README.md): set `DATABASE_URL` in production
