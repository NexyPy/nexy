# Teste

`nx test` executa os testes do servidor com pytest, e o cliente testa com vitest quando você os solicita.

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## O que funciona

| Parte | Comando | Condição |
|---|---|---|
| Servidor | `pytest` | roda em `tests/` quando existe, caso contrário, na raiz do projeto; ignorado com um aviso quando o pytest não está instalado |
| Cliente | `npx vitest run` | somente com `--client`, e somente quando `vitest.config.ts` existir ou `vitest` aparecer em `package.json` |

Não há corredor de ponta a ponta integrado. Dirija o servidor com `TestClient` e adicione Playwright ou
Cypress você mesmo pelo comportamento do navegador.

## Teste o servidor

O cliente de teste se comunica com o aplicativo ASGI durante o processo: nenhum servidor para iniciar, nenhuma porta para escolher.

```python filename="testes/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` é a aplicação montada, construída na primeira vez que é lida. Ele lê
`nexyconfig.py` do diretório de trabalho, então execute pytest na raiz do projeto.

Quando um teste altera a configuração ou as rotas, crie um novo aplicativo em vez de
reutilizando o nível do módulo:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` remonta rotas, middleware, sessões e traduções, para que cada chamada seja iniciada
do estado atual do diretório do projeto.

## O que afirmar

Uma página retorna HTML. Afirme o status e, em seguida, o conteúdo de seu interesse:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

Um manipulador de API retorna JSON. Uma falha de validação é um `422` e uma rota ausente é um `404`
respondido por `notfound.nexy` quando esse arquivo existe:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

Para uma ação, teste a função diretamente - é uma função normal - e teste o endpoint HTTP
lendo seu caminho gerado na página que o expõe:

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

Uma chamada com JSON responde com o resultado e `422` com os campos inválidos.

> [!NOTA]
> os caminhos de ação são específicos do projeto e gerados. Nunca codifique
> `/_nx_<hash>` em um teste.

## Teste um componente `.nexy`

`nexy.testing.render` compila um componente, com os componentes que ele importa, e retorna seu HTML.
Props são argumentos de palavras-chave e `children=` preenche o espaço:

```python filename="testes/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

Execute pytest a partir da raiz do projeto: os arquivos compilados vão para `__nexy__/`, como acontece com `nx dev`. Um
componente que lê a solicitação (`usePathname`, `useSession`) precisa de um teste de página com `TestClient`
em vez disso.

## Teste o cliente

`nx test --client` espera sua própria configuração de vitest. Um teste de componente mínimo:

```tsx filename="src/componentes/counter.test.tsx"
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

`vitest` e a biblioteca de testes são dependências do projeto: `nexy new` não instala uma pilha de testes.
Adicione `vitest.config.ts` com o ambiente que você precisa (jsdom ou happy-dom para componentes).

## Integração contínua

Dois comandos são suficientes para um pipeline de projeto:

```bash
nx build
nx test
```

`nx build` falha devido a um erro de compilação; `nx test` falha em uma asserção com falha e sai diferente de zero.
`nx check` adiciona mypy e `tsc` à execução.

Trabalhar no próprio Nexy usa comandos diferentes: veja [CONTRIBUTING](../../CONTRIBUTING.md).

## Próximas etapas

- [CLI](../reference/cli.md): cada sinalizador de `nx test`
- [API](../routing/fbr/handlers/README.md): o que um endpoint retorna
- [Deploy](../deployment/README.md): crie antes de testar no CI