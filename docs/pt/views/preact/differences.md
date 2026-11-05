# Preact

Nexy renderiza Preact 10 componentes no servidor e então Preact os assume no navegador. Páginas, layouts, ilhas e ações são iguais em todos os frameworks: esta página cobre a configuração e depois as partes que diferem dos [contratos compartilhados](../frontend/pages.md).

| Modo | `nexyconfig.py` | As páginas são | Preact são |
|---|---|---|---|
| Servidor (padrão) | `useCSR = False` | `.nexy` arquivos | [ilhas](../../rendering/islands.md) dentro dessas páginas |
| Cliente | `useCSR = True` | `.tsx` arquiva | a página inteira, com [layouts](../frontend/layouts.md) e um roteador cliente |

## Iniciar um projeto

```bash
nx new my-app --template web-fbr-preact
```

O modelo é um projeto em modo servidor com Preact ilhas. Execute `nx new my-app` sem um modelo para responder aos prompts: o roteador, o tipo de projeto, se deve usar roteamento do lado do cliente e, em seguida, a estrutura.

## Habilite Preact em um projeto existente

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` grava este arquivo; Nexy escreve `__nexy__/vite.ts` sozinho, então não o edite.

| Pacote | Versão `nx new` escreve |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (dependência de desenvolvimento) |
| `preact-render-to-string` | `^6.7.0` (dependência de desenvolvimento, renderização no servidor) |

## Escreva Preact

Um componente Preact é uma função no estilo React. As diferenças que importam aqui:

```tsx filename="src/componentes/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- Ganchos vêm de `preact/hooks`, tipos como `ComponentChildren` de `preact`.
- Escreva atributos HTML: `class`, `for`, `charset`. `Link` lê suas classes de `class`.

## Regras

- **Uma estrutura por projeto.** `useFF` leva exatamente uma estrutura; `useFF = [preact(), react()]` interrompe o servidor na inicialização. Com `useFF = preact()`, todo arquivo `.tsx` é Preact.
- **As páginas são `.tsx`.** Somente um arquivo `.tsx` em `src/routes/` se torna uma página; `.jsx` é adequado para um componente.
- **Os componentes ficam fora de `src/routes/`**, geralmente em `src/components/`, portanto não são páginas.
- **Um projeto em modo servidor não tem página `.tsx`**, e um projeto em modo cliente não tem página `.nexy`: Nexy se recusa a iniciar e nomeia o arquivo. Consulte [modos](../../routing/fbr/modes.md).
- **Uma página `.mdx` importa de `"preact"`.** Nexy compila um arquivo `.mdx` com Preact somente quando vê essa importação, por exemplo `import { h } from "preact"`, e com React caso contrário. Consulte [Markdown e MDX](../nexy/markdown.md).

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

Os parâmetros de URL estão disponíveis através do gancho `useParams`:

```tsx filename="src/rotas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Layouts

### Implementação

O layout raiz define o shell do documento. Layouts aninhados envolvem o conteúdo.

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## Ilhas

No modo servidor, um componente Preact importado para um arquivo `.nexy` é uma ilha.

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

Use o gancho `useAction` para gerenciar o estado de uma chamada de ação:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### Navegação

Use o componente `Link` para transições do lado do cliente. Observe que Preact usa `class` em vez de `className`:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

Para navegação programática, use o gancho `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Acesso URL

- `usePathname()`: caminho atual
- `useParams()`: segmentos dinâmicos
- `useSearchParams()`: string de consulta
- `useLocation()`: objeto de localização completo

## Próximas etapas

- [Visualizações](../README.md): compare os formatos que uma página pode usar
- [Frontend](../../guides/frontend.md): Vite e a compilação do cliente
