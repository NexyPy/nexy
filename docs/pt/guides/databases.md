# Bancos de dados

`nx new` pode criar uma camada de modelo com SQLModel, SQLAlchemy ou Tortoise-ORM. Nexy não embrulha
o ORM: você o usa diretamente, a partir de manipuladores e páginas.

## O que o andaime adiciona

| Arquivo | Finalidade |
|---|---|
| `src/configs/db.py` | o mecanismo (SQLModel, SQLAlchemy) ou as configurações `TORTOISE_ORM` |
| `src/models/` | classes de modelo |
| `src/services/` | funções que consultam os modelos |
| `.env` | `DATABASE_URL`, escrito quando você fornece uma URL de banco de dados durante `nx new` |

A string de conexão vem da variável de ambiente `DATABASE_URL`. Quando não estiver definido, o
o mecanismo scaffolded recorre a um arquivo SQLite local, `dev.db`.

## Use um serviço em uma página

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

## Usar um serviço em um manipulador de API

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```

## Tortoise-ORM é assíncrono

Uma página é executada no loop de eventos do servidor e não pode esperar por ela, então `asyncio.run(...)` falha lá com
"não pode ser chamado de um loop de eventos em execução". O andaime `src/configs/db.py` dá à Tartaruga uma
loop próprio, em um thread, e dois auxiliares que enviam uma corrotina para ele:

| Onde você está | Ligue para | Faz |
|---|---|---|
| código de sincronização, como uma página | `run(UserService.get_all())` | executa-o e retorna o resultado |
| código assíncrono, como um manipulador ou um controlador | `await arun(UserService.get_all())` | o mesmo, sem bloquear o servidor |

```nexy filename="src/rotas/usuários/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

A tartaruga se conecta na primeira vez que um deles é chamado. Chame o modelo de um `async def`
(`await UserModel.all()` dentro de um serviço), não no nível do módulo: uma chamada fora de uma corrotina é executada
antes que o Tortoise se conecte.

Liste todos os módulos que contêm modelos em `TORTOISE_ORM` (a entrada `models` de `src/configs/db.py`).
O andaime lista o modelo do usuário e `aerich.models`; um modelo em um módulo que não está listado não é
encontrado.

## Migrações

`nx migrate` escolhe a ferramenta para seu ORM: Alembic para SQLModel e SQLAlchemy, Aerich para
Tartaruga-ORM.

| Comando | Faz |
|---|---|
| `nx migrate --init` | inicializar a ferramenta de migração para o projeto |
| `nx migrate -m "add users"` | crie uma migração a partir das alterações do seu modelo |
| `nx migrate --upgrade` | aplicar migrações pendentes |

Com Aerich, o primeiro `nx migrate` executa `aerich init-db`, que cria a primeira migração e a
mesas juntas; os próximos executam `aerich migrate --name "..."` e `--upgrade` executam
`aerich upgrade`.

`nx migrate` para com uma mensagem clara quando `DATABASE_URL` está faltando ou o banco de dados não pode ser
alcançado (Apenas Alambique: Aerich relata seus próprios erros).

### A primeira migração é feita para você

Quando você escolhe um ORM e fornece uma URL de banco de dados, `nx new` configura a ferramenta de migração, cria o
primeira migração e a aplica, então a página do usuário responde na primeira `nexy dev`. A migração
ferramenta (`alembic` ou `aerich`) é instalada no projeto com o ORM.

Se o banco de dados não responder (um servidor PostgreSQL que não está em execução, um driver ausente), `nx new`
diz o porquê, ignora a migração e lista os dois comandos a serem executados quando estiver pronto:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

Até que as tabelas existam, uma página que lê o banco de dados falha com "nenhuma tabela".

### Adicionar um modelo

Alembic compara o banco de dados com os modelos que `alembic/env.py` importa. Um modelo em um novo
O módulo não é visto até que esse módulo seja importado para lá, próximo ao modelo do usuário:

```python filename="alambique/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Para Tortoise-ORM, liste o módulo em `TORTOISE_ORM` (veja acima).

## Próximas etapas

- [Testing](testing.md): manipuladores de teste em um banco de dados temporário
- [Configuração](../reference/config.md)
- [Implantar](../deployment/README.md): definir `DATABASE_URL` em produção