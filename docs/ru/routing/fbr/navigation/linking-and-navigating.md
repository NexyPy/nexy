# Связывание и навигация

При маршрутизации клиента (`useCSR = True`) ссылка между двумя страницами меняет местами страницу в браузере вместо перезагрузки документа. Макеты сохраняют свое состояние.

## Простые ссылки уже работают

Каждая `<a href>` страница вашего проекта перемещается по клиенту без каких-либо компонентов и маркеров:

```html
<a href="/about">About</a>
```

Ссылка остается в браузере и загружает страницу нормально, если:

- зажата клавиша-модификатор или кнопка не основная;
- он имеет `target` (кроме `_self`), `download`, `rel="external"` или `data-nexy-reload`;
- `href` — это другой источник, ссылка `mailto:` или `tel:` или только `#fragment`;
- путь не соответствует ни одному клиентскому маршруту, поэтому сервер отвечает на него.

## `Link`

`Link` — это тот же якорь, чего не может сделать простой: его `href` проверяется по вашим маршрутам, он нагревает целевую страницу и знает, когда он указывает на текущую страницу. Nexy генерирует `Link` вашего фреймворка в `__nexy__/src` при запуске `nx dev` или `nx build`.

| Рамочная основа | Импорт |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| Опора | Значение |
|---|---|
| `href` | Маршрут проекта (опечатка — это ошибка типа), опционально с `?query` или `#fragment` или внешний URL. |
| `replace` | Замените запись истории вместо ее добавления. |
| `scroll` | `false` сохраняет позицию прокрутки после навигации. По умолчанию: `true`. |
| `prefetch` | `'intent'` (по умолчанию) загружает страницу при наведении, фокусе или касании; `'viewport'` когда ссылка прокручивается в поле зрения; `false` никогда. |
| `activeClassName` | Добавляется в класс, когда ссылка указывает на текущую страницу или страницу под ней (`activeClass` в Vue и Svelte). |
| `exact` | Активен только на конкретной странице. |

Ссылка, указывающая на текущую страницу, также получает `aria-current="page"`.

## Крючки

Местоположение доступно в каждом фреймворке, в его идиоме. Во время первого этапа серверная часть обрабатывает ответ с URL-адресом запроса, поэтому страница гидратируется без несоответствий.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Путь | `usePathname()` | `usePathname()` возвращает метод доступа | `usePathname()` возвращает ссылку | `$pathname` магазин |
| Параметры маршрута | `useParams()` | `useParams()` аксессор | `useParams()` ссылка | `$params` магазин |
| Запрос | `useSearchParams()` | `useSearchParams()` аксессор | `useSearchParams()` ссылка | `$searchParams` магазин |
| все | `useLocation()` | `useLocation()` аксессор | `useLocation()` ссылка | `$location` магазин |
| Навигация | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| Навигация в полете | `useTransition()` | `useTransition()` аксессор | `useTransition()` ссылка | `useTransition()` магазин |
| Сопоставить путь | `useMatch(path?)` | `useMatch(path?)` аксессор | `useMatch(path?)` ссылка | `useMatch(path?)` магазин |
| Спросите перед отъездом | `useBlocker(dirty)` | `useBlocker(dirty())` в `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` в `$effect` |

