# Действия и навигация

Взаимодействие в Nexy осуществляется через единую систему **Действий** и **Навигации**, гарантируя, что интерфейс и серверная часть остаются синхронизированными без ручного связующего кода API.

## Контракт действия

**Действие** — это серверная функция, которая обрабатывает мутацию (например, обновление базы данных). 

1.  **Типизированный ввод**: действия определены в Python с подсказками типов. Nexy генерирует соответствующий клиент TypeScript, поэтому вы получаете автозаполнение и проверку в своей IDE.
2.  **Атомное выполнение**: действие представляет собой одиночный `POST` запрос.
3.  **Обработка результатов**: действия возвращают типизированный результат, который клиент может использовать для обновления пользовательского интерфейса.

```python filename="src/actions/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

Страница вызывает его с объявленным вводом Python и получает в ответ типизированный `Todo`:

```tsx filename="src/маршруты/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

## Клиентская навигация

Навигация в Nexy «умная». Вместо полной перезагрузки браузера Nexy меняет содержимое текущей страницы, сохраняя при этом активные макеты.

- **Компонент `Link`**: используйте компонент `Link` для конкретной платформы для выполнения переходов на стороне клиента.
- **Программная навигация**: используйте `useRouter()` из `@nexy/client` и вызывайте `push()` для изменения страниц в ответ на логику (например, после успешного входа в систему).

```tsx filename="src/компоненты/Nav.tsx"
import { Link } from "@nexy/client";

export function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
    </nav>
  );
}
```

```tsx filename="источник/компоненты/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## Координация: Действие → Навигация

Самый распространенный шаблон — выполнить действие, а затем перевести пользователя на новую страницу.

**Порядок повторной проверки:**
1.  Клиент вызывает Action.
2.  Действие выполняется на сервере и вызывает `revalidate("/path")`.
3.  Сервер возвращает результат с заголовком `x-nexy-revalidate` с указанием устаревших путей.
4.  Клиент обновляет содержимое страницы, чтобы отразить новое состояние.

```python filename="src/actions/session.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

```tsx filename="src/маршруты/login.tsx"
import { useAction, useRouter } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export default function Login() {
  const router = useRouter();
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) router.push("/dashboard");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```

`check_password` означает вашу собственную проверку. См. [Действия](../../guides/actions.md) для ошибок, форм без JavaScript и безопасности.

## Реализация фреймворка

API для вызова действий и навигации зависит от платформы. См. руководство **Различия** для выбранной вами технологии:

- [React Различия](../react/differences.md)
- [Vue Различия](../vue/differences.md)
- [Svelte Различия](../svelte/differences.md)
- [Solid Различия](../solid/differences.md)
- [Preact Различия](../preact/differences.md)
