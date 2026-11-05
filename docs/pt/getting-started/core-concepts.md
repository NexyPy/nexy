# Conceitos centrais

As palavras que o restante dos documentos usam – rota, página, visualização, componente, manipulador, endpoint – cada uma em uma linha, com um link para a página que se aprofunda. Novo no Nexy? Comece com [O que é Nexy?](what-is-nexy.md).

## Como ler esses documentos

| Nível | A pergunta que ele responde | Comece com |
|---|---|---|
| Arquitetura de aplicativo | qual camada responde a uma solicitação e o que ela se recusa a fazer | [Como funciona o Nexy](how-nexy-works.md) |
| Estrutura do aplicativo | onde fica o código e o que um arquivo se torna | [Estrutura do projeto](project-structure.md) |
| Apresentação e renderização | o que o leitor vê e quem produz o HTML | [Visualizações](../views/README.md), [Renderização](../rendering/README.md) |
| Interação do aplicativo | o que o leitor faz e o que é executado em resposta | [Ações](../guides/actions.md) |

Os níveis são lidos nessa ordem uma vez. Depois disso, a página que você precisa é uma pesquisa, não um curso.

## Arquitetura de aplicativo

Três maneiras de decidir qual código responde a uma URL. São alternativas, não camadas:

- **Roteamento baseado em arquivo (FBR)**: um arquivo em `src/routes/` é uma rota. O padrão.
- **Roteador modular**: controladores e módulos em `src/apps/`, declarados com decoradores, para uma base de código estilo NestJS.
- **Roteador personalizado**: um FastAPI `APIRouter` existente incluído no aplicativo.

A escolha é uma linha de `nexyconfig.py`. O roteamento baseado em arquivo não precisa de nada: sem `useRouter`, Nexy lê `src/routes/`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```

Escolher um dos três é uma decisão. A escolha de uma estrutura de front-end é outra: consulte [Escolha um roteador](../routing/README.md) e [Visualizações](../views/README.md).

## Estrutura do aplicativo

Cinco noções que um leitor vindo de Next.js costuma fundir em uma só. Eles não são a mesma coisa, e a diferença explica a maioria das perguntas "por que minha página não está sendo renderizada".

| Noção | O que é isso | O que não é |
|---|---|---|
| **Rota** | um padrão de URL, produzido pelo caminho de um arquivo | um arquivo: um arquivo pode responder a vários URLs (`[slug]`) |
| **Página** | um arquivo de rota que renderiza uma visualização: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | um endpoint: responde a um documento, não a dados |
| **Ver** | o que produz o corpo de uma página: Jinja2 e Python, Markdown, ou um componente cliente | uma rota: a mesma visualização pode servir diversas páginas |
| **Componente** | uma peça reutilizável que uma página importa | uma rota: no modo servidor, um componente nunca é servido sozinho |
| **Manipulador de rota** | a função de um arquivo de rota `.py`, nomeado após o método HTTP (`GET`, `POST`, …) | uma página: retorna JSON, um arquivo ou um `Response` |
| **Ponto final** | o par (URL, método) que um manipulador responde | um manipulador: um arquivo pode responder a vários endpoints |

Em uma frase: **uma página é um arquivo de rota, uma visualização é o que a renderiza, um componente é o que uma página reutiliza, um manipulador responde a um endpoint.**

Todos os cinco em um pequeno projeto:

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/rotas/blog/[slug].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

O frontmatter e o modelo abaixo dele são a visualização da página; `Like` é o componente que ele reutiliza.

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

Mais duas palavras que voltam em todos os lugares:

- **Layout**: um arquivo `layout.*` que agrupa as páginas abaixo de sua pasta; o root possui o documento HTML. Consulte [Layouts](../routing/fbr/layouts/README.md).
- **Dependência**: função executada antes de um manipulador, aplicada por rota ou por pasta. Consulte [Dependências](../routing/fbr/dependencies/README.md).

## Apresentação e renderização

Duas decisões independentes, muitas vezes confusas:

- **O formato** decide qual arquivo renderiza a página: [Visualizações](../views/README.md).
- **O modo** decide quem produz o HTML e quando: [Renderização](../rendering/README.md).

| Noção | Uma linha |
|---|---|
| Modo servidor | o servidor renderiza páginas `.nexy` e `.md`; componentes são ilhas ([modos](../routing/fbr/modes.md)) |
| Modo cliente | `useCSR = True`: os arquivos do framework são as rotas e a navegação acontece no navegador |
| SSR, ISR, RSE, ilhas | quatro modos de renderização, decididos por página, exceto CSR, que é por projeto ([renderização](../rendering/README.md)) |
| Hidratação | o navegador anexando uma estrutura ao HTML o servidor já enviou ([ilhas](../rendering/islands.md)) |
| Adereços | os valores que um pai passa para um componente, declarado `name: prop[type]` em um arquivo `.nexy` ([arquivos .nexy](../views/nexy/README.md)) |

Uma página em modo servidor com uma ilha: o servidor renderiza a página, o navegador hidrata o gráfico apenas quando ele rola para visualização.

```nexy filename="src/rotas/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

## Interação do aplicativo

| Noção | Uma linha |
|---|---|
| Ação | uma função Python marcada como `@Action`, servida como `POST`, que pode ser chamada de um formulário ou como uma função digitada ([ações](../guides/actions.md)) |
| Formulário | um formulário HTML que posta em uma ação, com erros de validação voltando para a página ([ações](../guides/actions.md)) |
| Navegação | links que fazem pré-busca e ganchos que leem o caminho, a consulta, os cookies e a sessão ([hooks](../routing/fbr/navigation/hooks.md)) |
| Busca de dados | feito pela página ou pelo manipulador que precisa; Nexy não fornece nenhuma camada de dados do cliente ([manipuladores](../routing/fbr/handlers/README.md)) |

Uma ação e o formulário postado nela, que funciona antes do carregamento de qualquer script:

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

```html filename="src/rotas/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```

## O que Nexy não faz

Autenticação, autorização, banco de dados, internacionalização, trabalhos em segundo plano, e-mail, pagamentos e pesquisa são **de responsabilidade da sua aplicação**, e não da estrutura. Nexy dá os pontos de extensão e diz onde conectar cada um: veja [O que Nexy deixa para você](how-nexy-works.md#what-nexy-leaves-to-you).

A autenticação, por exemplo, se conecta a uma dependência da pasta que protege. Nexy o executa antes de cada rota abaixo; quem é o usuário fica com sua decisão:

```python filename="src/routes/account/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

A razão não é o minimalismo por si só: uma estrutura que escolhe seu ORM ou sua biblioteca de autenticação decidiu algo que somente seu aplicativo pode decidir.

## Próximas etapas

- [Estrutura do projeto](project-structure.md): todas as pastas e arquivos de um projeto
- [Glossário](../reference/glossary.md): as mesmas palavras, em um índice alfabético
- [Como funciona o Nexy](how-nexy-works.md): as camadas, quem constrói o quê e o que o Nexy deixa para você
