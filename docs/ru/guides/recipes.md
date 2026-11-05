# Рецепты

Три вещи, которые нужны почти каждому приложению: целые файлы, которые можно копировать. Каждый приведенный ниже блок кода с `filename` записывается в новый проект и проверяется набором тестов, поэтому выполняется то, что вы читаете.

Они используют простые обработчики API; одни и те же функции работают за страницей в любом [режиме](../routing/fbr/modes.md).

## Войти с помощью сеанса

Посетитель публикует имя и пароль, сервер запоминает их в подписанном файле cookie, и все, что находится под `/api/account`, закрыто для всех остальных.

Включите сеансы. Им нужно `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

Войдите и выйдите:

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

Защитите всю папку одним [`dependencies.py`](../routing/fbr/dependencies/README.md):

```python filename="src/routes/api/account/dependents.py"
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

> [!ПРИМЕЧАНИЕ]
> держите настоящие пароли подальше от источника. Сохраните хеш (`argon2`, `bcrypt`) и прочитайте секретный ключ из среды. Файл cookie сеанса подписан, а не зашифрован.

## JSON API с возможностью создания, чтения и удаления.

Магазин в модуле, маршрут сбора и маршрут товара. Замените словарь на [базу данных](databases.md), если данные должны пережить перезапуск.

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

```python filename="src/routes/api/notes/[id].py"
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

Тело, которое не соответствует `NewNote`, отклоняется с помощью `422` до запуска вашего кода, и возвращаемая аннотация становится документированным ответом. См. [проверка и ошибки](../routing/fbr/handlers/validation-and-errors.md).

## Получить файл

Для загрузки необходимо `python-multipart` (`uv add python-multipart`). Проверьте размер самостоятельно и никогда не используйте имя файла клиента в качестве пути:

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

`Path(...).name` удаляет любую папку, имя которой клиент указал, например `../../etc/passwd`. Сохраняйте байты под сгенерированным вами именем, а не под этим.

## Следующие шаги

- [Действия](actions.md): типизированные серверные функции для форм и кнопок.
- [Промежуточное ПО и безопасность](middleware-and-security.md): CORS, хосты, сеансы
- [Тестирование](testing.md): протестируйте свои собственные обработчики таким же образом
