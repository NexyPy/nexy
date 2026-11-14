# Документация Некси

**Python Фреймворк для полнофункциональных веб-приложений.**

Nexy объединяет ваши страницы и ваш API в один Python проект, обслуживаемый одним сервером. Версия 2.2 построена на FastAPI: каждый маршрут API представляет собой маршрут FastAPI, указанный в схеме OpenAPI, которую Scalar показывает в `/docs`.

- **Python первым.** Страницы, конечные точки, формы и действия — это Python, а страница не требует JavaScript.
- **Интерфейс, когда он вам нужен.** React, Vue, Svelte, Solid или Preact, для одного компонента или для всего сайта.
- **Один файл, один URL.** Файл в `src/routes/` — это маршрут: `.nexy` — страница, `.py` — конечная точка API.
- **Есть куда расти.** Начните с одного файла; перейдите к модулям или подключите существующий маршрутизатор FastAPI по мере роста проекта.

Впервые здесь? Прочтите [Что такое Nexy?](getting-started/what-is-nexy.md), затем [Быстрый старт](getting-started/quick-start.md).

## Начало работы

### Первые шаги
| Страница | Что ты будешь делать |
|---|---|
| [Что такое Некси?](getting-started/what-is-nexy.md) | Узнайте, что такое Nexy, на чем он построен и что вы получаете |
| [Установка](getting-started/installation.md) | Установите uv и Nexy CLI, затем создайте свой первый проект. |
| [Быстрый старт](getting-started/quick-start.md) | Создайте проект, запустите его с перезагрузкой в реальном времени и соберите для производства. |
| [Учебное пособие](getting-started/tutorial.md) | Создайте приложение для заметок шаг за шагом, по одной работающей части за раз. |

### Понять модель
| Страница | Что ты будешь делать |
|---|---|
| [Основные концепции](getting-started/core-concepts.md) | Получите ментальную модель: маршрут, страница, представление, компонент, обработчик, конечная точка. |
| [Структура проекта](getting-started/project-structure.md) | Знайте, для чего предназначена каждая папка и файл в проекте. |
| [Выберите роутер](routing/README.md) | Выберите файловый, модульный или индивидуальный маршрутизатор. |
| [Выберите формат просмотра](views/README.md) | Выберите `.nexy`, Markdown или клиентскую платформу для страницы. |

## Учебное пособие

### Блок 1: основы
| Страница | Что вы построите |
|---|---|
| [1. Создайте проект](tutorial/create-the-project.md) | Создайте проект заметок и запустите его в браузере. |
| [2. Страницы и макеты](tutorial/pages-and-layouts.md) | Добавьте страницу заметок и измените ее макет. |
| [3. Динамические маршруты и API](tutorial/dynamic-routes.md) | Дайте каждой заметке URL-адрес и подавайте заметки в формате JSON. |
| [4. Компоненты](tutorial/components.md) | Превратите каждую ноту в многоразовый компонент `.nexy` |

### Блок 2: данные
| Страница | Что вы построите |
|---|---|
| [5. Сохраните заметки в папке SQLite](tutorial/store-the-notes.md) | Добавьте модель, миграцию и начальное значение и прочитайте примечания из базы данных. |
| [6. Создайте заметку из формы](tutorial/create-a-note.md) | Опубликовать форму в действии, которое сохраняет заметку |
| [7. Показать ошибки проверки](tutorial/validation-errors.md) | Откажитесь от пустой заметки и скажите, почему, над формой. |
| [8. Редактировать и удалить заметку](tutorial/edit-and-delete.md) | Добавляйте формы, которые меняют и удаляют заметку |
| [9. Разбивка заметок на страницы](tutorial/paginate-the-notes.md) | Показывать пять заметок одновременно со ссылками между страницами. |

### Блок 3: пользователи
| Страница | Что вы построите |
|---|---|
| [10. Создайте учетную запись и войдите в нее](tutorial/accounts.md) | Зарегистрируйтесь, войдите и выйдите с помощью сеансового файла cookie. |
| [11. Дайте каждому пользователю свои заметки](tutorial/own-notes.md) | Привяжите каждую заметку к ее пользователю и охраняйте страницы, действия и API. |
| [12. Сброс забытого пароля по электронной почте](tutorial/password-reset.md) | Отправьте подписанную ссылку по электронной почте, которая работает один раз, в течение часа |

