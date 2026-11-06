# Ações e navegação

A interação no Nexy é feita por meio de um sistema unificado de **Ações** e **Navegação**, garantindo que o frontend e o backend permaneçam sincronizados sem código de colagem manual da API.

## O Contrato de Ação

Uma **Action** é uma função do lado do servidor que lida com uma mutação (por exemplo, atualizar um banco de dados). 

1.  **Entrada digitada**: As ações são definidas em Python com dicas de tipo. Nexy gera um cliente TypeScript correspondente, para que você obtenha preenchimento automático e validação em seu IDE.
2.  **Execução Atômica**: Uma ação é uma única solicitação `POST`.
3.  **Tratamento de resultados**: As ações retornam um resultado digitado que o cliente pode usar para atualizar a UI.

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

A página o chama com a entrada Python declarada e recebe um `Todo` digitado de volta:

```tsx filename="src/routes/todos.tsx"
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

## Navegação do lado do cliente

A navegação no Nexy é "inteligente". Em vez de recarregar completamente o navegador, o Nexy troca o conteúdo da página atual enquanto mantém os layouts ativos montados.

- **O `Link` Componente**: Use o componente específico da estrutura `Link` para realizar transições do lado do cliente.
- **Navegação programática**: Use `useRouter()` de `@nexy/client` e chame `push()` para alterar páginas em resposta à lógica (por exemplo, após um login bem-sucedido).

```tsx filename="src/componentes/Nav.tsx"
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

```tsx filename="src/componentes/Concluído.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## Coordenação: Ação → Navegação

O padrão mais comum é executar uma ação e então direcionar o usuário para uma nova página.

**O Fluxo de Revalidação:**
1.  O cliente chama uma ação.
2.  A Action é executada no servidor e chama `revalidate("/path")`.
3.  O servidor retorna o resultado com um cabeçalho `x-nexy-revalidate` nomeando os caminhos obsoletos.
4.  O cliente atualiza o conteúdo da página para refletir o novo estado.

```python filename="src/actions/session.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

```tsx filename="src/routes/login.tsx"
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

`check_password` significa seu próprio cheque. Veja [Ações](../../guides/actions.md) para erros, formulários sem JavaScript e segurança.

## Implementação da Estrutura

A API para chamar ações e navegar varia de acordo com a estrutura. Consulte o guia **Diferenças** da tecnologia escolhida:

- [React Diferenças](../react/differences.md)
- [Vue Diferenças](../vue/differences.md)
- [Svelte Diferenças](../svelte/differences.md)
- [Solid Diferenças](../solid/differences.md)
- [Preact Diferenças](../preact/differences.md)
