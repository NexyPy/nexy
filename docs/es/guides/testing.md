# Pruebas

`nx test` ejecuta las pruebas del servidor con pytest, y el cliente prueba con vitest cuando las solicitas.

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## que corre

| Parte | Comando | Condición |
|---|---|---|
| El servidor | `pytest` | se ejecuta en `tests/` cuando existe; de lo contrario, en la raíz del proyecto; omitido con una advertencia cuando pytest no está instalado |
| Cliente | `npx vitest run` | solo con `--client`, y solo cuando `vitest.config.ts` existe o `vitest` aparece en `package.json` |

No hay un corredor integrado de un extremo a otro. Maneja el servidor con `TestClient` y agrega Playwright o Cypress tú mismo para el comportamiento del navegador.

## Probar el servidor

El cliente de prueba se comunica con la aplicación ASGI en proceso: no hay servidor para iniciar, no hay puerto para elegir.

```python filename="pruebas/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` es la aplicación ensamblada, creada la primera vez que se lee. Lee `nexyconfig.py` del directorio de trabajo, así que ejecuta pytest desde la raíz del proyecto.

Cuando una prueba cambia la configuración o las rutas, cree una aplicación nueva en lugar de reutilizar la de nivel de módulo:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` vuelve a ensamblar rutas, middleware, sesiones y traducciones, por lo que cada llamada comienza desde el estado actual del directorio del proyecto.

## que afirmar

Una página devuelve HTML. Afirme el estado y luego el contenido que le interesa:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

Un controlador API devuelve JSON. Un error de validación es un `422`, y una ruta faltante es un `404` respondido por `notfound.nexy` cuando ese archivo existe:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

Para una acción, pruebe la función directamente (es una función normal) y pruebe el punto final HTTP leyendo su ruta generada en la página que lo expone:

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    response = client.post(action, data={"name": "Ada"}, follow_redirects=False)
    assert response.status_code == 303
```

Una llamada con JSON responde con el resultado, y `422` con los campos no válidos.

> [!NOTE]
> Las rutas de acción son específicas del proyecto y se generan. Nunca codifique `/_nx_<hash>` en una prueba.

## Probar un componente `.nexy`

`nexy.testing.render` compila un componente, con los componentes que importa y devuelve su HTML. Los accesorios son argumentos de palabras clave y `children=` llena el espacio:

```python filename="pruebas/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

Ejecute pytest desde la raíz del proyecto: los archivos compilados van a `__nexy__/`, como ocurre con `nx dev`. Un componente que lee la solicitud (`usePathname`, `useSession`) necesita una prueba de página con `TestClient` en su lugar.

## Probar al cliente

`nx test --client` espera su propia configuración de vitest. Una prueba de componentes mínimos:

```tsx filename="src/components/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` y la biblioteca de pruebas son dependencias del proyecto: `nexy new` no instala una pila de pruebas. Agregue `vitest.config.ts` con el entorno que necesita (jsdom o happy-dom para componentes).

## Integración continua

Dos comandos son suficientes para la canalización de un proyecto:

```bash
nx build
nx test
```

`nx build` falla por un error de compilación; `nx test` falla en una aserción fallida y sale de un valor distinto de cero. `nx check` agrega mypy y `tsc` a la ejecución.

Trabajar en Nexy utiliza diferentes comandos: consulte [CONTRIBUCIÓN](../../CONTRIBUTING.md).

## Próximos pasos

- [CLI](../reference/cli.md): cada bandera de `nx test`
- [API](../routing/fbr/handlers/README.md): qué devuelve un punto final
- [Implementar](../deployment/README.md): compila antes de probar en CI
