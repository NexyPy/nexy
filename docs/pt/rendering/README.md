# Renderização

A renderização responde a uma pergunta: **quem produz o HTML e quando**. Nexy tem quatro respostas e uma
padrão.

**Não tem certeza? Mantenha o SSR.** Mude uma página somente quando você souber o motivo: conteúdo que raramente muda
(ISR), um widget que precisa do navegador (ilha) ou navegação semelhante a um aplicativo (CSR).

## Como funciona

```diagram filename="Quem produz o HTML e quando"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## Os quatro modos

| | RSS | ISR | RSC | Ilhas |
|---|---|---|---|---|
| Os dados são lidos | em cada solicitação | em cada regeneração | no navegador | em cada solicitação |
| O HTML vem do | servidor | do servidor, depois um cache | do servidor para o primeiro documento, do navegador depois | do servidor |
| JavaScript | apenas para ilhas | apenas para ilhas | o pacote de estrutura | apenas a ilha |
| Hidratação | nenhuma | nenhuma | todo o documento | a ilha |
| Cache | nenhum | por URL, na memória | nenhum | nenhum |
| Decidido por | padrão | `revalidate = N` na página | `useCSR = True` no projeto | `directive` no componente |
| Grão | página | página | **projeto** | componente |

## Ciclo de vida de renderização

Dois fatos explicam a maioria das surpresas.

1. **Um projeto está em um modo.** `useCSR` escolhe entre o modo de servidor (SSR, ISR, ilhas, `.nexy`,
   `.md`, `.mdx` rotas) e modo cliente (rotas de estrutura e um roteador cliente). Os dois não podem ser
   misto: veja [modo servidor e modo cliente](../routing/fbr/modes.md).
2. **No modo servidor, o modo é por página.** Uma página pode ser armazenada em cache com `revalidate`, outra
   pode controlar uma ilha, um terceiro não pode fazer nenhuma das duas coisas.

O modo cliente ainda envia um documento real: Nexy o renderiza no Node para a primeira resposta, depois o
navegador assume a navegação. Uma página CSR não é uma página em branco aguardando um pacote.

## Quando usar

- **Conteúdo, marketing, documentação**: SSR, mais ISR quando o conteúdo muda raramente.
- **Uma página quase toda estática com um widget interativo**: SSR com uma ilha.
- **Painéis, editores, navegação semelhante a um aplicativo**: CSR.
- **Uma página lida constantemente e raramente alterada**: ISR.

## Configuração

| Modo | Onde |
|---|---|
| SSR | em lugar nenhum: é o padrão |
| ISR | `revalidate = 60` no cabeçalho de uma página `.nexy` |
| CSR | `useCSR = True` em `nexyconfig.py`, com `useFF` definido |
| Ilhas | `directive="client:visible"` na tag do componente |

## Exemplo

```nexy filename="src/rotas/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

A mesma página sem a linha frontmatter é SSR.

## Limitações

- **Não há modo SSG.** Nexy pré-renderiza HTML em tempo de construção (componente HTML, documentos do cliente),
  mas sempre lê de volta através do servidor: sem comando de exportação, sem pasta independente para hospedar
  estaticamente. Para conteúdo congelado, use ISR com uma janela longa.
- **ISR não é um CDN.** O cache reside no processo que renderiza a página; vários trabalhadores mantêm
  vários caches. Consulte [ISR](isr.md).
- **CSR é uma decisão do projeto.** Você não pode criar um CSR de uma página e manter o SSR restante.
- **Ilhas hidratam a ilha, não a página.** Uma página cujas ilhas dependem umas das outras é uma
  Página CSR disfarçada.

## Próximas etapas

- [SSR](ssr.md): o padrão
- [ISR](isr.md): armazenar em cache uma página por URL
- [CSR](csr.md): navegação manual para o navegador
- [Ilhas](islands.md): hidratar um widget
- [Desempenho](../deployment/performance.md)