### Блок 4: интерактивность
| Страница | Что вы построите |
|---|---|
| [13. Ищите заметки по мере ввода](tutorial/search-the-notes.md) | Фильтруйте каждую заметку в браузере с помощью острова React |
| [14. Отметьте заметку без перезагрузки страницы](tutorial/tick-a-note.md) | Отметьте заметку как готовую с помощью формы, которую отправляют на место несколько строк JavaScript |

## Маршрутизация

### На основе файлов {fbr}
| Страница | Что ты будешь делать |
|---|---|
| [Маршрутизация на основе файлов](routing/fbr/README.md) | Превратите путь к файлу в URL-адрес |
| [Страницы](routing/fbr/pages/README.md) | Написать страницу |
| [Динамические маршруты](routing/fbr/pages/dynamic-routes.md) | Используйте `[slug]`, `[...path]` и группы маршрутов. |
| [Метаданные страницы](routing/fbr/pages/metadata.md) | Установите заголовок, описание и поделитесь изображением страницы {new} |
| [Макеты](routing/fbr/layouts/README.md) | Делитесь кадром между страницами |
| [Наследование](routing/fbr/inheritance.md) | Прочтите порядок разрешения макетов, зависимостей и страниц ошибок. |
| [Режим сервера и режим клиента](routing/fbr/modes.md) | `useCSR` и что позволяет каждый режим |
| [Связывание и навигация](routing/fbr/navigation/linking-and-navigating.md) | Связывание страниц, навигация по клиенту, предварительная загрузка |
| [Крючки](routing/fbr/navigation/hooks.md) | Прочитайте путь, запрос, файлы cookie и сеанс. |

### Обработчики и ошибки {fbr}
| Страница | Что ты будешь делать |
|---|---|
| [Обработчики маршрутов](routing/fbr/handlers/README.md) | Добавьте конечную точку Python |
| [Проверка и ошибки](routing/fbr/handlers/validation-and-errors.md) | Ответьте на `422` и `404` и поднимите `HTTPException` |
| [WebSocket обработчики](routing/fbr/realtime/websocket.md) | Обработка соединения `SOCKET` |
| [Зависимости и меры защиты](routing/fbr/dependencies/README.md) | Запустите `dependencies.py` перед обработчиком и наследуйте его. |
| [Файлы промежуточного программного обеспечения](routing/fbr/middleware/README.md) | Обернуть запросы с помощью `middleware.py`, наследуемого каталогом |
| [Страницы ошибок](routing/fbr/errors/README.md) | Ответьте с ошибками `notfound.nexy`, `errors.nexy` и JSON. |
| [Страниц ошибок в папке](routing/fbr/errors/folder-pages.md) | Пограничный случай: ошибки из подпапок |

### Модульный маршрутизатор {modular}
Контроллеры и модули.
| Страница | Что ты будешь делать |
|---|---|
| [Модульная маршрутизация](routing/modular/README.md) | Монтаж контроллеров и модулей |
| [Внедрение зависимостей](routing/modular/dependency-injection.md) | Определите сервисы, их области действия и контейнер. |
| [Охранники и метаданные](routing/modular/guards-and-metadata.md) | Защищайте и документируйте маршруты |
| [Модульный маршрутизатор против NestJS](routing/modular/vs-nestjs.md) | Сравнение с NestJS |

### Интеграция пользовательского маршрутизатора {custom}
| Страница | Что ты будешь делать |
|---|---|
| [Пользовательская маршрутизация](routing/custom/README.md) | Включить существующее приложение FastAPI |

## Фронтенд

### Совместные контракты
| Страница | Что он определяет |
|---|---|
| [Действия и навигация](views/frontend/actions-and-navigation.md) | Вызвать набранное действие, связать страницы, прочитать URL |
| [Получить данные в компоненте](views/frontend/fetch-data.md) | `useFetch`: прочитать JSON из маршрута, поделиться им, обновить его |

