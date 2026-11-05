# Страницы ошибок в папке

Папка может отвечать на свои собственные ошибки: блог с ошибкой 404, приватная область, предлагающая форму входа вместо голого `401`. Остальная часть сайта сохраняет уже имеющуюся страницу.

На этой странице добавляется один из этих файлов и отображается ответ на него.

## Правило

**Самый глубокий файл, соответствующий ответам URL.** Все остальное остается как есть: те же коды состояния, JSON для API-клиента и встроенная страница, когда ни в одной папке цепочки нет файла.

![Область страницы ошибки](../../../assets/error-page-scopes.svg)

Для `/blog/2024/hello` Nexy поднимается по дереву: `/blog/2024`, затем `/blog`, затем `/`. Первая папка, содержащая файл, отвечает. Папка сопоставляется целиком: `/blogger/hello` не находится под `/blog`, поэтому копия в `blog/` никогда не отвечает на нее.

## Четыре файла

| Файл | Ответы | Что до него доходит |
|---|---|---|
| `notfound.nexy` | `404` | URL-адрес не соответствует маршруту, `notFound()` |
| `errors.nexy` | `500` | исключение ничего не обработано |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` остается зарезервированным: он еще не имеет эффекта во время выполнения.

Одного файла где-то в `src/routes/` достаточно, чтобы Nexy ответил на этот статус: копия в корне отвечает всему проекту, копия в папке отвечает этой папке, а URL-адрес за пределами каждой копии получает встроенную страницу. Зарезервируйте другое расширение для этих имен в `nexyconfig.py` с помощью `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` и `useUnauthorizedExtensions`.

## Ваша первая страница папки

```nexy filename="src/маршруты/блог/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

Запустите проект и запросите сообщение, которого не существует:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

URL-адрес за пределами папки сохраняет уже имеющуюся у вас страницу:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## 401, который куда-то ведет

Папка защищенной области отвечает `401` страницей, которая предлагает путь:

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependents.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

Каждый звонок и каждый статус хранят два ответа:

| Кто спрашивает | `401` с файлом | `401` без одного |
|---|---|---|
| Браузер (`Accept: text/html`) | страница папки | встроенная страница |
| Клиент (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` добавляет `WWW-Authenticate: Bearer` к обоим ответам. Деталь, созданная на основе пользовательского ввода, на странице экранируется HTML.

> [!TIP]
> `Accept: */*`, значение по умолчанию для `curl` и многих HTTP-библиотек, не запрашивает ни того, ни другого и получает HTML-страницу. Добавьте `-H "Accept: application/json"` если вам нужен ответ в формате JSON.

## Проверьте это

```python filename="тесты/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## Следующие шаги

- [Страницы ошибок](README.md): что вызывает каждый статус, HTML или JSON
- [Зависимости и меры защиты](../dependencies/README.md): защита всей папки.
- [Тестирование](../../../guides/testing.md): `TestClient` из первого теста
