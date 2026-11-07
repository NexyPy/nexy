# Acciones y Navegación

La interacción en Nexy se maneja a través de un sistema unificado de **Acciones** y **Navegación**, lo que garantiza que el frontend y el backend permanezcan sincronizados sin código de pegamento API manual.

## El contrato de acción

Una **Acción** es una función del lado del servidor que maneja una mutación (por ejemplo, actualizar una base de datos). 

1.  **Entrada escrita**: las acciones se definen en Python con sugerencias de tipo. Nexy genera un cliente TypeScript coincidente, por lo que obtienes autocompletado y validación en tu IDE.
2.  **Ejecución atómica**: una acción es una única solicitud `POST`.
3.  **Manejo de resultados**: las acciones devuelven un resultado escrito que el cliente puede usar para actualizar la interfaz de usuario.

```python filename="src/acciones/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

La página lo llama con la entrada Python declarada y obtiene un `Todo` escrito de vuelta:

<!-- router:fbr,custom -->
```tsx filename="src/rutas/todos.tsx"
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
<!-- /router -->

<!-- router:modular -->
El componente es una isla de una vista y un controlador devuelve la vista:

```tsx filename="src/components/Todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

```nexy filename="src/apps/todos_view.nexy"
---
from "@/components/Todos.tsx" import Todos
---
<Todos directive="client:load" />
```
<!-- /router -->

## Navegación del lado del cliente

La navegación en Nexy es "inteligente". En lugar de recargar completamente el navegador, Nexy intercambia el contenido de la página actual mientras mantiene montados los diseños activos.

- **El componente `Link`**: utilice el componente `Link` específico del marco para realizar transiciones del lado del cliente.
- **Navegación programática**: use `useRouter()` desde `@nexy/client` y llame a `push()` para cambiar páginas en respuesta a la lógica (por ejemplo, después de un inicio de sesión exitoso).

```tsx filename="src/components/Nav.tsx"
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

```tsx filename="src/components/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## Coordinación: Acción → Navegación

El patrón más común es realizar una acción y luego llevar al usuario a una nueva página.

**El flujo de revalidación:**
1.  El cliente llama a una Acción.
2.  La acción se ejecuta en el servidor y llama a `revalidate("/path")`.
3.  El servidor devuelve el resultado con un encabezado `x-nexy-revalidate` que nombra las rutas obsoletas.
4.  El cliente actualiza el contenido de la página para reflejar el nuevo estado.

```python filename="src/acciones/sesión.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

<!-- router:fbr,custom -->
```tsx filename="src/rutas/login.tsx"
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
<!-- /router -->

<!-- router:modular -->
```tsx filename="src/components/Login.tsx"
import { useAction } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export function Login() {
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) window.location.assign("/dashboard/");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```
<!-- /router -->

`check_password` representa su propio cheque. Consulte [Acciones](../../guides/actions.md) para errores, formularios sin JavaScript y seguridad.

## Implementación del marco

La API para invocar acciones y navegar varía según el marco. Consulta la guía de **Diferencias** para la tecnología elegida:

- [React Diferencias](../react/differences.md)
- [Vue Diferencias](../vue/differences.md)
- [Svelte Diferencias](../svelte/differences.md)
- [Solid Diferencias](../solid/differences.md)
- [Preact Diferencias](../preact/differences.md)
