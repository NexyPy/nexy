# Bases de datos

`nx new` puede crear una capa de modelo con SQLModel, SQLAlchemy o Tortoise-ORM. Nexy no envuelve
el ORM: lo usas directamente, desde manejadores y páginas.

## Lo que añade el andamio

| Archivo | Propósito |
|---|---|
| `src/configs/db.py` | el motor (SQLModel, SQLAlchemy) o la configuración `TORTOISE_ORM` |
| `src/models/` | clases de modelo |
| `src/services/` | funciones que consultan los modelos |
| `.env` | `DATABASE_URL`, escrito cuando proporcionas la URL de una base de datos durante `nx new` |

La cadena de conexión proviene de la variable de entorno `DATABASE_URL`. Cuando está desarmado, el
El motor con scaffolding recurre a un archivo SQLite local, `dev.db`.

## Usar un servicio en una página

```nexy filename="src/rutas/usuarios/index.nexy"
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

## Usar un servicio en un controlador API

```python filename="src/rutas/api/usuarios.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```

## Tortoise-ORM es asíncrono

Una página se ejecuta en el bucle de eventos del servidor y no puede esperar, por lo que `asyncio.run(...)` falla allí con
"no se puede llamar desde un bucle de eventos en ejecución". El andamio `src/configs/db.py` le da a Tortoise un
bucle propio, en un hilo, y dos ayudantes que le envían una corrutina:

| Dónde estás | Llama | Hace |
|---|---|---|
| código de sincronización, como una página | `run(UserService.get_all())` | lo ejecuta y devuelve el resultado |
| código asíncrono, como un manejador o un controlador | `await arun(UserService.get_all())` | el mismo, sin bloquear el servidor |

```nexy filename="src/rutas/usuarios/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

La tortuga se conecta la primera vez que se llama a una de ellas. Llame al modelo desde un `async def`
(`await UserModel.all()` dentro de un servicio), no a nivel de módulo: se ejecuta una llamada fuera de una rutina
antes de que Tortoise se haya conectado.

Enumere todos los módulos que contienen modelos en `TORTOISE_ORM` (la entrada `models` de `src/configs/db.py`).
El andamio enumera el modelo de usuario y `aerich.models`; un modelo en un módulo que no está listado no es
encontrado.

## Migraciones

`nx migrate` elige la herramienta para su ORM: Alembic para SQLModel y SQLAlchemy, Aerich para
Tortuga-ORM.

| Comando | Hace |
|---|---|
| `nx migrate --init` | inicializar la herramienta de migración para el proyecto |
| `nx migrate -m "add users"` | crea una migración a partir de los cambios de tu modelo |
| `nx migrate --upgrade` | aplicar migraciones pendientes |

Con Aerich, el primer `nx migrate` ejecuta `aerich init-db`, lo que crea la primera migración y la
mesas juntas; los siguientes ejecutan `aerich migrate --name "..."`, y `--upgrade` ejecutan
`aerich upgrade`.

`nx migrate` se detiene con un mensaje claro cuando falta `DATABASE_URL` o no se puede acceder a la base de datos.
alcanzado (sólo Alambique: Aerich informa de sus propios errores).

### La primera migración está hecha para ti.

Cuando elige un ORM y proporciona una URL de base de datos, `nx new` configura la herramienta de migración, crea el
primera migración y la aplica, por lo que la página de usuarios responde en la primera `nexy dev`. la migracion
La herramienta (`alembic` o `aerich`) está instalada en el proyecto con el ORM.

Si la base de datos no responde (un servidor PostgreSQL que no se está ejecutando, falta un controlador), `nx new`
dice por qué, omite la migración y enumera los dos comandos que se ejecutarán cuando esté listo:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

Hasta que existan las tablas, una página que lee la base de datos falla con "no existe tal tabla".

### Agregar un modelo

Alembic compara la base de datos con los modelos que `alembic/env.py` importa. Un modelo en un nuevo
El módulo no se ve hasta que ese módulo se importa allí, junto al modelo de usuario:

```python filename="alambique/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Para Tortoise-ORM, enumere el módulo en `TORTOISE_ORM` (ver arriba).

## Próximos pasos

- [Testing](testing.md): prueba los controladores contra una base de datos temporal
- [Configuración](../reference/config.md)
- [Implementar](../deployment/README.md): establecer `DATABASE_URL` en producción