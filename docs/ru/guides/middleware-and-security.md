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

## HTTPS

Обслуживайте HTTPS напрямую с помощью `useSslKeyfile` и `useSslCertfile` или завершите TLS на обратном прокси-сервере и установите `useHTTPSRedirect`. В процессе разработки сервер разработки Vite остается на HTTP-петле позади источника Nexy, поэтому TLS никогда не достигает его.

## Контрольный список производства

- `useDocs = False` если схема OpenAPI не должна быть общедоступной.
- `useTrustedHost` установите для ваших доменов, чтобы блокировать атаки по заголовку хоста.
- `useCORS` с явным происхождением, никогда `["*"]` вместе с учетными данными.
- Настоящий `secret_key` для сессий, считываемых из среды.
- Свойства, передаваемые клиентским компонентам, Nexy экранирует HTML. Не отмечайте ввод пользователя `| safe` в шаблонах.

## Охранники и зависимости

Защита на каждом маршруте использует зависимости FastAPI. `dependencies.py` в каталоге маршрутов применяется ко всему, что находится ниже него: см. [Зависимости](../routing/fbr/dependencies/README.md). В модульном маршрутизаторе используйте [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Следующие шаги

- [Конфигурация](../reference/config.md): каждое поле промежуточного программного обеспечения.
- [Развернуть](../deployment/README.md)
- [Производительность](../deployment/performance.md)
