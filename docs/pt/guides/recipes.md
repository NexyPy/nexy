# Receitas

Três coisas que quase todos os aplicativos precisam: arquivos completos que você pode copiar. Cada bloco de código abaixo com `filename` é escrito em um novo projeto e exercitado pelo conjunto de testes, então o que você lê é o que é executado.

Eles usam manipuladores de API simples; as mesmas funções funcionam atrás de uma página em [modo](../routing/fbr/modes.md).

## Faça login com uma sessão

Um visitante publica um nome e uma senha, o servidor os lembra em um cookie assinado e tudo em `/api/account` é fechado para qualquer outra pessoa.

Ative as sessões. Eles precisam de `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

Entrar e sair:

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import HTTPException, Request

USERS = {"ada": "lovelace"}


class Credentials(BaseModel):
    name: str
    password: str


async def POST(request: Request, body: Credentials):
    if USERS.get(body.name) != body.password:
        raise HTTPException(status_code=401, detail="Wrong name or password")
    request.session["user"] = body.name
    return {"user": body.name}
```

```python filename="src/routes/api/logout.py"
from nexy.http import Request


async def POST(request: Request):
    request.session.clear()
    return {"signed_out": True}
```

Guarde uma pasta inteira com um [`dependencies.py`](../routing/fbr/dependencies/README.md):

```python filename="src/routes/api/account/dependencies.py"
from nexy.http import HTTPException, Request


def current_user(request: Request) -> str:
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Sign in first")
    return request.session["user"]


dependencies = [current_user]
```

```python filename="src/routes/api/account/index.py"
from nexy.http import Request


async def GET(request: Request):
    return {"user": request.session["user"]}
```

> [!NOTE]
> mantenha senhas reais fora da fonte. Armazene um hash (`argon2`, `bcrypt`) e leia a chave secreta do ambiente. O cookie de sessão é assinado, não criptografado.

## Uma API JSON com criação, leitura e exclusão

Uma loja em módulo, uma rota de coleta e uma rota de item. Substitua o dicionário por [um banco de dados](databases.md) quando os dados precisarem sobreviver a uma reinicialização.

```python filename="src/notes.py"
from pydantic import BaseModel


class Note(BaseModel):
    id: int
    title: str


NOTES: dict[int, Note] = {}
```

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel

from src.notes import NOTES, Note


class NewNote(BaseModel):
    title: str


async def GET() -> list[Note]:
    return list(NOTES.values())


async def POST(body: NewNote) -> Note:
    note = Note(id=max(NOTES, default=0) + 1, title=body.title)
    NOTES[note.id] = note
    return note
```

```python filename="src/rotas/api/notes/[id].py"
from nexy.http import HTTPException

from src.notes import NOTES, Note


async def GET(id: int) -> Note:
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return NOTES[id]


async def DELETE(id: int) -> dict[str, bool]:
    if NOTES.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="No such note")
    return {"deleted": True}
```

Um corpo que não se ajusta a `NewNote` é recusado com `422` antes que seu código seja executado, e a anotação de retorno se torna a resposta documentada. Veja [validação e erros](../routing/fbr/handlers/validation-and-errors.md).

## Receber um arquivo

Os uploads precisam de `python-multipart` (`uv add python-multipart`). Verifique você mesmo o tamanho e nunca use o nome do arquivo do cliente como caminho:

```python filename="src/routes/api/upload.py"
from pathlib import Path

from nexy.http import HTTPException, UploadFile

MAX_BYTES = 1_000_000


async def POST(file: UploadFile) -> dict[str, int | str]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = Path(file.filename or "upload").name
    return {"name": name, "size": len(data)}
```

`Path(...).name` descarta qualquer pasta que o cliente colocou no nome, como `../../etc/passwd`. Salve os bytes com um nome que você gerar, não com este.

## Próximas etapas

- [Ações](actions.md): funções de servidor digitadas para formulários e botões
- [Middleware e segurança](middleware-and-security.md): CORS, hosts, sessões
- [Teste](testing.md): teste seus próprios manipuladores da mesma maneira
