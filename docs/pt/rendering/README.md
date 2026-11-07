# Renderização

A renderização responde a uma pergunta: **quem produz o HTML e quando**. Nexy tem quatro respostas e um padrão.

**Não tenho certeza? Mantenha o SSR.** Mude uma página apenas quando você puder nomear o motivo: conteúdo que raramente muda (ISR), um widget que precisa do navegador (ilha) ou navegação semelhante a um aplicativo (CSR).

<!-- router:modular -->
> [!NOTE]
> O roteador modular renderiza todas as visualizações no servidor, com ilhas onde uma visualização as contém. ISR e CSR são modos de páginas de arquivo: eles precisam do roteador baseado em arquivo.
<!-- /router -->

## Como funciona

```diagram filename="Quem produz o HTML e quando"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## Os quatro modos

| | RSS | ISR | RSE | Ilhas |
|---|---|---|---|---|
| Os dados são lidos | em cada pedido | em cada regeneração | no navegador | em cada pedido |
| O HTML vem de | o servidor | o servidor, depois um cache | o servidor para o primeiro documento, o navegador depois | o servidor |
| JavaScript | apenas para ilhas | apenas para ilhas | o pacote de estrutura | só a ilha |
| Hidratação | nenhum | nenhum | todo o documento | a ilha |
| Cache | nenhum | por URL, na memória | nenhum | nenhum |
| Decidido por | padrão | `revalidate = N` na página | `useCSR = True` no projeto | `directive` no componente |
| Grão | página | página | **projeto** | componente |

## Ciclo de vida de renderização

Dois fatos explicam a maioria das surpresas.

1. **Um projeto está em um modo.** `useCSR` escolhe entre o modo servidor (SSR, ISR, ilhas, `.nexy`, `.md`, `.mdx` rotas) e modo cliente (rotas de estrutura e um roteador cliente). Os dois não podem ser misturados: consulte [modo servidor e modo cliente](../routing/fbr/modes.md).
2. **Dentro do modo servidor, o modo é por página.** Uma página pode ser armazenada em cache com `revalidate`, outra pode conter uma ilha, uma terceira não pode fazer nenhuma das duas.

O modo cliente ainda envia um documento real: Nexy o renderiza no Node para a primeira resposta, então o navegador assume a navegação. Uma página CSR não é uma página em branco aguardando um pacote.

## Quando usar

- **Conteúdo, marketing, documentação**: SSR, mais ISR quando o conteúdo raramente muda.
- **Uma página quase toda estática com um widget interativo**: SSR com uma ilha.
- **Painéis, editores, navegação semelhante a um aplicativo**: CSR.
- **Uma página lida constantemente e raramente alterada**: ISR.

## Configuração

| Modo | Onde |
|---|---|
| RSS | em lugar nenhum: é o padrão |
| ISR | `revalidate = 60` no cabeçalho de uma página `.nexy` |
| RSE | `useCSR = True` em `nexyconfig.py`, com `useFF` definido |
| Ilhas | `directive="client:visible"` na tag do componente |

## Exemplo

<!-- router:fbr,custom -->
```nexy filename="src/rotas/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

A mesma página sem a linha frontmatter é SSR.
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Rendered on every request</h1>
<Chart directive="client:visible" />
```

A visualização é SSR e o gráfico é uma ilha que se hidrata quando aparece.
<!-- /router -->

## Limitações

- **Não há modo SSG.** Nexy pré-renderiza HTML em tempo de construção (componente HTML, documentos do cliente), mas sempre o lê de volta através do servidor: sem comando de exportação, sem pasta autônoma para hospedar estaticamente. Para conteúdo congelado, use ISR com uma janela longa.
- **ISR não é um CDN.** O cache reside no processo que renderiza a página; vários trabalhadores mantêm vários caches. Veja [ISR](isr.md).
- **O CSR é uma decisão do projeto.** Você não pode criar um CSR de uma página e manter o restante do SSR.
- **As ilhas hidratam a ilha, não a página.** Uma página cujas ilhas dependem umas das outras é uma página de RSE disfarçada.

## Próximas etapas

- [SSR](ssr.md): o padrão
- [ISR](isr.md): armazenar em cache uma página por URL
- [CSR](csr.md): navegação manual para o navegador
- [Ilhas](islands.md): hidratar um widget
- [Desempenho](../deployment/performance.md)