### Некси просмотры
| Страница | Что ты будешь делать |
|---|---|
| [файлы .nexy](views/nexy/README.md) | Напишите страницу с Python, Jinja2 и реквизитом. |
| [Компоненты](views/nexy/components.md) | Используйте `Image`, `Link`, `Audio`, `Video` и `Import` |

### Страницы и макеты в файлах {fbr,custom}
| Страница | Что он определяет |
|---|---|
| [Страницы внешнего интерфейса](views/frontend/pages.md) | Один файл, один маршрут: реквизит, рендеринг, метаданные |
| [Макеты внешнего интерфейса](views/frontend/layouts.md) | Оболочка документа, вложение и то, чего не может макет |
| [макет.nexy](views/nexy/layouts.md) | Напишите макет в режиме сервера |
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
| Страница | Что ты решишь |
|---|---|
| [Рендеринг](rendering/README.md) | Какой режим рендеринга подходит для страницы |
| [ССР](rendering/ssr.md) | Серверный рендеринг, по умолчанию |
| [Острова](rendering/islands.md) | Гидратация при простое, видимом или медиа-запросе |

### Режимы страниц файла {fbr,custom}
| Страница | Что ты решишь |
|---|---|
| [ISR](rendering/isr.md) | Кэшировать страницы с устаревшими при повторной проверке |
| [КСО](rendering/csr.md) | Маршрутизация на стороне клиента |

## Путеводители

### Формы и данные
| Страница | Что ты будешь делать |
|---|---|
| [Действия](guides/actions.md) | Вызов функции Python из формы или типизированной функции TypeScript |
| [Базы данных](guides/databases.md) | Выберите ORM и запустите миграцию |

### Безопасность и развертывание
| Страница | Что ты будешь делать |
|---|---|
| [Промежуточное ПО и безопасность](guides/middleware-and-security.md) | Настройте CORS, GZip, доверенные хосты и сеансы. |
| [Развернуть](deployment/README.md) | Создавайте, контейнеризируйте и обслуживайте |
| [Производительность](deployment/performance.md) | Измерьте и настройте параметры по умолчанию |

### Сборка и тестирование
| Страница | Что ты будешь делать |
|---|---|
| [Vite и стиль](guides/frontend.md) | Настройка Vite, стилизация и сборка клиента |
| [Тестирование](guides/testing.md) | Проверьте с помощью pytest, `TestClient` и vitest |

### Инструменты и помощь
| Страница | Что ты будешь делать |
|---|---|
| [Панель инструментов разработчика](guides/devtools.md) | Используйте панель инструментов `nexy dev` и отключите ее. |
| [Агенты кодирования](guides/ai-agents.md) | Дайте Claude Code, Codex и OpenCode правила вашего проекта. |
| [Устранение неполадок](guides/troubleshooting.md) | Исправляйте первые проблемы, с которыми сталкиваются люди |

## Базы данных

### Базы данных SQL
| Страница | Что ты будешь делать |
|---|---|
| [SQLite](databases/sqlite.md) | Используйте один файл, без сервера: движок, прагмы, миграции и тесты. |
| [PostgreSQL](databases/postgresql.md) | Подключайтесь к psycopg, используйте JSONB, массивы, поиск и обновления. |
| [Неон](databases/neon.md) | Используйте бессерверное PostgreSQL: объединенный хост, автоприостановку и ветки. |
| [MySQL и MariaDB](databases/mysql-mariadb.md) | Подключитесь к pymysql, используйте utf8mb4, upserts и полнотекстовый поиск. |

## Исходя из

Те же задачи, написанные в знакомом вам фреймворке, а затем в Nexy.

### Обзор
| Страница | Что ты будешь делать |
|---|---|
| [Исходя из другого фреймворка](getting-started/coming-from-other-frameworks.md) | Переведите FastAPI, Next.js и выразите привычки на Nexy |

### Python фреймворки {fbr}
| Страница | Что ты будешь делать |
|---|---|
| [От FastAPI](coming-from/fastapi.md) | Сохраните свой код FastAPI: только `@app.get` станет файлом |
| [От Flask](coming-from/flask.md) | Превратите представления, чертежи, шаблоны и формы в маршруты Nexy |
| [От Django](coming-from/django.md) | Сопоставление представлений, шаблонов, моделей, форм и настроек с Nexy |

