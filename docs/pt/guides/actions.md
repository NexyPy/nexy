# Ações

Um `@Action` transforma uma função Python em um endpoint `POST`. Ao contrário de um manipulador de API padrão, ele é projetado como uma ponte de comunicação digitada: Nexy gera automaticamente o cliente TypeScript, valida a entrada e trata a resposta.

**Antes de começar:** um projeto criado pelo [Início rápido](../getting-started/quick-start.md). As ações ficam ao lado das páginas, em `src/actions/`.

```diagram filename="O Ciclo de Ação"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## O Ciclo de Ação

### 1. Definir
Uma ação é uma função normal Python marcada com `@Action`. Nexy usa sua assinatura para definir o contrato da API.

```python filename="src/actions/user.py"
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

Os parâmetros são a entrada, validados por Pydantic. Um parâmetro denominado `request` ou `response` é injetado e não faz parte da entrada.

### 2. Validar
Quando a ação é chamada, Nexy valida a entrada em relação às dicas de tipo da função. Se um campo estiver faltando ou tiver o tipo errado, a ação não será executada e um `422 Unprocessable Entity` será retornado.

### 3. Executar
A lógica é executada no servidor. Por ser uma função padrão Python, você pode usar qualquer biblioteca, acessar o banco de dados ou chamar outros serviços. Você também pode acionar uma atualização de página usando `revalidate()`.

### 4. Serializar
O valor de retorno é serializado automaticamente para JSON. Os modelos Pydantic são tratados nativamente e os tipos Python padrão são mapeados para seus equivalentes JSON.

### 5. Consumir
O frontend recebe o resultado com total segurança de tipo. Nexy escreve `__nexy__/src/actions.ts` a partir de suas assinaturas e `@nexy/actions` resolve isso.

<!-- router:fbr,custom -->
```tsx filename="src/routes/users.tsx"
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
O componente é uma ilha da visão que um controlador retorna:

```tsx filename="src/componentes/NewUser.tsx"
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

Sem um gancho, uma ação é apenas uma função `async`: `const user = await create_user({ name: "Ada" })`.

| Estrutura | O que `useAction` retorna |
|---|---|
| React, Preact | `{ pending, data, error, run, reset }` |
| Solid | o mesmo, com `pending()`, `data()` e `error()` como acessadores |
| Vue | o mesmo, com `pending`, `data` e `error` como referências |
| Svelte | uma loja: `$save.pending`, `$save.data`, `$save.error`, mais `save.run(input)` e `save.reset()` |

`useAction(action, { onSuccess, onError })` também recebe dois retornos de chamada. `run` nunca lança: uma falha cai em `error` e `run` resolve com `undefined`.

Os tipos vêm de Python: `str` é `string`, `int` e `float` são `number`, `list[T]` é `T[]`, um modelo Pydantic ou um `Enum` é um tipo nomeado, e um campo com um padrão é opcional na entrada. Um tipo Pydantic que não pode ser descrito torna-se `unknown`.

## Erros e Falhas

Uma ação pode falhar em diferentes estágios. Você deve distingui-los em sua IU:

1.  **Erros de validação (422)**: a entrada não correspondeu à assinatura Python. `error.fields` mapeia cada campo inválido para sua mensagem.
2.  **Erros de negócios (`HTTPException`)**: seu código recusou a chamada, por exemplo `403 Forbidden` ou `409 Conflict`.
3.  **Erros de servidor (500)**: ocorreu uma exceção não tratada em seu código Python.
4.  **Erros de rede**: a solicitação nunca chegou ao servidor, por exemplo, tempo limite ou perda de conexão.
5.  **Erros de autorização (401, 403)**: seu próprio cheque rejeitou o chamador. Nexy não decide isso por você.

A verificação de origem descrita abaixo é uma proteção CSRF, não uma autorização: ela diz de onde veio a chamada, nunca quem tem permissão para realizá-la.

## Atualize a página após uma ação

Uma ação diz quais páginas sua alteração tornou obsoletas, como Next.js faz com `revalidatePath`:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

A resposta carrega os caminhos em um cabeçalho `x-nexy-revalidate`. O cliente então busca novamente a página atual através do roteador ou a recarrega quando não há nenhum roteador cliente.

## Formulários sem JavaScript

Uma ação também assume um formato HTML padrão, para que a página funcione antes de qualquer script ser carregado:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

Em um modelo `.nexy` `__actions_path["name"]` é o caminho, `__actions["name"]` a função, e a função também está no escopo com seu próprio nome.

Em caso de sucesso, o visitante é enviado de volta à página em que o formulário estava, com status `303`. Para responder de forma diferente, retorne um objeto `Response` (por exemplo, `RedirectResponse("/done", status_code=303)`).

## Segurança

### A obscuridade do caminho não é autorização
O caminho da ação é `/_nx_` seguido por um hash do módulo da função, seu nome e um segredo do projeto. Ele é definido por `NEXY_ACTION_SECRET`, ou mantido em `__nexy__/action.key`, que `nx build` cria para que o pacote do cliente e `nx start` concordem: mantenha esse arquivo com a compilação. O caminho oculta o endpoint da descoberta casual e **o caminho gerado não é um mecanismo de autorização**.

Qualquer pessoa que conheça o caminho pode iniciar a ação. Você **deve** verificar a identidade e as permissões do usuário dentro da ação:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### Proteção de origem
Para evitar falsificação de solicitação entre sites (CSRF), Nexy recusa solicitações cujo `Origin` seja outro site ou que o navegador marque `Sec-Fetch-Site: cross-site` com um `403`. Liste os sites que podem chamar suas ações em `NEXY_ALLOWED_ORIGINS`. Chamadas sem `Origin` (como `curl`) são aceitas.

## Erros de importação

Na inicialização, o Nexy importa todos os módulos de `src/` para encontrar as ações. Um módulo que falha na importação é relatado e os outros ainda são carregados:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## Próximas etapas

- [API](../routing/fbr/handlers/README.md): manipuladores explícitos
- [Testando](testing.md#what-to-assert): como testar uma ação
- [Configuração](../reference/config.md): opções de middleware e autenticação
