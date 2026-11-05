# Preact

Nexy отображает Preact 10 компонентов на сервере, затем Preact обрабатывает их в браузере. Страницы, макеты, острова и действия одинаковы в каждой платформе: на этой странице рассказывается о настройке, а затем о частях, которые отличаются от [общих контрактов](../frontend/pages.md).

| Режим | `nexyconfig.py` | Страницы — | Preact — |
|---|---|---|---|
| Сервер (по умолчанию) | `useCSR = False` | `.nexy` файлы | [острова](../../rendering/islands.md) внутри этих страниц |
| Клиент | `useCSR = True` | `.tsx` файлы | всей страницы с [макетами](../frontend/layouts.md) и клиентским маршрутизатором |

## Начать проект

```bash
nx new my-app --template web-fbr-preact
```

Шаблон представляет собой серверный проект с Preact островами. Вместо этого запустите `nx new my-app` без шаблона, чтобы ответить на запросы: маршрутизатор, тип проекта, использовать ли маршрутизацию на стороне клиента, а затем структуру.

## Включить Preact в существующем проекте

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` записывает этот файл; Nexy пишет `__nexy__/vite.ts` сам, поэтому не редактируйте его.

| Пакет | Версия `nx new` записывает |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (зависимость от разработчиков) |
| `preact-render-to-string` | `^6.7.0` (зависимость от разработчиков, рендеринг на сервере) |

## Напишите Preact

Компонент Preact — это функция в стиле React. Отличия, которые здесь имеют значение:

```tsx filename="src/компоненты/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- Хуки происходят из `preact/hooks`, такие типы, как `ComponentChildren` из `preact`.
- Напишите атрибуты HTML: `class`, `for`, `charset`. `Link` считывает свои классы из `class`.

## Правила

- **Один фреймворк на проект.** `useFF` требуется ровно один фреймворк; `useFF = [preact(), react()]` останавливает сервер при запуске. При использовании `useFF = preact()` каждый файл `.tsx` является Preact.
- **Страницы являются `.tsx`.** Только файл `.tsx` под `src/routes/` становится страницей; `.jsx` подходит для компонента.
- **Компоненты находятся за пределами `src/routes/`**, обычно в `src/components/`, поэтому они не являются страницами.
- **Проект в режиме сервера не имеет страницы `.tsx`**, а проект в режиме клиента не имеет страницы `.nexy`: Nexy отказывается запускаться и присваивает файлу имя. См. [режимы](../../routing/fbr/modes.md).
- **Страница `.mdx` импортируется из `"preact"`.** Nexy компилирует файл `.mdx` с Preact только тогда, когда видит этот импорт, например `import { h } from "preact"`, и с React в противном случае. См. [Markdown и MDX](../nexy/markdown.md).

## Страницы

В режиме клиента (`useCSR = True`) страница представляет собой файл `.tsx`.

### Компонент страницы

Страница — это экспорт файла по умолчанию. Если экспорта по умолчанию не существует, Nexy выбирает первый названный экспорт.

```tsx filename="src/маршруты/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Динамические сегменты

Параметры URL доступны через хук `useParams`:

```tsx filename="src/маршруты/блог/[слизень].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Макеты

### Реализация

Корневой макет определяет оболочку документа. Вложенные макеты оборачивают содержимое.

```tsx filename="src/маршруты/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## Острова

В режиме сервера компонент Preact, импортированный в файл `.nexy`, является островом.

### Импорт

Импортируйте компоненты в начале файла `.nexy`:

```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/Counter.tsx" import Counter
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

Используйте хук `useAction` для управления состоянием вызова действия:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### Навигация

Используйте компонент `Link` для переходов на стороне клиента. Обратите внимание, что Preact использует `class` вместо `className`:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

Для программной навигации используйте хук `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL-доступ

- `usePathname()`: текущий путь
- `useParams()`: динамические сегменты
- `useSearchParams()`: строка запроса
- `useLocation()`: объект полного местоположения

## Следующие шаги

- [Просмотры](../README.md): сравнение форматов, которые может использовать страница.
- [Фронтенд](../../guides/frontend.md): Vite и клиентская сборка
