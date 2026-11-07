# Bancos de dados

`nx new` pode criar uma camada de modelo com SQLModel, SQLAlchemy ou Tortoise-ORM. Nexy não envolve o ORM: você o usa diretamente, a partir de manipuladores e páginas.

## O que o andaime adiciona

| Arquivo | Objetivo |
|---|---|
| `src/configs/db.py` | o motor (SQLModel, SQLAlchemy) ou as configurações `TORTOISE_ORM` |
| `src/models/` | classes de modelo |
| `src/services/` | funções que consultam os modelos |
| `.env` | `DATABASE_URL`, escrito quando você fornece uma URL de banco de dados durante `nx new` |

A string de conexão vem da variável de ambiente `DATABASE_URL`. Quando não é definido, o mecanismo de scaffolded volta para um arquivo local SQLite, `dev.db`.

## Use um serviço em uma página

<!-- router:fbr,custom -->
```nexy filename="src/rotas/usuários/index.nexy"
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

## Use um serviço em um manipulador de API

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```
<!-- /router -->

<!-- router:modular -->
Um controlador chama o serviço e passa as linhas para sua visualização ou as retorna como JSON:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

from src.services.user_service import UserService


@Controller("/users")
class UserController:
    async def get(self):
        users = UserService.get_all()
        return useViews("src/apps/users/user_view.nexy", context={"users": users})


@Controller("/api/users")
class UserApiController:
    async def get(self):
        return UserService.get_all()
```

```nexy filename="src/apps/users/user_view.nexy"
---
users: prop[list] = []
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```
<!-- /router -->

## Tortoise-ORM é assíncrono

Uma página é executada no loop de eventos do servidor e não pode esperar por ela, então `asyncio.run(...)` falha lá com "não pode ser chamada a partir de um loop de eventos em execução". O scaffolded `src/configs/db.py` fornece ao Tortoise um loop próprio, em um thread, e dois auxiliares que enviam uma corrotina para ele:

| Onde você está | Ligar | Faz |
|---|---|---|
| código de sincronização, como uma página | `run(UserService.get_all())` | executa e retorna o resultado |
| código assíncrono, como um manipulador ou controlador | `await arun(UserService.get_all())` | o mesmo, sem bloquear o servidor |

<!-- router:fbr,custom -->
```nexy filename="src/rotas/usuários/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```
<!-- /router -->

<!-- router:modular -->
Um controlador é assíncrono: aguarda o serviço através de `arun` e a visualização mostra apenas as linhas:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

from src.configs.db import arun
from src.services.user_service import UserService


@Controller("/users")
class UserController:
    async def get(self):
        users = await arun(UserService.get_all())
        return useViews("src/apps/users/user_view.nexy", context={"users": users})
```
<!-- /router -->

Tortoise conecta na primeira vez que um deles é chamado. Chame o modelo de um `async def` (`await UserModel.all()` dentro de um serviço), não no nível do módulo: uma chamada fora de uma corrotina é executada antes de Tortoise ser conectado.

Liste todos os módulos que contêm modelos em `TORTOISE_ORM` (a entrada `models` de `src/configs/db.py`). O andaime lista o modelo do usuário e `aerich.models`; um modelo em um módulo que não está listado não foi encontrado.

## Migrações

`nx migrate` escolhe a ferramenta para o seu ORM: Alembic para SQLModel e SQLAlchemy, Aerich para Tortoise-ORM.

| Comando | Faz |
|---|---|
| `nx migrate --init` | inicializar a ferramenta de migração para o projeto |
| `nx migrate -m "add users"` | crie uma migração a partir das alterações do seu modelo |
| `nx migrate --upgrade` | aplicar migrações pendentes |

Com Aerich, o primeiro `nx migrate` executa `aerich init-db`, que cria a primeira migração e as tabelas juntas; os próximos executam `aerich migrate --name "..."` e `--upgrade` executam `aerich upgrade`.

`nx migrate` para com uma mensagem clara quando `DATABASE_URL` está faltando ou o banco de dados não pode ser alcançado (Alembic apenas: Aerich relata seus próprios erros).

### A primeira migração é feita para você

Quando você escolhe um ORM e fornece uma URL de banco de dados, `nx new` configura a ferramenta de migração, cria a primeira migração e a aplica, para que a página do usuário responda na primeira `nexy dev`. A ferramenta de migração (`alembic` ou `aerich`) é instalada no projeto com o ORM.

Se o banco de dados não responder (um servidor PostgreSQL que não está rodando, um driver ausente), `nx new` diz o porquê, pula a migração e lista os dois comandos para executar quando estiver pronto:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

Até que as tabelas existam, uma página que lê o banco de dados falha com "nenhuma tabela".

### Adicionar um modelo

Alembic compara o banco de dados com os modelos que `alembic/env.py` importa. Um modelo em um novo módulo não é visto até que esse módulo seja importado para lá, próximo ao modelo do usuário:

```python filename="alambique/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Para Tortoise-ORM, liste o módulo em `TORTOISE_ORM` (veja acima).

## Próximas etapas

- [Testes](testing.md): manipuladores de teste em um banco de dados temporário
- [Configuração](../reference/config.md)
- [Implantar](../deployment/README.md): definir `DATABASE_URL` em produção
