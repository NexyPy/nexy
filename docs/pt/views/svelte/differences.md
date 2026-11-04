# Esbelto

Nexy renderiza os componentes do Svelte 5 no servidor e, em seguida, o Svelte os assume no navegador. Páginas,
layouts, ilhas e ações são iguais em todos os frameworks: esta página cobre a configuração, depois as partes
que diferem dos [contratos compartilhados](../frontend/pages.md).

| Modo | `nexyconfig.py` | As páginas são | Svelte é |
|---|---|---|---|
| Servidor (padrão) | `useCSR = False` | `.nexy` arquivos | [ilhas](../../rendering/islands.md) dentro dessas páginas |
| Cliente | `useCSR = True` | `.svelte` arquiva | a página inteira, com [layouts](../frontend/layouts.md) e um roteador cliente |

## Iniciar um projeto

```bash
nx new my-app --template web-fbr-svelte
```

O modelo é um projeto em modo servidor com ilhas Svelte. Execute `nx new my-app` sem um modelo para
em vez disso, responda aos prompts: o roteador, o tipo de projeto, se deve usar roteamento do lado do cliente e, em seguida,
o quadro.

## Ativar o Svelte em um projeto existente

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` grava este arquivo; Nexy escreve `__nexy__/vite.ts` sozinho, então não o edite.

| Pacote | Versão `nx new` escreve |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## Regras

- **Svelte 5.** Os componentes usam runas: `$props()`, `$state()` e trechos para crianças.
- **Uma estrutura por projeto.** `useFF` usa exatamente uma estrutura; `useFF = [svelte(), vue()]`
  interrompe o servidor na inicialização.
- **Um componente por arquivo.** O nome sob o qual você importa um arquivo `.svelte` é apenas a tag que você escreve.
- **Os componentes ficam fora de `src/routes/`**, geralmente em `src/components/`, portanto, não são páginas.
- **Um projeto em modo servidor não tem página `.svelte`** e um projeto em modo cliente não tem página `.nexy`: Nexy
  se recusa a iniciar e nomeia o arquivo. Veja [modos](../../routing/fbr/modes.md).

## Páginas

No modo cliente (`useCSR = True`), uma página é um arquivo `.svelte`.

### Componente de página

A página é o componente definido pelo bloco de script do arquivo `.svelte`.

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### Segmentos dinâmicos

Os parâmetros de URL chegam à página como acessórios por meio da runa `$props()`:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Alternativamente, use o armazenamento `$params` de `@nexy/client` em qualquer componente.

## Layouts

### Implementação

O layout raiz define o shell do documento. Layouts aninhados envolvem o conteúdo usando o `children`
trecho.

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## Ilhas

No modo servidor, um componente Svelte importado para um arquivo `.nexy` é uma ilha.

### Importando

Importe componentes no frontmatter do arquivo `.nexy`:

```nexy filename="src/rotas/index.nexy"
---
from "@/components/Counter.svelte" import Counter
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

### Ações de chamada

Use o gancho `useAction` para gerenciar o estado de uma chamada de ação. Em Svelte, isso retorna uma loja (leia
com `$`).

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### Navegação

Use o componente `Link` para transições do lado do cliente:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

Para navegação programática, use o objeto `router` de `@nexy/client`:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### Acesso ao URL

Todos os dados de localização são fornecidos como lojas:

- `$pathname`: caminho atual
- `$params`: segmentos dinâmicos
- `$searchParams`: string de consulta
- `$location`: objeto de localização completo

## Próximas etapas

- [Visualizações](../README.md): compare os formatos que uma página pode usar
- [Frontend](../../guides/frontend.md): Vite e a construção do cliente