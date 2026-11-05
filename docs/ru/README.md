# Документация Некси

**Python Фреймворк для полнофункциональных веб-приложений.**

Nexy — это связующее звено между серверной частью Python и интерфейсом браузера. Вместо двух серверов, двух систем сборки и двух таблиц маршрутов вы получаете один источник: FastAPI и Starlette обслуживают приложение, Vite собирает клиент, а файл под `src/routes/` — это маршрут — `.nexy` — страница, `.py` — обработчик API.

- **Python в первую очередь.** Страницы, конечные точки, формы и действия — это Python, а страница, отображаемая на сервере, не нуждается в интерфейсной платформе.
- **Три маршрутизатора, одна интеграция.** Файловый, модульный или существующий FastAPI `APIRouter`.
- **Интерфейс, когда он вам нужен.** React, Vue, Svelte, Solid или Preact, на страницу в виде островов или для всего проекта в клиентском режиме.
- **Рендеринг, одна модель.** Рендеринг сервера, кэшированные страницы и острова определяются для каждой страницы; маршрутизация клиента — это переключатель проекта.
- **Типизированные действия.** Сообщение формы и типизированный вызов клиента достигают одной и той же функции Python.

Начните с одного файла в папке `src/routes/` и добавляйте структуру по мере роста проекта.

## Начало работы

### Первые шаги
| Страница | Что вы будете делать |
|---|---|
| [Установка](getting-started/installation.md) | Установите uv и Nexy CLI, затем создайте свой первый проект |
| [Быстрый старт](getting-started/quick-start.md) | Создайте проект, запустите его с оперативной перезагрузкой и соберите для производства |
| [Учебное пособие](getting-started/tutorial.md) | Создайте страницу заметок с конечной точкой, общими данными и рабочей сборкой за 10 минут |

### Понять модель
| Страница | Что вы будете делать |
|---|---|
| [Основные понятия](getting-started/core-concepts.md) | Получите мысленную модель: маршрут, страница, представление, компонент, обработчик, конечная точка |
| [Как работает Nexy](getting-started/how-nexy-works.md) | Переходите по одному запросу от URL-адреса к файлу, который на него отвечает |
| [Архитектура](architecture.md) | Знайте, какой уровень что делает и что Nexy оставляет вашему приложению |
| [Структура проекта](getting-started/project-structure.md) | Знайте, для чего предназначена каждая папка и файл в проекте |
| [Выберите маршрутизатор](routing/README.md) | Выберите файловый, модульный или специальный маршрутизатор |
| [Выберите формат просмотра](views/README.md) | Выберите `.nexy`, Markdown или клиентскую платформу для страницы |

### Приезжая из другого места
| Страница | Что вы будете делать |
|---|---|
| [Из другого фреймворка](getting-started/coming-from-other-frameworks.md) | Переведите FastAPI, Next.js и выразите привычки в Nexy |

## Маршрутизация

### На основе файлов {fbr}
| Страница | Что вы будете делать |
|---|---|
| [Маршрутизация на основе файлов](routing/fbr/README.md) | Преобразование пути к файлу в URL-адрес |
| [Страницы](routing/fbr/pages/README.md) | Написать страницу |
| [Динамические маршруты](routing/fbr/pages/dynamic-routes.md) | Используйте `[slug]`, `[...path]` и группы маршрутов |
| [Метаданные страницы](routing/fbr/pages/metadata.md) | Установите заголовок, описание и поделитесь изображением страницы {new} |
| [Макеты](routing/fbr/layouts/README.md) | Совместное использование кадра между страницами |
| [Наследование](routing/fbr/inheritance.md) | Чтение порядка разрешения макетов, зависимостей и страниц ошибок |
| [Режим сервера и режим клиента](routing/fbr/modes.md) | `useCSR`, и что позволяет каждый режим |
| [Связывание и навигация](routing/fbr/navigation/linking-and-navigating.md) | Связывание страниц, навигация по клиенту, предварительная загрузка |
| [Хуки](routing/fbr/navigation/hooks.md) | Чтение пути, запроса, файлов cookie и сеанса |

### Обработчики и ошибки {fbr}
| Страница | Что вы будете делать |
|---|---|
| [Обработчики маршрутов](routing/fbr/handlers/README.md) | Добавьте конечную точку Python |
| [Проверка и ошибки](routing/fbr/handlers/validation-and-errors.md) | Ответьте на `422` и `404` и поднимите `HTTPException` |
| [WebSocket обработчики](routing/fbr/realtime/websocket.md) | Обработка соединения `SOCKET` |
| [Зависимости и меры защиты](routing/fbr/dependencies/README.md) | Запускайте `dependencies.py` перед обработчиком и наследуйте его |
| [Файлы промежуточного программного обеспечения](routing/fbr/middleware/README.md) | Обертывание запросов с помощью `middleware.py`, наследуемых каталогом |
| [Страницы ошибок](routing/fbr/errors/README.md) | Ответьте с ошибками `notfound.nexy`, `errors.nexy` и JSON |
| [Страницы с ошибками в папке](routing/fbr/errors/folder-pages.md) | Крайний регистр: ошибки из подпапок |

### Модульный маршрутизатор {modular}
Контроллеры и модули.
| Страница | Что вы будете делать |
|---|---|
| [Модульная маршрутизация](routing/modular/README.md) | Монтаж контроллеров и модулей |
| [Внедрение зависимостей](routing/modular/dependency-injection.md) | Определите сервисы, их области действия и контейнер |
| [Охрана и метаданные](routing/modular/guards-and-metadata.md) | Защищайте и документируйте маршруты |
| [Модульный маршрутизатор против NestJS](routing/modular/vs-nestjs.md) | Сравнение с NestJS |

