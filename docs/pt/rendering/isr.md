# ISR (obsoleto enquanto revalidado)

## Definição

O ISR armazena em cache o HTML de uma página, por URL, e o veicula até que sua janela expire. A cópia expirada ainda é veiculada enquanto uma nova é renderizada em segundo plano: isto é *obsoleto enquanto revalida*.

## Como funciona

`revalidate = N` no frontmatter de uma página `.nexy` ativa-o. `N` é um número de segundos; um valor ausente, zero ou negativo significa que não há cache algum.

A chave de cache é apenas o **caminho da solicitação** - `request.scope["path"]`. A string de consulta não faz parte dela.

| Qual | Valor |
|---|---|
| Digite | o caminho do URL (`/blog/hello`) |
| Armazenamento | na memória, no processo que renderiza a página |
| Limite | 256 entradas por processo, menos usadas recentemente despejadas |
| Cabeçalho de resposta | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

## Ciclo de vida de renderização

1. Chega uma solicitação para uma página que declara `revalidate`.
2. Nenhuma entrada ainda: a página é renderizada, armazenada e retornada.
3. Entrada menor que `N` segundos: retornada como está, a página não é renderizada.
4. Entrada com mais de `N` segundos: a entrada **obsoleta** é retornada imediatamente e uma tarefa em segundo plano renderiza uma nova.
5. Se a renderização em segundo plano aumentar, a entrada obsoleta permanecerá e a próxima solicitação obsoleta tentará novamente.

## Quando usar

- O mesmo HTML para cada visitante: uma postagem no blog, uma página de produto, uma página de documentação.
- A página é lida com frequência e raramente muda.
- Os dados podem ter alguns segundos sem que ninguém perceba.

## Configuração

```nexy filename="src/rotas/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

`N` é um número inteiro simples. Não há substituição por rota em outro lugar, e os manipuladores `.py` não são páginas: eles nunca entram neste cache.

## Exemplo

Uma postagem de blog que lê um banco de dados:

```nexy filename="src/rotas/blog/[slug].nexy"
---
revalidate = 300
slug: prop[str] = "untitled"
posts = {"hello": {"title": "Hello"}, "other": {"title": "Other"}}
post = posts.get(slug, {"title": "Untitled"})
---
<h1>{{ post.title }}</h1>
```

A primeira solicitação para `/blog/hello` renderizar e armazenar. Os próximos 300 segundos são servidos na memória. `/blog/other` é uma entrada separada, renderizada e armazenada por conta própria. Em um projeto real `posts` vem de um banco de dados ou serviço, chamado uma vez por regeneração.

## Limitações

**Nexy garante** que a chave do cache é o caminho, a cópia obsoleta é servida durante a regeneração e o armazenamento é limitado e seguro para threads.

**Por convenção**, uma página que declara `revalidate` é conteúdo público. Escreva como se todos os visitantes vissem o mesmo HTML.

**Sua aplicação é responsável por** todo o resto:

| Limite | O que significa |
|---|---|
| String de consulta ignorada | `/search?q=a` e `/search?q=b` compartilham uma entrada. Não armazene em cache uma página de pesquisa. |
| Sessão não isolada | A resposta diz `public`, e o HTML do primeiro visitante é servido a todos. Nunca leia a sessão em uma página com `revalidate`. |
| Nenhuma invalidação do lado do servidor | Nada limpa uma entrada antes que sua janela termine. `revalidate(...)` dentro de uma [Action](../guides/actions.md) apenas diz ao **navegador** para recarregar um caminho; ele não toca neste cache. |
| Um cache por processo | Vários trabalhadores mantêm vários caches, com conteúdos diferentes. |
| Regenerações simultâneas | Nada as desduplica: dez solicitações obsoletas podem iniciar dez renderizações. |
| Os erros são silenciosos | Uma regeneração com falha continua servindo a página antiga; a falha é registrada, não retornada. |

## Próximas etapas

- [SSR](ssr.md): como a página é renderizada antes de ser armazenada em cache
- [Actions](../guides/actions.md): o cabeçalho `revalidate` e o que ele não faz
- [Desempenho](../deployment/performance.md)
- [Páginas](../routing/fbr/pages/README.md): layouts e segmentos dinâmicos