Запрос представляет собой `URLSearchParams`. `useRouter()` и `router` дают `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` и `prefetch(href)`; `push` и `replace` принимают `{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## Показать состояние загрузки с помощью `useTransition`

`useTransition()` сообщает, работает ли клиентская навигация. `pending` — это `true` от щелчка до отображения следующей страницы, а `next` — это место, куда он направляется. Он возвращается к `{ pending: false, next: null }` после отображения страницы, когда навигация прекращается или когда ее заменяет более новая.

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## Сопоставьте путь с `useMatch`

`useMatch(path)` сообщает, соответствует ли `path` маршруту клиента. Он возвращает `{ match, found }`, где `match` содержит маршрут `file`, его `layouts` и его `params` или является `null`. Без пути он соответствует текущей странице и следует за каждой навигацией. Во время рендеринга сервера маршрутизатор еще не установлен, поэтому `match` — это `null`, а `found` — это `false`.

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## Перехватите страницу, которая терпит неудачу, с помощью `ErrorBoundary`

`ErrorBoundary` показывает запасной вариант вместо своих дочерних элементов, когда один из них выдает ошибку во время рендеринга в браузере. Резервный вариант получает ошибку и `reset`, который снова отображает дочерние элементы.

| Рамочная основа | Импорт | Резервный вариант |
|---|---|---|
| React, Preact, Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | функция `fallback`; дети идут в слот по умолчанию |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | фрагмент `fallback` |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

Не ловит:

- ошибка, возникшая позже, в обработчике событий, таймере или обещании: поймайте ее там, где она произойдет. Vue является исключением для собственных обработчиков событий, ошибки которых достигают границы;
- страница, которую маршрутизатор не может загрузить: вместо этого браузер запрашивает ее у сервера (см. [Что делает маршрутизатор](#what-the-router-does)).

## Спросите, прежде чем покинуть страницу с несохраненными изменениями.

`useBlocker(dirty, message?)` спрашивает посетителя, прежде чем он уйдет, пока `dirty` верно: ссылка, `router.push`, кнопки «Назад» и «Вперед», перезагрузка и закрытая вкладка. Клиентская навигация показывает `message` в `confirm()`: да продолжается, нет остается на странице. Перезагрузка или закрытие вкладки показывает собственный вопрос браузера, который не может сформулировать ни одна страница. Без сообщения вопрос "У вас есть несохраненные изменения. Покинуть эту страницу?".

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

Флаг читается там, где он меняется, в идиоме каждого фреймворка:

| Рамочная основа | Следуй за флагом |
|---|---|
| React, Preact | `useBlocker(dirty)` при каждом рендеринге |
| Vue | `useBlocker(dirty)` с `dirty` ссылкой или вычисленным |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` также принимает функцию для принятия решения, которая зависит от того, куда идет посетитель. Он получает следующее и текущее местоположение и возвращает причину (строку) оставаться или нечего продолжать:

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

Функция сама не запрашивает и не держит перезагрузку; позвоните в `confirm()` и спросите.

## `Image`

`Image` отображает `<img>` по умолчанию ленивым и не меняет макет, когда его размер известен.

| Рамочная основа | Импорт |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` требуется; используйте `alt=""` для декоративного изображения. Nexy предупреждает один раз, когда он отсутствует.
- И с `width`, и с `height` атрибуты задают браузеру соотношение сторон, и изображение остается плавным (`height: auto; max-width: 100%`).
- `priority` теперь загружает изображение с высоким приоритетом, то есть то, которое видно по прибытии.
- `fill` заставляет изображение перекрывать позиционируемый родительский элемент, игнорируя `width` и `height`.
- `sizes` и `srcSet` проходят. Nexy не изменяет размер и не конвертирует изображения.

## Ссылка со страницы `.nexy`

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` отображает `<a href="/about" data-nexy-link="true">`. Каждый атрибут и `href` экранируются HTML.

## Что делает роутер

По навигации роутер:

1. сопоставляет путь с клиентскими маршрутами (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. импортирует и визуализирует страницу и ее [макеты](../layouts/README.md) **сначала**, а только затем перемещает URL-адрес с помощью `history.pushState`, поэтому в адресной строке никогда не отображается страница, на которой произошел сбой;
3. отправляет событие `nexy:navigated` на `document`;
4. прокручивает вверх или к цели `#fragment`.

Новая навигация отменяет старую, которая все еще отображается. Если страница не может отобразиться, браузер вместо этого запрашивает ее у сервера. Кнопки «Назад» и «Вперед» отображают страницу этой записи и восстанавливают ее положение прокрутки.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

Маршрутизатор запускается только в проекте с клиентскими маршрутами, поэтому в проекте, отображаемом на сервере, сохраняется собственная кнопка браузера «Назад» и восстановление прокрутки.

## Следующие шаги

- [Макеты](../layouts/README.md)
- [КСО](../../../rendering/csr.md)
- [Компоненты](../../../views/nexy/components.md)
