# ISR (obsoleto enquanto revalidado)

## Definição

O ISR armazena em cache o HTML de uma página, por URL, e o veicula até que sua janela expire. A cópia expirada ainda é veiculada enquanto uma nova é renderizada em segundo plano: isto é *obsoleto enquanto revalida*.

## Como funciona

`revalidate = N` no frontmatter de uma página `.nexy` ativa-o. `N` é um número de segundos; um valor ausente, zero ou negativo significa que não há cache algum.

A chave de cache é apenas o **caminho da solicitação** - `request.scope["path"]`. A string de consulta não faz parte dela.

| O que | Valor |
|---|---|
| Chave | o caminho da URL (`/blog/hello`) |
| Armazenamento | selecionado por `useISRCache`: memória por padrão, arquivo, Redis ou um armazenamento personalizado |
| Obrigado | 256 entradas para o armazenamento de memória, usadas menos recentemente, despejadas; arquivo e Redis mantêm entradas até serem invalidados |
| Cabeçalho de resposta | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

Cada resposta ISR carrega esse cabeçalho, incluindo a primeira renderização e uma renderização substituta quando o armazenamento está inativo. Uma CDN pode usá-lo para manter sua própria cópia da mesma URL pública.

## Ciclo de vida de renderização

1. Chega uma solicitação para uma página que declara `revalidate`.
2. Nenhuma entrada ainda: a página é renderizada, armazenada e retornada.
3. Entrada menor que `N` segundos: retornada como está, a página não é renderizada.
4. Entrada com mais de `N` segundos: a entrada **obsoleta** é retornada imediatamente e uma tarefa em segundo plano renderiza uma nova.
5. Se a renderização em segundo plano falhar, a entrada obsoleta permanecerá e a próxima solicitação obsoleta tentará novamente.
6. Se o armazenamento falhar, a página será renderizada e retornada sem uma entrada em cache. A solicitação ainda foi bem-sucedida.

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

## Escolha uma loja

Defina `useISRCache` em `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useISRCache = "file"
```

| Valor | Loja | Compartilhado por |
|---|---|---|
| não definido, `None` ou `"memory"` | memória de processo, limitada a 256 entradas | um trabalhador |
| `"file"` | Arquivos JSON em `.nexy/isr` | trabalhadores em um host |
| `{"type": "file", "directory": ".cache/isr"}` | Arquivos JSON no diretório fornecido | trabalhadores em um host |
| `"redis"` | Redis em `redis://localhost:6379/0` | qualquer trabalhador que chegue ao servidor |
| `{"type": "redis", "url": "redis://cache:6379/0"}` | Redis nesse URL | qualquer trabalhador que chegue ao servidor |
| `{"type": "redis", "client": client}` | o cliente Redis que você passa | qualquer trabalhador que chegue ao servidor |
| um objeto com `get`, `set` e `invalidate` | sua própria loja | o que quer que compartilhe |

A loja Redis precisa do pacote do cliente: `uv add redis`. Não é instalado com Nexy. Uma loja personalizada implementa o protocolo `ISRCache` de `nexy.modules.runtime.cache`; seu `get` retorna um `CacheEntry` ou `None`.

As entradas do arquivo são escritas atomicamente, de modo que um trabalhador nunca lê uma página escrita pela metade. Os trabalhadores que usam o mesmo diretório ou o mesmo servidor Redis leem a mesma entrada. Uma loja quebrada custa apenas uma renderização: ela nunca responde à solicitação com erro.

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

A primeira solicitação para `/blog/hello` renderizar e armazenar. Os próximos 300 segundos são servidos na loja selecionada. `/blog/other` é uma entrada separada, renderizada e armazenada por conta própria. Em um projeto real `posts` vem de um banco de dados ou serviço, chamado uma vez por regeneração.

## O que uma CDN pode e não pode compartilhar

Um CDN que honra `cache-control` pode manter uma cópia de `/blog/hello` por `s-maxage` segundos e servi-la enquanto é revalidada. Ele compartilha essa cópia entre visitantes e funcionários porque a resposta diz `public`.

Um CDN não conhece a loja Nexy. `revalidate()` em uma [Ação](../guides/actions.md) remove a entrada do armazenamento Nexy configurado, mas não limpa um CDN. A CDN mantém sua cópia até que sua própria janela termine ou até que você configure sua eliminação.

Não forneça a uma CDN uma página cujo HTML dependa do visitante. A resposta diz `public`, e a chave do Nexy é apenas o caminho: duas strings de consulta em um caminho compartilham uma entrada. Uma sessão, um cookie ou um ID de usuário no HTML pode ser servido a outro visitante.

## Limitações

**Nexy garante** que a chave do cache é o caminho, a cópia obsoleta é servida durante a regeneração e uma falha de armazenamento retorna para uma renderização.

**Por convenção**, uma página que declara `revalidate` é conteúdo público. Escreva como se todos os visitantes vissem o mesmo HTML.

**Sua aplicação é responsável por** todo o resto:

| Limite | O que isso significa |
|---|---|
| String de consulta ignorada | `/search?q=a` e `/search?q=b` compartilham uma entrada. Não armazene em cache uma página de pesquisa. |
| Sessão não isolada | A resposta diz `public`, e o HTML do primeiro visitante é servido a todos. Nunca leia a sessão em uma página com `revalidate`. |
| CDN não eliminado | `revalidate()` limpa a loja Nexy, não um CDN ou outro proxy na frente dela. |
| Sem TTL em armazenamentos de arquivos e Redis | As entradas permanecem até `revalidate()` ou sua própria limpeza as remove. O armazenamento de memória despeja a entrada usada menos recentemente após 256. |
| Regenerações simultâneas | Nada os desduplica: dez solicitações obsoletas podem iniciar dez renderizações. |
| Erros são silenciosos | Uma operação de regeneração ou armazenamento com falha continua servindo a página; a falha não é retornada. |

## Próximas etapas

- [SSR](ssr.md): como a página é renderizada antes de ser armazenada em cache
- [Ações](../guides/actions.md): o cabeçalho `revalidate` e a invalidação da loja
- [Configuração](../reference/config.md#server): `useISRCache`
- [Desempenho](../deployment/performance.md)
- [Páginas](../routing/fbr/pages/README.md): layouts e segmentos dinâmicos
