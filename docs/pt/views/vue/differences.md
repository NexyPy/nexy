# Vue

Nexy renderiza Vue 3 componentes de arquivo único no servidor e, em seguida, Vue os assume no navegador. Páginas, layouts, ilhas e ações são iguais em todos os frameworks: esta página cobre a configuração e depois as partes que diferem dos [contratos compartilhados](../frontend/pages.md).

<!-- router:fbr,custom -->
| Modo | `nexyconfig.py` | As páginas são | Vue é |
|---|---|---|---|
| Servidor (padrão) | `useCSR = False` | `.nexy` arquivos | [ilhas](../../rendering/islands.md) dentro dessas páginas |
| Cliente | `useCSR = True` | `.vue` arquivos | a página inteira, com [layouts](../frontend/layouts.md) e um roteador cliente |
<!-- /router -->

<!-- router:modular -->
Com o roteador modular, Vue componentes são [ilhas](../../rendering/islands.md) dentro das `.nexy` visualizações que um controlador retorna: não há arquivo de paginação e nenhum roteador cliente.
<!-- /router -->

## Iniciar um projeto

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-vue
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-vue
```
<!-- /router -->

O modelo é um projeto em modo servidor com Vue ilhas. Execute `nx new my-app` sem um modelo para responder aos prompts: o roteador, o tipo de projeto, se deve usar roteamento do lado do cliente e, em seguida, a estrutura.

## Habilite Vue em um projeto existente

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` grava este arquivo; Nexy escreve `__nexy__/vite.ts` sozinho, então não o edite.

| Pacote | Versão `nx new` escreve |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## Regras

- **Uma estrutura por projeto.** `useFF` leva exatamente uma estrutura; `useFF = [vue(), react()]` interrompe o servidor na inicialização.
- **Um componente por arquivo.** Um arquivo `.vue` exporta seu componente como padrão; o nome com o qual você o importa é apenas a tag que você escreve.
<!-- router:fbr,custom -->
- **Os componentes ficam fora de `src/routes/`**, geralmente em `src/components/`, portanto não são páginas.
- **Um projeto em modo servidor não tem página `.vue`**, e um projeto em modo cliente não tem página `.nexy`: Nexy se recusa a iniciar e nomeia o arquivo. Veja [modos](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Os componentes residem em `src/components/`**, e uma visualização os importa como ilhas.
<!-- /router -->

<!-- router:fbr,custom -->
## Páginas

No modo cliente (`useCSR = True`), uma página é um arquivo `.vue`.

### Componente de página

A página é o componente definido pelo bloco `<script setup>`.

```vue filename="src/rotas/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### Segmentos dinâmicos

Os parâmetros de URL chegam à página como acessórios. Você pode declará-los usando `defineProps`:

```vue filename="src/rotas/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Alternativamente, use o gancho `useParams` de `@nexy/client` em qualquer componente.

## Layouts

### Implementação

O layout raiz define o shell do documento. Os layouts aninhados envolvem o conteúdo em seu slot padrão.

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```
<!-- /router -->

## Ilhas

No modo servidor, um componente Vue importado para um arquivo `.nexy` é uma ilha.

### Importando

Importe componentes no frontmatter do arquivo `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/rotas/index.nexy"
---
from "@/components/Counter.vue" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.vue" import Counter
---
<Counter start=3 />
```
<!-- /router -->

### Diretrizes de hidratação

Use a propriedade `directive` para controlar quando a ilha hidrata:

- `client:load` (padrão): imediatamente
- `client:idle`: quando o navegador está ocioso
- `client:visible`: quando rola para visualização
- `client:media`: quando a consulta de mídia corresponde

## Ações e navegação

### Chamando ações

Use o gancho `useAction` para gerenciar o estado de uma chamada de ação. Em Vue, o estado retornado (`pending`, `data`, `error`) são referências calculadas.

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### Navegação

Use o componente `Link` para transições do lado do cliente:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

Para navegação programática, use o gancho `useRouter`:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Acesso URL

Todos os ganchos de localização retornam referências computadas:

- `usePathname()`: caminho atual
- `useParams()`: segmentos dinâmicos
- `useSearchParams()`: string de consulta
- `useLocation()`: objeto de localização completo

## Próximas etapas

- [Visualizações](../README.md): compare os formatos que uma página pode usar
- [Frontend](../../guides/frontend.md): Vite e a construção do cliente
