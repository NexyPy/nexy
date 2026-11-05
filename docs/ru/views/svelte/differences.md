# Svelte

Nexy отображает Svelte 5 компонентов на сервере, затем Svelte обрабатывает их в браузере. Страницы, макеты, острова и действия одинаковы в каждой платформе: на этой странице рассказывается о настройке, а затем о частях, которые отличаются от [общих контрактов](../frontend/pages.md).

| Режим | `nexyconfig.py` | Страницы — | Svelte — |
|---|---|---|---|
| Сервер (по умолчанию) | `useCSR = False` | `.nexy` файлы | [острова](../../rendering/islands.md) внутри этих страниц |
| Клиент | `useCSR = True` | `.svelte` файлы | всей страницы с [макетами](../frontend/layouts.md) и клиентским маршрутизатором |

## Начать проект

```bash
nx new my-app --template web-fbr-svelte
```

Шаблон представляет собой серверный проект с Svelte островами. Вместо этого запустите `nx new my-app` без шаблона, чтобы ответить на запросы: маршрутизатор, тип проекта, использовать ли маршрутизацию на стороне клиента, а затем структуру.

## Включить Svelte в существующем проекте

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` записывает этот файл; Nexy пишет `__nexy__/vite.ts` сам, поэтому не редактируйте его.

| Пакет | Версия `nx new` записывает |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## Правила

- **Svelte 5.** В компонентах используются руны: `$props()`, `$state()` и фрагменты для детей.
- **Один фреймворк на проект.** `useFF` требуется ровно один фреймворк; `useFF = [svelte(), vue()]` останавливает сервер при запуске.
- **Один компонент на файл.** Имя, под которым вы импортируете файл `.svelte` — это только тег, который вы пишете.
- **Компоненты находятся вне `src/routes/`**, обычно в `src/components/`, поэтому они не являются страницами.
- **Проект в режиме сервера не имеет страницы `.svelte`**, а проект в режиме клиента не имеет страницы `.nexy`: Nexy отказывается запускаться и присваивает файлу имя. См. [режимы](../../routing/fbr/modes.md).

## Страницы

В клиентском режиме (`useCSR = True`) страница представляет собой файл `.svelte`.

### Компонент страницы

Страница — это компонент, определенный блоком сценария файла `.svelte`.

```svelte filename="src/маршруты/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### Динамические сегменты

Параметры URL-адреса попадают на страницу в качестве реквизита через руну `$props()`:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Альтернативно, используйте хранилище `$params` из `@nexy/client` в любом компоненте.

## Макеты

### Реализация

Корневой макет определяет оболочку документа. Вложенные макеты оборачивают содержимое с помощью фрагмента `children`.

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## Острова

В режиме сервера компонент Svelte, импортированный в файл `.nexy`, является островом.

### Импорт

Импортируйте компоненты в начале файла `.nexy`:

```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<Counter start=3 />
```

### Директивы по гидратации

Используйте реквизит `directive` для управления моментом гидратации острова:

- `client:load` (по умолчанию): немедленно
- `client:idle`: когда браузер бездействует
- `client:visible`: когда он прокручивается в поле зрения
- `client:media`: когда медиа-запрос соответствует

## Действия и навигация

### Вызов действий

Используйте перехватчик `useAction` для управления состоянием вызова действия. В Svelte возвращается хранилище (читается с помощью `$`).

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### Навигация

Используйте компонент `Link` для переходов на стороне клиента:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

Для программной навигации используйте объект `router` из `@nexy/client`:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### URL-доступ

Все данные о местоположении предоставляются в виде магазинов:

- `$pathname`: текущий путь
- `$params`: динамические сегменты
- `$searchParams`: строка запроса
- `$location`: объект полного местоположения

## Следующие шаги

- [Просмотры](../README.md): сравнение форматов, которые может использовать страница.
- [Frontend](../../guides/frontend.md): Vite и клиентская сборка
