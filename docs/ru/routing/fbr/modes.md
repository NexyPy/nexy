# Режим сервера и режим клиента

Проект Nexy либо **отрисовывается на сервере** либо **маршрутизируется клиентом**, например, проект Next.js — это либо страницы, визуализируемые на сервере, либо клиентское приложение. `useCSR` в `nexyconfig.py` выбирает.

## Режим сервера (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- Страницы — это файлы `.nexy`, `.md` или `.mdx` в папке `src/routes/`.
- Корень `layout.nexy` владеет `<!DOCTYPE html>`, `<html>`, `<head>` и `<body>`.
- Клиентские компоненты (React, Vue, Svelte, Solid или Preact) разрешены как **острова**: вы импортируете один из них со страницы `.nexy` и он гидратируется в браузере. См. [Острова](../../rendering/islands.md).
- Клиентский компонент никогда не является маршрутом. Храните их в `src/components/`.
- Одна клиентская платформа за раз.

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## Клиентский режим (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- Страницы — это файлы вашей клиентской среды: `.tsx` для React, `.vue`, `.svelte`.
- Файлы `.md` и `.mdx` остаются действительными маршрутами: Nexy отображает их на сервере внутри макета клиента, и клиентский маршрутизатор берет на себя навигацию оттуда.
- Корневой макет любой платформы (`layout.tsx`, `layout.vue`, `layout.svelte`) владеет `<!DOCTYPE html>`, `<html>`, `<head>` и `<body>`, как и корневой макет Next.js App Router. Nexy визуализирует его в Node для первого ответа, а фреймворк гидратирует весь документ. См. [layout.tsx](../../views/react/differences.md).
- Файлы `.py` — это обработчики API, обслуживаемые FastAPI, рядом с клиентскими маршрутами.
- Файла `.nexy` вообще нет, как и `layout.nexy`.
- Навигация между страницами происходит в браузере.

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## Что отвергается

Nexy проверяет проект перед `nx dev`, `nx start` и `nx build` и останавливается на списке файлов:

| Режим | Отклонено | Сообщение |
|---|---|---|
| сервер | `.tsx`, `.jsx`, `.vue` или `.svelte` в разделе `src/routes/` | переместите компоненты в `src/components/` или установите `useCSR = True` |
| клиент | любой `.nexy` файл в `src/routes/` | запишите их как компоненты фреймворка или установите `useCSR = False` |
| обе | более одной внешней среды в `useFF` | `useFF must configure exactly one frontend framework` |
| клиент | `useRouter` (модульный маршрутизатор) | `useCSR requires file-based routing` |
| клиент | нет `useFF` | `useCSR requires a client framework` |

Эта проверка игнорирует файлы и папки, начинающиеся с `_` или `.`.

## Какой из них

- **Контент, маркетинг, документация, SEO-сайты**: серверный режим с островами.
- **Панели мониторинга и приложения с расширенной клиентской навигацией**: клиентский режим.
- **Python API с клиентским приложением сверху**: клиентский режим, с обработчиками `.py` рядом со страницами.

## Следующие шаги

- [Макеты](layouts/README.md)
- [Рендеринг](../../rendering/README.md)
- [Конфигурация](../../reference/config.md)
