# Solid

Nexy renderiza Solid componentes 1.9 no servidor e então Solid os assume no navegador. Páginas, layouts, ilhas e ações são iguais em todos os frameworks: esta página cobre a configuração e depois as partes que diferem dos [contratos compartilhados](../frontend/pages.md).

| Modo | `nexyconfig.py` | As páginas são | Solid são |
|---|---|---|---|
| Servidor (padrão) | `useCSR = False` | `.nexy` arquivos | [ilhas](../../rendering/islands.md) dentro dessas páginas |
| Cliente | `useCSR = True` | `.tsx` arquiva | a página inteira, com [layouts](../frontend/layouts.md) e um roteador cliente |

## Iniciar um projeto

```bash
nx new my-app --template web-fbr-solid
```

O modelo é um projeto em modo servidor com Solid ilhas. Execute `nx new my-app` sem um modelo para responder aos prompts: o roteador, o tipo de projeto, se deve usar roteamento do lado do cliente e, em seguida, a estrutura.

## Habilite Solid em um projeto existente

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

No modo cliente escreva `solid({ ssr: true })`: Solid compila um componente de maneira diferente para o servidor e para o navegador, e o modo cliente precisa de ambos. `nx new` grava este arquivo; Nexy escreve `__nexy__/vite.ts` sozinho, então não o edite.

| Pacote | Versão `nx new` escreve |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (dependência de desenvolvimento) |

## Pense em sinais

Uma função de componente Solid é executada **uma vez**. O que muda depois é lido através de um sinal, e apenas as expressões que o leem são atualizadas:

```tsx filename="src/componentes/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- Chame o sinal, `count()`, dentro do JSX, não em uma variável acima dele.
- Leia adereços como `props.start`. A desestruturação `{ start }` lê o valor uma vez e perde as atualizações.
- Solid escreve atributos HTML: `class`, `for`, `charset`, não `className`.

## Regras

- **Uma estrutura por projeto.** `useFF` leva exatamente uma estrutura; `useFF = [solid(), react()]` interrompe o servidor na inicialização. Com `useFF = solid()`, cada arquivo `.tsx` é Solid.
- **As páginas são `.tsx`.** Somente um arquivo `.tsx` em `src/routes/` se torna uma página; `.jsx` é adequado para um componente.
- **Os componentes ficam fora de `src/routes/`**, geralmente em `src/components/`, portanto não são páginas.
- **Um projeto em modo servidor não tem página `.tsx`**, e um projeto em modo cliente não tem página `.nexy`: Nexy se recusa a iniciar e nomeia o arquivo. Consulte [modos](../../routing/fbr/modes.md).
- **Não `.mdx` com Solid.** MDX compila para React ou Preact; `.md` páginas funcionam.

## Páginas

No modo cliente (`useCSR = True`), uma página é um arquivo `.tsx`.

### Componente de página

Uma página é a exportação padrão do arquivo. Se não existir nenhuma exportação padrão, Nexy escolhe a primeira exportação nomeada.

```tsx filename="src/rotas/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Segmentos dinâmicos

Os parâmetros de URL estão disponíveis através do gancho `useParams`, que retorna um acessador:

```tsx filename="src/rotas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## Layouts

### Implementação

O layout raiz define o shell do documento. Layouts aninhados envolvem o conteúdo.

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

Não desestruturar `props.children`, pois Solid lê preguiçosamente.

## Ilhas

No modo servidor, um componente Solid importado para um arquivo `.nexy` é uma ilha.

### Importando

Importe componentes no frontmatter do arquivo `.nexy`:

```nexy filename="src/rotas/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### Diretrizes de hidratação

Use a propriedade `directive` para controlar quando a ilha hidrata:

- `client:load` (padrão): imediatamente
- `client:idle`: quando o navegador está ocioso
- `client:visible`: quando rola para visualização
- `client:media`: quando a consulta de mídia corresponde

## Ações e navegação

### Chamando ações

Use o gancho `useAction` para gerenciar o estado de uma chamada de ação. Em Solid, isso retorna acessadores (chame-os como funções).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### Navegação

Use o componente `Link` para transições do lado do cliente:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

Para navegação programática, use o gancho `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Acesso URL

Todos os ganchos de localização retornam acessadores:

- `usePathname()`: caminho atual
- `useParams()`: segmentos dinâmicos
- `useSearchParams()`: string de consulta
- `useLocation()`: objeto de localização completo

## Próximas etapas

- [Visualizações](../README.md): compare os formatos que uma página pode usar
- [Frontend](../../guides/frontend.md): Vite e a compilação do cliente
