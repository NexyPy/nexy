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

| Фреймворк | Импорт |
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
| `href` | Маршрут проекта (опечатка — ошибка типа), опционально с `?query` или `#fragment`, или внешний URL. |
| `replace` | Заменить запись истории вместо ее добавления. |
| `scroll` | `false` сохраняет положение прокрутки после навигации. По умолчанию: `true`. |
| `prefetch` | `'intent'` (по умолчанию) загружает страницу при наведении, фокусировке или касании; `'viewport'` когда ссылка прокручивается в поле зрения; `false` никогда. |
| `activeClassName` | Добавляется в класс, когда ссылка указывает на текущую страницу или страницу под ней (`activeClass` в Vue и Svelte). |
| `exact` | Активно только на конкретной странице. |

Ссылка, указывающая на текущую страницу, также получает `aria-current="page"`.

## Крючки

Местоположение доступно в каждом фреймворке, в его идиоме. Во время первого этапа серверная часть обрабатывает ответ с URL-адресом запроса, поэтому страница гидратируется без несоответствий.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Путь | `usePathname()` | `usePathname()` возвращает метод доступа | `usePathname()` возвращает ссылку на | `$pathname` хранилище |
| Параметры маршрута | `useParams()` | `useParams()` средство доступа | `useParams()` ссылка | `$params` хранилище |
| Запрос | `useSearchParams()` | `useSearchParams()` аксессор | `useSearchParams()` ссылка | `$searchParams` хранилище |
| Все | `useLocation()` | `useLocation()` аксессор | `useLocation()` ссылка | `$location` магазин |
| Перейдите по | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

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

## `Image`

`Image` отображает `<img>` по умолчанию лениво и не меняет макет, когда его размер известен.

| Фреймворк | Импорт |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` требуется; используйте `alt=""` для декоративного изображения. Nexy предупреждает один раз, когда он отсутствует.
- Как для `width`, так и для `height` атрибуты задают браузеру соотношение сторон, и изображение остается плавным (`height: auto; max-width: 100%`).
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

1. сопоставляет путь с маршрутами клиента (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. импортирует и отображает страницу и ее [макеты](../layouts/README.md) **сначала** и только затем перемещает URL-адрес с помощью `history.pushState`, поэтому в адресной строке никогда не отображается страница, которая не удалась;
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
