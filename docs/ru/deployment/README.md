# Развертывание

Две команды: `nx build` производит артефакты, `nx start` их обслуживает.

**Прежде чем начать:** проект, который собирается локально с помощью `nx build` и — для клиентских страниц — набор инструментов внешнего интерфейса, установленный `nx new`.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

Среде выполнения требуется только Python. Uvicorn обслуживает скомпилированное приложение и статические ресурсы; ни один процесс Node и процесс Vite не задействованы.

## Что дает сборка

`__nexy__/` содержит скомпилированные модули маршрутов, клиентский пакет в `__nexy__/client/` и предварительно обработанный HTML для маршрутов платформы. Скопируйте проект — исходный код плюс `__nexy__/` — или создайте его внутри образа.

## Docker

На этапе сборки необходим Node (для Vite) и Python (для компилятора). На этапе выполнения требуется только Python.

```dockerfile filename="Докерфайл"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

`uv` извлекает управляемый Python, когда в базовом образе его нет, поэтому этап сборки может начаться с образа узла.

## За обратным прокси

Запустите `nx start` на локальном хосте и позвольте Nginx, Caddy или прокси-серверу платформы завершить TLS:

```bash
nx start --host 127.0.0.1 --port 8000
```

Убедитесь, что прокси-сервер пересылает обновления WebSocket, если вы используете обработчики `SOCKET`, и что он пересылает исходный хост — FastAPI создает из него абсолютные URL-адреса.

## Проверка здоровья

<!-- router:fbr,custom -->
Добавьте файл-обработчик `src/routes/api/health.py` и проверьте `/api/health` — вместо страницы, которая может отображаться медленно:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
Добавьте контроллер и проверьте `/health/` — вместо представления, которое может отображаться медленно:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

Перечислите его в `controllers` корневого модуля.
<!-- /router -->

### Встроенные конечные точки

Балансировщик нагрузки или Kubernetes задает два вопроса: активен ли процесс и может ли он получать трафик? Установите `useHealth` и Nexy отвечает оба, без файла-обработчика и без контроллера:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useHealth = True
```

| Конечная точка | Ответы 200 | Ответы 503 |
|---|---|---|
| `GET /health/live` | пока процесс отвечает | никогда |
| `GET /health/ready` | как только приложение запустится | пока он запускается, и как только сервер попросит его остановиться |

Nexy гарантирует, что `/health/ready` следует за запуском и завершением работы сервера.

Nexy гарантирует, что обе конечные точки останутся вне журнала доступа и схемы OpenAPI.

Nexy гарантирует, что обе конечные точки ответят до `useTrustedHost` и `useHTTPSRedirect`, поэтому зонд, отправленный по HTTP на адрес модуля, не будет отклонен.

По соглашению вы держите свои собственные маршруты отключенными от `/health/live` и `/health/ready`, пока `useHealth` включен: конечные точки Nexy отвечают первыми. `useHealth` по умолчанию равен `False`, поэтому проект, в котором он не установлен, сохраняет оба пути.

Ваше приложение отвечает за проверку того, от чего оно зависит: `/health/ready` сообщает о жизненном цикле сервера, а не о состоянии базы данных.

Направьте на них зонды Kubernetes `Deployment`:

```yaml filename="k8s/deployment.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: registry.example.com/app:1.0
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            periodSeconds: 5
```

## Статический хостинг

Каждая страница представляет собой HTML, но Nexy предполагает наличие сервера для маршрутизации и обработчиков API.

> [!NOTE]
> режима сборки `--static` нет. Чисто статический экспорт должен быть сгенерирован в вашем конвейере из вывода `nx build`.

## Контрольный список

- [ ] `nx build` в CI нет предупреждений для маршрутов, которые вы планируете отображать на сервере.
- [ ] `nx start` завершается с кодом 1 и ничего не запускает, если файл маршрута не может загрузиться
- [ ] `NEXY_ACTION_SECRET` установлено или `__nexy__/action.key` сохраняется вместе со сборкой
- [ ] `useDocs = False` в производстве, если схема API не должна быть общедоступной
- [ ] `useTrustedHost` и `useHTTPSRedirect` установлены для публичного развертывания.
- [ ] `useHealth = True` когда балансировщик нагрузки или Kubernetes проверяет приложение
- [ ] `__nexy__/` не зафиксировано

## Следующие шаги

- [Конфигурация](../reference/config.md): HTTPS, доверенные хосты, сеансы.
- [Фронтенд](../guides/frontend.md): что строит Vite
- [Тестирование](../guides/testing.md): команды для запуска в CI
