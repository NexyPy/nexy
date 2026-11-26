# Промежуточное ПО и безопасность

Nexy работает на FastAPI и Starlette, поэтому применяется их промежуточное программное обеспечение. Общие — одна строка в `nexyconfig.py`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

Каждый словарь `use*` передается в качестве аргументов ключевого слова соответствующему промежуточному программному обеспечению Starlette: `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Ваше собственное промежуточное программное обеспечение

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` использует классы промежуточного программного обеспечения ASGI.

## Ограничение скорости

`useRateLimit` отвечает `429 Too Many Requests` на адрес клиента, который отправляет более `requests` запросов в одном окне продолжительностью `per` секунд.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy гарантирует, что запрос, превышающий лимит, получит `429` с заголовком `Retry-After`, количество секунд, оставшихся в окне, и никогда не достигнет ваших маршрутов, действий или промежуточного программного обеспечения.

Nexy гарантирует, что без `useRateLimit` не будет добавлено промежуточное программное обеспечение с ограничением скорости.

Nexy гарантирует, что количество зондов `useHealth` никогда не будет ограничено.

`paths` не является обязательным: без него каждый путь ограничен. Действия сервера обслуживаются под `/_nx_`, так что этот префикс ограничивает их все.

Окно фиксировано и доступно всем клиентам: отсчет начинается заново каждые секунды, кратные `per`. Таким образом, клиент может отправить до двух раз `requests` через край окна.

Графы живут в памяти каждого работника. Если `useWorkers` выше единицы, клиент может отправить `requests` каждому работнику, и подсчет начнется снова при перезапуске сервера.

Адрес клиента — это тот адрес, по которому uvicorn отправляет запрос. За обратным прокси-сервером на той же машине uvicorn читает его из `X-Forwarded-For`; для прокси-сервера на другом компьютере укажите его адрес в переменной среды `FORWARDED_ALLOW_IPS`, иначе каждый клиент будет использовать адрес прокси-сервера.

Ваше приложение несет ответственность за ограничение, общее для нескольких рабочих процессов или серверов: обратного прокси-сервера или хранилища, такого как Redis.

## HTTPS

Обслуживайте HTTPS напрямую с помощью `useSslKeyfile` и `useSslCertfile` или завершите TLS на обратном прокси-сервере и установите `useHTTPSRedirect`. В процессе разработки сервер разработки Vite остается на HTTP-петле позади источника Nexy, поэтому TLS никогда не достигает его.

## Контрольный список производства

- `useDocs = False` если схема OpenAPI не должна быть общедоступной.
- `useTrustedHost` установлен для ваших доменов, чтобы блокировать атаки по заголовку хоста.
- `useCORS` с явным происхождением, никогда `["*"]` вместе с учетными данными.
- Настоящий `secret_key` для сессий, считываемых из среды.
- Props, передаваемые клиентским компонентам, Nexy экранирует HTML. Не отмечайте ввод пользователя `| safe` в шаблонах.

## Охранники и зависимости

Защита на каждом маршруте использует зависимости FastAPI. `dependencies.py` в каталоге маршрутов применяется ко всему, что находится под ним: см. [Зависимости](../routing/fbr/dependencies/README.md). В модульном маршрутизаторе используйте [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Следующие шаги

- [Конфигурация](../reference/config.md): каждое поле промежуточного программного обеспечения.
- [Развернуть](../deployment/README.md)
- [Производительность](../deployment/performance.md)
