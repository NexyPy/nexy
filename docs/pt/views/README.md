# Visualizações

Antes de escolher um formato de arquivo, é importante distinguir entre como o Nexy lida com os recursos e como ele os renderiza.

| Termo | Definição |
|---|---|
| **Page** | Um recurso endereçável por URL do aplicativo. É definido por um arquivo em `src/routes/`. |
| **View** | O processo de produção do corpo de resposta para uma página. Uma visualização transforma lógica e dados em HTML ou JSON. |
| **Componente** | Um bloco de construção de UI reutilizável usado para compor uma visualização. Os componentes podem ser auxiliares nativos do Nexy ou específicos da estrutura (React, Vue, etc.). |
| **Manipulador de rota** | Uma função Python que trata uma solicitação HTTP para um método específico (por exemplo, `GET`, `POST`). |
| **Endpoint** | A combinação exclusiva de uma URL e um método HTTP que um manipulador de rota responde. |

**Não tenho certeza? Escreva um arquivo `.nexy`.** Ele não precisa de estrutura de cliente e você pode adicionar um componente React, Vue, Svelte, Solid ou Preact dentro dele posteriormente, como uma ilha.

```diagram filename="Qual arquivo para qual página"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## Formatos

| Formato | Arquivo | Renderização do servidor | Estrutura do cliente | Notas |
|---|---|---|---|---|
| `.nexy` | [.arquivos .nexy](nexy/README.md) | Jinja2 + Python lógica, transmitida | opcional | Formato de página Nexy nativo |
| `.md` | [Markdown e MDX](nexy/markdown.md) | cmarkgfm no momento da solicitação | opcional via layout | Puro Markdown, GFM, layout-wrapped |
| `.mdx` | [Markdown e MDX](nexy/markdown.md) | framework SSR | React ou Preact | Markdown com componentes |
| `.tsx` | [React](react/differences.md), [Solid](solid/differences.md) ou [Preact](preact/differences.md) | modo cliente: a estrutura, renderizada no nó | React, Solid ou Preact | Rotas de componentes |
| `.vue` | [Vue](vue/differences.md) | modo cliente: a estrutura, renderizada no nó | Vue | rotas SFC |
| `.svelte` | [Svelte](svelte/differences.md) | modo cliente: a estrutura, renderizada no nó | Svelte | rotas SFC |

Auxiliares integrados `Image`, `Link`, `Audio`, `Video` e `Import`: [Componentes](nexy/components.md).

## Misturando formatos

Você pode misturar diferentes tecnologias dentro do mesmo projeto:
- **Ilhas**: Você pode importar um componente React ou Vue dentro de uma página `.nexy`. O servidor renderiza o shell e a estrutura hidrata o componente no cliente.
- **Lógica compartilhada**: Manipuladores de rota em arquivos `.py` podem fornecer dados para páginas em qualquer formato por meio do estado compartilhado do aplicativo ou chamadas de API.

## Habilitar uma estrutura

Defina `useFF` em `nexyconfig.py` e execute `nexy new` para adicionar dependências:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

Com uma estrutura habilitada, Vite lida com seus pacotes de clientes. No modo cliente suas extensões tornam-se rotas; no modo servidor, os mesmos arquivos são componentes que você importa como ilhas - um arquivo de estrutura em `src/routes/` é rejeitado lá. Consulte [modo servidor e modo cliente](../routing/fbr/modes.md).

> [!NOTE]
> no modo [CSR](../rendering/csr.md), apenas os arquivos de rota da estrutura são navegáveis ​​no lado do cliente.

## Layouts

Um `layout.*` em um diretório agrupa as páginas abaixo dele. Consulte [layouts](../routing/fbr/layouts/README.md).

## Próximas etapas

- [.arquivos nexy](nexy/README.md): Python + Jinja2 + adereços
- [Markdown e MDX](nexy/markdown.md): páginas de conteúdo
- [Componentes](nexy/components.md): auxiliares HTML integrados
