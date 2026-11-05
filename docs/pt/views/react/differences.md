# React

Nexy renderiza React 19 componentes no servidor e, em seguida, React os hidrata no navegador. Páginas, layouts, ilhas e ações são iguais em todos os frameworks: esta página cobre a configuração e depois as partes que diferem dos [contratos compartilhados](../frontend/pages.md).

| Modo | `nexyconfig.py` | As páginas são | React são |
|---|---|---|---|
| Servidor (padrão) | `useCSR = False` | `.nexy` arquivos | [ilhas](../../rendering/islands.md) dentro dessas páginas |
| Cliente | `useCSR = True` | `.tsx` arquiva | a página inteira, com [layouts](../frontend/layouts.md) e um roteador cliente |

## Iniciar um projeto

```bash
nx new my-app --template web-fbr-react
```

O modelo é um projeto em modo servidor com React ilhas. Execute `nx new my-app` sem um modelo para responder aos prompts: o roteador, o tipo de projeto, se deve usar roteamento do lado do cliente e, em seguida, a estrutura.

## Habilite React em um projeto existente

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` grava este arquivo; Nexy escreve `__nexy__/vite.ts` sozinho, então não o edite.

| Pacote | Versão `nx new` escreve |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | dependências de desenvolvimento |

## Regras

- **Uma estrutura por projeto.** `useFF` leva exatamente uma estrutura; `useFF = [react(), vue()]` interrompe o servidor na inicialização.
- **As páginas são `.tsx`.** React possui `.tsx` e `.jsx` para componentes, mas apenas um arquivo `.tsx` em `src/routes/` se torna uma página.
- **Os componentes ficam fora de `src/routes/`**, geralmente em `src/components/`, portanto não são páginas.
- **Um projeto em modo servidor não tem `.tsx` página**, e um projeto em modo cliente não tem página `.nexy`: Nexy se recusa a iniciar e nomeia o arquivo. Consulte [modos](../../routing/fbr/modes.md).

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

O layout raiz define o shell do documento. Os layouts aninhados envolvem o conteúdo abaixo deles.

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

## Ilhas

No modo servidor, um componente React importado para um arquivo `.nexy` é uma ilha.

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

- `usePathname()`: caminho atual
- `useParams()`: segmentos dinâmicos
- `useSearchParams()`: string de consulta
- `useLocation()`: objeto de localização completo

## Próximas etapas

- [Visualizações](../README.md): compare os formatos que uma página pode usar
- [Frontend](../../guides/frontend.md): Vite e a compilação do cliente
