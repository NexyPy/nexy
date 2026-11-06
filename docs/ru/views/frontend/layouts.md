# Макеты внешнего интерфейса

**Макет** — это оболочка, определяющая общую структуру одной или нескольких страниц. Макеты позволяют работать с приложением, сохраняя состояние и избегая полной перезагрузки страницы во время навигации.

## Вложенная логика

Макеты имеют иерархическую структуру, основанную на дереве каталогов в `src/routes/`.

1.  **Корневой макет**: каждый проект имеет корневой макет (например, `src/routes/layout.nexy`). Это единственный макет, отвечающий за определение оболочки документа: `<html>`, `<head>` и `<body>`.
2.  **Вложенные макеты**: любая папка может содержать собственный файл `layout.*`. Этот макет объединяет все страницы и подмакеты в этой папке.
3.  **Наследование**: страница оборачивается всеми макетами от корня до собственной папки.

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

Вложенный макет рисует только свою часть пользовательского интерфейса и помещает страницу туда, где идет `children`:

```tsx filename="src/маршруты/панель мониторинга/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## Общее состояние и состав

Макеты спроектированы так, чтобы быть стабильными. В клиентском режиме при навигации между двумя страницами с одинаковым макетом макет **не** перерисовывается; меняется только дочерний контент. В режиме сервера каждая навигация представляет собой новый документ.

- **Слоты**: макеты предоставляют слот, в который вставляется вложенная страница: `children` в JSX и свойство `children` в макете `.nexy`.
- **Сохранение состояния**: поскольку макет остается смонтированным, любое состояние, содержащееся в нем (например, поисковый запрос в заголовке), сохраняется во время навигации.

Тот же слот в макете `.nexy`:

```nexy filename="src/маршруты/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

Поле поиска ниже сохраняет то, что вводил пользователь при перемещении между страницами панели управления, поскольку макет, в котором оно содержится, никогда не размонтируется:

```tsx filename="src/маршруты/панель мониторинга/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## Статические ограничения

Для предварительно обработанных маршрутов (SSG) корневой макет не может зависеть от данных времени запроса, таких как файлы cookie или заголовки. Он должен быть представлен как статичная оболочка, которую клиент затем увлажняет.

Вместо этого прочитайте тему из браузера в скрипте статической оболочки:

```tsx filename="src/маршруты/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Реализация фреймворка

Реализация слотов и вложенности немного различается в зависимости от платформы. См. руководство **Различия** для выбранной вами технологии:

- [React Различия](../react/differences.md)
- [Vue Различия](../vue/differences.md)
- [Svelte Различия](../svelte/differences.md)
- [Solid Различия](../solid/differences.md)
- [Preact Различия](../preact/differences.md)
