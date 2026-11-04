# Dependências e guardas

Compartilhe autenticação, sessões de banco de dados e outras configurações entre rotas com dependências FastAPI.
Eles funcionam em dois níveis, e o nível do diretório é herdado como layouts.

| Nível | Onde | se aplica a |
|---|---|---|
| Diretório | `dependencies.py` | todas as rotas no diretório e abaixo, páginas incluídas |
| Manipulador | `Depends`, `@UseGuard`, `@Middleware` | um manipulador |

## Por diretório: `dependencies.py`

Um `dependencies.py` declara uma lista `dependencies` de funções simples. Nexy envolve cada um em
`Depends`.

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!NOTA]
> liste as próprias funções. Um objeto `Depends(...)` na lista é ignorado.

Cada rota em `src/routes/admin/` agora requer o cabeçalho, `.py` manipuladores e `.nexy` páginas
iguais.

## Herança

As dependências são coletadas da raiz das rotas até o diretório da rota, **mais externo primeiro**,
exatamente como os layouts, e os próprios guardas do manipulador são executados por último:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

Para `GET /admin/users` a ordem é `root`, `admin`, `users`, as funções do manipulador `@UseGuard`,
suas funções `@Middleware` e, em seguida, o manipulador. Um grupo de rotas (`(group)/`) é um diretório como qualquer outro
outro, então seu `dependencies.py` participa.

## Por manipulador

Use `Depends` na assinatura, como em qualquer aplicativo FastAPI:

```python filename="src/rotas/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Guardas e middleware em um manipulador

`@UseGuard` e `@Middleware` anexam dependências FastAPI a um manipulador sem alterar seu
assinatura. Ambos são dependências, não middleware ASGI:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

Para middleware ASGI real (CORS, GZip, sessões, seu próprio) use `useMiddlewares` e o `use*`
opções em [Middleware e segurança](../../../guides/middleware-and-security.md).

## Falhando em uma dependência

Uma dependência rejeita uma solicitação aumentando. `HTTPException` responde com o status que você levantou, como
JSON para clientes API (`Accept: application/json`) e como página de erro para navegadores. Veja
[Validação e erros](../handlers/validation-and-errors.md).

## Próximas etapas

- [Herança](../inheritance.md)
- [Manipuladores](../handlers/README.md)
- [Middleware e segurança](../../../guides/middleware-and-security.md)