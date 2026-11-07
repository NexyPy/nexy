# Incluir um roteador FastAPI existente no Nexy

Para incluir um roteador FastAPI existente no Nexy, defina `useRouter` para aquele `APIRouter` na classe `NexyConfig` de `nexyconfig.py`: suas rotas são servidas como estão, ao lado dos arquivos de `src/routes/`.

## Quando usar um roteador personalizado

- **Migração gradual**: um aplicativo FastAPI se move para Nexy rota por rota, e suas rotas antigas continuam respondendo enquanto isso.
- **Reutilização de código**: um pacote já expõe um `APIRouter`, para autenticação ou cobrança.
- **Um backend que você mantém**: a API permanece simples FastAPI, e Nexy adiciona as páginas.

## Definir `useRouter` em `nexyconfig.py`

O roteador é qualquer FastAPI `APIRouter`, escrito da maneira que você já escreve um:

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` é um campo da classe `NexyConfig`, como toda configuração do projeto:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` então responde `GET /api/status` e `GET /api/users/{id}`, e `/docs` os lista.

> [!NOTE]
> `useRouter` em `nexyconfig.py` é uma configuração. `from nexy import useRouter` é outra coisa: o gancho que uma página `.nexy` usa para ler a rota atual. Não importe-o para configurar o roteador.

## Vários roteadores

`useRouter` leva um roteador. Reúna vários sob um dos pais com `include_router`:

```python filename="src/legacy/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## Páginas e arquivos de rota próximos a ela

`src/routes/` ainda é lido enquanto `useRouter` está definido: uma página `.nexy` ou um arquivo de rota `.py` responde próximo às rotas incluídas.

```nexy filename="src/rotas/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

Dois limites enquanto `useRouter` estiver definido:

- as páginas não são quebradas por `layout.nexy`;
- `useCSR = True` é recusado: `nx dev` e `nx build` respondem `useCSR requires file-based routing`.

Um URL é respondido uma vez. Dê um prefixo ao roteador incluído, aqui `/api`, e mantenha os arquivos de `src/routes/` fora dos caminhos que ele usa.

## Um aplicativo FastAPI completo

`useRouter` usa um aplicativo `APIRouter`, não um aplicativo `FastAPI`. As rotas de um aplicativo ficam em seu atributo `router`:

```python filename="src/legacy/service.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

O middleware, os manipuladores de exceções e os eventos de inicialização do próprio aplicativo ficam para trás: mova-os para `useMiddlewares` e os outros campos de `nexyconfig.py`.

## Dependências, autenticação e banco de dados

O roteador é executado no processo Nexy, portanto `Depends`, esquemas de segurança e sessões de banco de dados funcionam como no aplicativo original:

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## Teste

```python filename="testes/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## Próximas etapas

- [De FastAPI para Nexy](../../coming-from/fastapi.md): mova as rotas para os arquivos, uma por uma
- [Roteamento baseado em arquivo](../fbr/README.md)
- [Roteamento modular](../modular/README.md): `useRouter = AppModule`
