# Acciones

Un `@Action` convierte una función Python en un punto final `POST`. A diferencia de un controlador API estándar, está diseñado como un puente de comunicación escrito: Nexy genera automáticamente el cliente TypeScript, valida la entrada y maneja la respuesta.

**Antes de comenzar:** un proyecto creado por el [Inicio rápido](../getting-started/quick-start.md). Las acciones se encuentran junto a las páginas, en `src/actions/`.

```diagram filename="El ciclo de acción"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## El ciclo de acción

### 1. Definir
Una acción es una función normal Python marcada con `@Action`. Nexy usa su firma para definir el contrato API.

```python filename="src/acciones/usuario.py"
from pydantic import BaseModel
from nexy.decorators import Action, revalidate

class User(BaseModel):
    name: str
    age: int = 0

@Action
async def create_user(name: str, age: int = 0) -> User:
    revalidate()
    return User(name=name, age=age)
```

Los parámetros son la entrada, validada por Pydantic. Se inyecta un parámetro denominado `request` o `response` y no forma parte de la entrada.

### 2. Validar
Cuando se llama a la acción, Nexy valida la entrada con las sugerencias de tipo de la función. Si falta un campo o tiene un tipo incorrecto, la acción no se ejecuta y se devuelve un `422 Unprocessable Entity`.

### 3. Ejecutar
La lógica se ejecuta en el servidor. Dado que es una función estándar Python, puede usar cualquier biblioteca, acceder a la base de datos o llamar a otros servicios. También puede activar una actualización de la página usando `revalidate()`.

### 4. Serializar
El valor de retorno se serializa automáticamente a JSON. Los modelos Pydantic se manejan de forma nativa y los tipos estándar Python se asignan a sus equivalentes JSON.

### 5. Consumir
La interfaz recibe el resultado con total seguridad de tipo. Nexy escribe `__nexy__/src/actions.ts` a partir de sus firmas y `@nexy/actions` lo resuelve.

<!-- router:fbr,custom -->
```tsx filename="src/rutas/usuarios.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export default function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
El componente es una isla de la vista que devuelve un controlador:

```tsx filename="src/components/NuevoUsuario.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```

```nexy filename="src/apps/users/user_view.nexy"
---
from "@/components/NewUser.tsx" import NewUser
---
<NewUser directive="client:load" />
```
<!-- /router -->

Sin un gancho, una acción es solo una función `async`: `const user = await create_user({ name: "Ada" })`.

| Marco | Lo que `useAction` devuelve |
|---|---|
| React, Preact | `{ pending, data, error, run, reset }` |
| Solid | lo mismo, con `pending()`, `data()` y `error()` como accesores |
| Vue | lo mismo, con `pending`, `data` y `error` como referencias |
| Svelte | una tienda: `$save.pending`, `$save.data`, `$save.error`, más `save.run(input)` y `save.reset()` |

`useAction(action, { onSuccess, onError })` también acepta dos devoluciones de llamada. `run` nunca lanza: un fallo aterriza en `error` y `run` se resuelve con `undefined`.

Los tipos provienen de Python: `str` es `string`, `int` y `float` son ​​`number`, `list[T]` es `T[]`, un modelo Pydantic o un `Enum` es un tipo con nombre, y un campo con un valor predeterminado es opcional en la entrada. Un tipo Pydantic que no se puede describir se convierte en `unknown`.

## Errores y fallas

Una acción puede fallar en diferentes etapas. Debes distinguir entre ellos en tu UI:

1.  **Errores de validación (422)**: la entrada no coincidía con la firma Python. `error.fields` asigna cada campo no válido a su mensaje.
2.  **Errores comerciales (`HTTPException`)**: su código rechazó la llamada, por ejemplo `403 Forbidden` o `409 Conflict`.
3.  **Errores del servidor (500)**: se produjo una excepción no controlada en su código Python.
4.  **Errores de red**: la solicitud nunca llegó al servidor, por ejemplo, un tiempo de espera o una conexión perdida.
5.  **Errores de autorización (401, 403)**: su propio cheque rechazó a la persona que llama. Nexy no decide esto por ti.

La verificación de origen que se describe a continuación es una protección CSRF, no una autorización: dice de dónde vino la llamada, nunca quién puede realizarla.

## Actualizar la página después de una acción.

Una acción dice qué páginas su cambio dejó obsoletas, como lo hace Next.js con `revalidatePath`:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

La respuesta lleva las rutas en un encabezado `x-nexy-revalidate`. Luego, el cliente vuelve a buscar la página actual a través del enrutador o la recarga cuando no hay ningún enrutador cliente.

## Formularios sin JavaScript

Una acción también toma un formato HTML estándar, por lo que la página funciona antes de que se cargue cualquier script:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

En una plantilla `.nexy`, `__actions_path["name"]` es la ruta, `__actions["name"]` la función y la función también está dentro del alcance bajo su propio nombre.

Si tiene éxito, el visitante regresa a la página en la que se encontraba el formulario, con el estado `303`. Para responder de manera diferente, devuelva un objeto `Response` (por ejemplo, `RedirectResponse("/done", status_code=303)`).

## Seguridad

### La oscuridad del camino no es autorización.
La ruta de acción es `/_nx_` seguida de un hash del módulo de la función, su nombre y un secreto del proyecto. Lo establece `NEXY_ACTION_SECRET`, o lo guarda en `__nexy__/action.key`, que `nx build` crea para que el paquete del cliente y `nx start` acuerden: conservar ese archivo con la compilación. La ruta oculta el punto final del descubrimiento casual y **la ruta generada no es un mecanismo de autorización**.

Cualquiera que conozca el camino puede iniciar la acción. Tú **debes** verificar la identidad y los permisos del usuario dentro de la acción:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### Protección de origen
Para evitar la falsificación de solicitudes entre sitios (CSRF), Nexy rechaza solicitudes cuyo `Origin` sea otro sitio o que el navegador marque `Sec-Fetch-Site: cross-site` con un `403`. Enumere los sitios que pueden llamar a sus acciones en `NEXY_ALLOWED_ORIGINS`. Se aceptan llamadas sin `Origin` (como `curl`).

## Errores de importación

Al inicio, Nexy importa todos los módulos de `src/` para encontrar las acciones. Se informa de un módulo que no se puede importar y los demás aún se cargan:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## Próximos pasos

- [API](../routing/fbr/handlers/README.md): controladores explícitos
- [Pruebas](testing.md#what-to-assert): cómo probar una acción
- [Configuración](../reference/config.md): opciones de autenticación y middleware
