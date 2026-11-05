# React

Nexy отображает React 19 компонентов на сервере, затем React гидратирует их в браузере. Страницы, макеты, острова и действия одинаковы в каждой платформе: на этой странице рассказывается о настройке, а затем о частях, которые отличаются от [общих контрактов](../frontend/pages.md).

| Режим | `nexyconfig.py` | Страницы — | React — |
|---|---|---|---|
| Сервер (по умолчанию) | `useCSR = False` | `.nexy` файлы | [острова](../../rendering/islands.md) внутри этих страниц |
| Клиент | `useCSR = True` | `.tsx` файлы | всей страницы с [макетами](../frontend/layouts.md) и клиентским маршрутизатором |

## Начать проект

```bash
nx new my-app --template web-fbr-react
```

Шаблон представляет собой серверный проект с React островами. Вместо этого запустите `nx new my-app` без шаблона, чтобы ответить на запросы: маршрутизатор, тип проекта, использовать ли маршрутизацию на стороне клиента, а затем структуру.

## Включить React в существующем проекте

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` записывает этот файл; Nexy пишет `__nexy__/vite.ts` сам, поэтому не редактируйте его.

| Пакет | Версия `nx new` записывает |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | зависимости от разработчиков |

## Правила

- **Один фреймворк на проект.** `useFF` требуется ровно один фреймворк; `useFF = [react(), vue()]` останавливает сервер при запуске.
- **Страницы — это `.tsx`.** React владеет `.tsx` и `.jsx` для компонентов, но только файл `.tsx` под `src/routes/` становится страницей.
- **Компоненты находятся вне `src/routes/`**, обычно в `src/components/`, поэтому они не являются страницами.
- **У проекта в режиме сервера нет страницы `.tsx`**, а у проекта в режиме клиента нет страницы `.nexy`: Nexy отказывается запускаться и присваивает файлу имя. См. [режимы](../../routing/fbr/modes.md).

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

Корневой макет определяет оболочку документа. Вложенные макеты оборачивают содержимое под ними.

```tsx filename="src/маршруты/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

## Острова

В режиме сервера компонент React, импортированный в файл `.nexy`, является островом.

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

Используйте компонент `Link` для переходов на стороне клиента:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
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
- [Frontend](../../guides/frontend.md): Vite и клиентская сборка
