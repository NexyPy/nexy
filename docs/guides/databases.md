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

With Tortoise-ORM, queries are async: call them with `asyncio.run(...)` in the frontmatter, as the
scaffold does.

## Use a service in an API handler

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```

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

## Next steps

- [Testing](testing.md): test handlers against a temporary database
- [Config](../reference/config.md)
- [Deploy](../deployment/README.md): set `DATABASE_URL` in production