### JavaScript бэкэнды {fbr}
| Страница | Что ты будешь делать |
|---|---|
| [Из экспресса](coming-from/express.md) | Преобразование маршрутов, промежуточного программного обеспечения и `req`/`res` в обработчики Python |
| [Из Fastify](coming-from/fastify.md) | Превратите схемы, плагины и перехватчики в модели, папки и файлы. |
| [Из Элизии](coming-from/elysia.md) | Сопоставьте схемы `t`, охранников и Эдем с Pydantic и типизированными действиями. |
| [Из Хоно](coming-from/hono.md) | Сопоставьте маршруты, промежуточное программное обеспечение и клиент `hc` с Nexy |

### Fullstack-фреймворки {fbr}
| Страница | Что ты будешь делать |
|---|---|
| [От Next.js](coming-from/nextjs.md) | Сохраните свои страницы React и переместите код сервера в Python |
| [От Remix](coming-from/remix.md) | Превратите загрузчики и действия в Python обработчики и действия. |
| [Из Нукста](coming-from/nuxt.md) | Сохраните свои страницы Vue и переместите `server/` на Python |
| [Из SvelteKit](coming-from/sveltekit.md) | Сохраните свои страницы Svelte и переместите нагрузки, действия и хуки на Python |
| [От Astro](coming-from/astro.md) | Запишите Astro страниц как `.nexy` страниц с теми же островами. |
| [Из Ларавеля](coming-from/laravel.md) | Сопоставление маршрутов, контроллеров, Blade, Eloquent и очередей в Nexy |
| [Из Ruby on Rails](coming-from/rails.md) | Сопоставление маршрутов, контроллеров, ERB, Active Record и заданий с Nexy |

### Фреймворки контроллера {modular}
| Страница | Что ты будешь делать |
|---|---|
| [От NestJS](coming-from/nestjs.md) | Переместите контроллеры, модули, провайдеры и охранники на модульный маршрутизатор. |
| [Из Spring Boot](coming-from/spring-boot.md) | Переместите контроллеры, сервисы и фильтры на модульный маршрутизатор. |

## Ссылка

### Команды и конфигурация
| Страница | Что он перечисляет |
|---|---|
| [Интерфейс командной строки](reference/cli.md) | Команды, флаги, подсказки и коды выхода |
| [Конфигурация](reference/config.md) | Каждое поле `nexyconfig.py` и его значение по умолчанию. |

### Python API и ошибки
| Страница | Что он перечисляет |
|---|---|
| [Python API](reference/python-api.md) | Каждое имя, экспортируемое Nexy, по модулю |
| [Исключения и ошибки](reference/exceptions.md) | Каждый сбой, его статус и файл, который на него отвечает. |

### Соглашения о файлах {fbr,custom}
| Страница | Что ты будешь делать |
|---|---|
| [Соглашения о файлах](reference/file-conventions.md) | Зарезервированные файлы и правила маршрутизации |

### Соглашения и концепции
| Страница | Что ты будешь делать |
|---|---|
| [Глоссарий](reference/glossary.md) | Слова, которые используются в этих документах |
| [Безопасность](reference/security.md) | Этажи версий, правила, которым следует Nexy, аудиты |

## Макет
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
├─ coming-from/         one page per framework: FastAPI, Django, Express, Next.js...
├─ databases/           one page per database: SQLite, PostgreSQL, Neon, MySQL
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

| Страница | Что ты будешь делать |
|---|---|
| [Как работает Nexy](getting-started/how-nexy-works.md) | Посмотрите, что происходит между файлом и страницей и что оставляет вам Nexy |
| [Обновление до версии 2.2](getting-started/upgrading.md) | Миграция с 2.1 на 2.2 |
| [Интернационализация (i18n)](guides/i18n.md) | Добавляйте переводы с помощью библиотеки по вашему выбору |
| [Рецепты](guides/recipes.md) | Примеры и шаблоны, а не учебник |

*Эти страницы не являются частью пути чтения по умолчанию. Ссылка «Вся документация» позволяет увидеть все.*
