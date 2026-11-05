# Vue

Nexy отображает Vue 3 однофайловых компонента на сервере, затем Vue обрабатывает их в браузере. Страницы, макеты, острова и действия одинаковы в каждой платформе: на этой странице рассказывается о настройке, а затем о частях, которые отличаются от [общих контрактов](../frontend/pages.md).

| Режим | `nexyconfig.py` | Страницы — | Vue — |
|---|---|---|---|
| Сервер (по умолчанию) | `useCSR = False` | `.nexy` файлы | [острова](../../rendering/islands.md) внутри этих страниц |
| Клиент | `useCSR = True` | `.vue` файлы | всей страницы с [макетами](../frontend/layouts.md) и клиентским маршрутизатором |

## Начать проект

```bash
nx new my-app --template web-fbr-vue
```

Шаблон представляет собой серверный проект с Vue островами. Вместо этого запустите `nx new my-app` без шаблона, чтобы ответить на запросы: маршрутизатор, тип проекта, использовать ли маршрутизацию на стороне клиента, а затем структуру.

## Включить Vue в существующем проекте

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` записывает этот файл; Nexy пишет `__nexy__/vite.ts` сам, поэтому не редактируйте его.

| Пакет | Версия `nx new` записывает |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## Правила

- **Один фреймворк на проект.** `useFF` требуется ровно один фреймворк; `useFF = [vue(), react()]` останавливает сервер при запуске.
- **Один компонент на файл.** Файл `.vue` экспортирует свой компонент по умолчанию; имя, под которым вы его импортируете, — это только тег, который вы пишете.
- **Компоненты находятся вне `src/routes/`**, обычно в `src/components/`, поэтому они не являются страницами.
- **У проекта в режиме сервера нет страницы `.vue`**, а у проекта в режиме клиента нет страницы `.nexy`: Nexy отказывается запускаться и присваивает файлу имя. См. [режимы](../../routing/fbr/modes.md).

## Страницы

В режиме клиента (`useCSR = True`) страница представляет собой файл `.vue`.

### Компонент страницы

Страница — это компонент, определенный блоком `<script setup>`.

```vue filename="src/маршруты/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### Динамические сегменты

Параметры URL-адреса попадают на страницу в качестве реквизита. Вы можете объявить их, используя `defineProps`:

```vue filename="src/маршруты/блог/[слизень].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Альтернативно, используйте перехватчик `useParams` из `@nexy/client` в любом компоненте.

## Макеты

### Реализация

Корневой макет определяет оболочку документа. Вложенные макеты помещают содержимое в слот по умолчанию.

```vue filename="src/маршруты/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

## Острова

В режиме сервера компонент Vue, импортированный в файл `.nexy`, является островом.

### Импорт

Импортируйте компоненты в начале файла `.nexy`:

```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/Counter.vue" import Counter
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

Используйте перехватчик `useAction` для управления состоянием вызова действия. В Vue возвращаемое состояние (`pending`, `data`, `error`) — это вычисляемые ссылки.

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### Навигация

Используйте компонент `Link` для переходов на стороне клиента:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

Для программной навигации используйте хук `useRouter`:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL-доступ

Все хуки местоположения возвращают вычисленные ссылки:

- `usePathname()`: текущий путь
- `useParams()`: динамические сегменты
- `useSearchParams()`: строка запроса
- `useLocation()`: объект полного местоположения

## Следующие шаги

- [Просмотры](../README.md): сравнение форматов, которые может использовать страница.
- [Фронтенд](../../guides/frontend.md): Vite и клиентская сборка