### Интеграция пользовательского маршрутизатора {custom}
| Страница | Что вы будете делать |
|---|---|
| [Пользовательская маршрутизация](routing/custom/README.md) | Включение существующего FastAPI приложения |

## Фронтенд

### Совместные контракты
| Страница | Что она определяет |
|---|---|
| [Страницы интерфейса](views/frontend/pages.md) | Один файл, один маршрут: реквизит, рендеринг, метаданные |
| [Макеты внешнего интерфейса](views/frontend/layouts.md) | Оболочка документа, вложение и то, чего не может макет |
| [Действия и навигация](views/frontend/actions-and-navigation.md) | Вызов набранного действия, ссылка на страницы, чтение URL |

### Некси просмотры
| Страница | Что вы будете делать |
|---|---|
| [файлы .nexy](views/nexy/README.md) | Напишите страницу с Python, Jinja2 и реквизитами |
| [Компоненты](views/nexy/components.md) | Используйте `Image`, `Link`, `Audio`, `Video` и `Import` |
| [layout.nexy](views/nexy/layouts.md) | Напишите макет режима сервера |
| [Markdown и MDX](views/nexy/markdown.md) | Написание страниц контента |

### Различия в фреймворках
| Страница | Что меняется |
|---|---|
| [React различия](views/react/differences.md) | Компоненты, хуки и `layout.tsx` {new} |
| [Vue различия](views/vue/differences.md) | SFC, ссылки и `layout.vue` {new} |
| [Svelte различия](views/svelte/differences.md) | Руны, магазины и `layout.svelte` {new} |
| [Solid различия](views/solid/differences.md) | Сигналы, средства доступа и `layout.tsx` {new} |
| [Preact различия](views/preact/differences.md) | Хуки, сигналы и `layout.tsx` {new} |

## Рендеринг

### Режимы
| Страница | Ваше решение |
|---|---|
| [Рендеринг](rendering/README.md) | Какой режим рендеринга подходит для страницы |
| [SSR](rendering/ssr.md) | Серверный рендеринг, по умолчанию |
| [ISR](rendering/isr.md) | Кэшировать страницы с устаревшей повторной проверкой |
| [CSR](rendering/csr.md) | Маршрутизация на стороне клиента |
| [Острова](rendering/islands.md) | Гидратация при простое, видимом или медиа-запросе |

## Путеводители

### Формы и данные
| Страница | Что вы будете делать |
|---|---|
| [Действия](guides/actions.md) | Вызов функции Python из формы или типизированной функции TypeScript |
| [Базы данных](guides/databases.md) | Выберите ORM и запустите миграцию |

### Безопасность и развертывание
| Страница | Что вы будете делать |
|---|---|
| [Промежуточное ПО и безопасность](guides/middleware-and-security.md) | Настройка CORS, GZip, доверенных хостов и сеансов |
| [Развертывание](deployment/README.md) | Сборка, контейнеризация и обслуживание |
| [Производительность](deployment/performance.md) | Измерение и настройка значений по умолчанию |

### Сборка и тестирование
| Страница | Что вы будете делать |
|---|---|
| [Vite и стиль](guides/frontend.md) | Настройка Vite, стиль и сборка клиента |
| [Тестирование](guides/testing.md) | Тестирование с помощью pytest, `TestClient` и vitest |

### Инструменты и помощь
| Страница | Что вы будете делать |
|---|---|
| [Панель инструментов разработчика](guides/devtools.md) | Используйте панель инструментов `nexy dev` и отключите ее |
| [Агенты кодирования](guides/ai-agents.md) | Дайте Claude Code, Codex и OpenCode правила вашего проекта |
| [Устранение неполадок](guides/troubleshooting.md) | Устранение первых проблем, с которыми сталкиваются люди |

## Ссылка

### Команды и конфигурация
| Страница | Что на ней перечислено |
|---|---|
| [CLI](reference/cli.md) | Команды, флаги, подсказки и коды выхода |
| [Config](reference/config.md) | Каждое поле `nexyconfig.py` и его значение по умолчанию |

### Python API и ошибки
| Страница | Что на ней перечислено |
|---|---|
| [Python API](reference/python-api.md) | Каждое имя, экспортируемое Nexy, по модулю |
| [Исключения и ошибки](reference/exceptions.md) | Каждый сбой, его статус и файл, который на него отвечает |

### Соглашения и концепции
| Страница | Что вы будете делать |
|---|---|
| [Соглашения о файлах](reference/file-conventions.md) | Зарезервированные файлы и правила маршрутизации |
| [Глоссарий](reference/glossary.md) | Слова, используемые в этих документах |
| [Безопасность](reference/security.md) | Этажи версий, правила, которым следует Nexy, аудиты |

## Макет
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## Расширенный

### Расширенный {advanced}

| Страница | Что вы будете делать |
|---|---|
| [Обновление до версии 2.2](getting-started/upgrading.md) | Переход с версии 2.1 на 2.2 |
| [Интернационализация (i18n)](guides/i18n.md) | Добавьте переводы с выбранной вами библиотекой |
| [Рецепты](guides/recipes.md) | Примеры и шаблоны, а не руководство |

*Эти страницы не являются частью пути чтения по умолчанию. Ссылка «Вся документация» позволяет увидеть все.*
