# Solid

Nexy отображает компоненты Solid 1.9 на сервере, а затем Solid переносит их в браузер. Страницы, макеты, острова и действия одинаковы в каждой платформе: на этой странице рассказывается о настройке, а затем о частях, которые отличаются от [общих контрактов](../frontend/pages.md).

| Режим | `nexyconfig.py` | Страницы — | Solid — |
|---|---|---|---|
| Сервер (по умолчанию) | `useCSR = False` | `.nexy` файлы | [острова](../../rendering/islands.md) внутри этих страниц |
| Клиент | `useCSR = True` | `.tsx` файлы | всей страницы с [макетами](../frontend/layouts.md) и клиентским маршрутизатором |

## Начать проект

```bash
nx new my-app --template web-fbr-solid
```

Шаблон представляет собой серверный проект с Solid островами. Вместо этого запустите `nx new my-app` без шаблона, чтобы ответить на запросы: маршрутизатор, тип проекта, использовать ли маршрутизацию на стороне клиента, а затем структуру.

## Включить Solid в существующем проекте

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

В клиентском режиме напишите `solid({ ssr: true })`: Solid компилирует компонент по-разному для сервера и для браузера, а в клиентском режиме требуется и то, и другое. `nx new` записывает этот файл; Nexy пишет `__nexy__/vite.ts` сам, поэтому не редактируйте его.

| Пакет | Версия `nx new` записывает |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (зависимость от разработчиков) |

## Думайте сигналами

Функция компонента Solid выполняется **один раз**. То, что меняется позже, считывается через сигнал, и обновляются только выражения, которые его читают:

```tsx filename="src/компоненты/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- Вызовите сигнал `count()` внутри JSX, а не в переменной над ним.
- Прочитайте реквизит как `props.start`. Деструктуризация `{ start }` считывает значение один раз и теряет обновления.
- Solid записывает атрибуты HTML: `class`, `for`, `charset`, а не `className`.

## Правила

- **Один фреймворк на проект.** `useFF` требуется ровно один фреймворк; `useFF = [solid(), react()]` останавливает сервер при запуске. При использовании `useFF = solid()` каждый файл `.tsx` является Solid.
- **Страницы являются `.tsx`.** Только файл `.tsx` под `src/routes/` становится страницей; `.jsx` подходит для компонента.
- **Компоненты находятся за пределами `src/routes/`**, обычно в `src/components/`, поэтому они не являются страницами.
- **У проекта в режиме сервера нет страницы `.tsx`**, а у проекта в режиме клиента нет страницы `.nexy`: Nexy отказывается запускаться и присваивает файлу имя. См. [режимы](../../routing/fbr/modes.md).
- **Нет `.mdx` с Solid.** MDX компилируется в React или Preact; `.md` страницы работают.

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

Параметры URL доступны через хук `useParams`, который возвращает метод доступа:

```tsx filename="src/маршруты/блог/[слизень].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## Макеты

### Реализация

Корневой макет определяет оболочку документа. Вложенные макеты оборачивают содержимое.

```tsx filename="src/маршруты/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

Не деструктурируйте `props.children`, поскольку Solid читает его лениво.

## Острова

В режиме сервера компонент Solid, импортированный в файл `.nexy`, является островом.

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

Используйте перехватчик `useAction` для управления состоянием вызова действия. В Solid это возвращает средства доступа (назовите их как функции).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
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

Все хуки местоположения возвращают средства доступа:

- `usePathname()`: текущий путь
- `useParams()`: динамические сегменты
- `useSearchParams()`: строка запроса
- `useLocation()`: объект с полным местоположением

## Следующие шаги

- [Просмотры](../README.md): сравнение форматов, которые может использовать страница.
- [Frontend](../../guides/frontend.md): Vite и клиентская сборка
