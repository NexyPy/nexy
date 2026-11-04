# .nexy arquivos

Um arquivo `.nexy` é um componente: Python na parte superior, HTML no meio, CSS na parte inferior.

**Antes de começar:** um projeto criado pelo [Início rápido](../../getting-started/quick-start.md).
Um arquivo `.nexy` não precisa de configuração de compilação: `nx dev` compila-o ao salvar.

```nexy filename="src/rotas/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

## Princípio

Tudo entre as duas `---` linhas é Python. As importações são resolvidas quando o componente é
compilado; o restante é executado para cada solicitação, para que possa ler o estado da solicitação.

| O que | Exemplo |
|---|---|
| Importar um módulo | `import json`, `from datetime import datetime` |
| Importar um componente | `from "@/components/card.nexy" import Card` |
| Declarar uma propriedade | `title: prop[str] = "Default"` |
| Calcular um valor | `year = datetime.now().year` |
| Leia a solicitação | `pathname = usePathname()` |
| Armazenar a página em cache (ISR) | `revalidate = 60` |

## Propriedades

As propriedades são a API do componente. `prop[type]` declara o tipo, `= value` fornece um padrão. Um
propriedade sem padrão deve ser passada pelo pai.

As importações que começam com um alias são resolvidas através de `useAliases`. A configuração `nx new` escreve mapas
`@` a `src`, o que faz com que `@/components/card.nexy` signifique `src/components/card.nexy`.

## Modelo

Abaixo do frontmatter está HTML com Jinja2. Variáveis ​​do frontmatter e as propriedades estão em
escopo.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

O escape automático está **desativado**: os modelos são o próprio HTML do projeto, então `{{ value }}` é inserido como
escrito. Fuja de valores não confiáveis ​​com `{{ value | e }}`. `| safe` portanto não muda nada.

> [!NOTA]
> envolver JavaScript que contém `{{` ou `{%` em `{% raw %}...{% endraw %}`.
> Frameworks como Vue e Svelte usam os mesmos colchetes.

## Componentes

Qualquer callable importado cujo nome comece com uma letra maiúscula pode ser usado como tag. O compilador
reescreve-o em uma chamada Jinja: os atributos tornam-se argumentos de palavras-chave.

```nexy filename="src/rotas/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```

A última linha é exatamente `{{ Audio("/theme.mp3", controls=True) }}`. Ambas as sintaxes são válidas para o
ajudantes integrados `Image`, `Link`, `Audio` e `Video` - consulte
[componentes](components.md#two-syntaxes-one-function).

Os filhos são renderizados por meio de `<Slot />` (S maiúsculo) dentro do componente filho e por meio de `{{ children }}`
dentro de um layout.

Passe um valor computado com Jinja dentro do atributo: `<Icon path="{{ icon }}" size="{{ size }}" />`.
Um nome simples como `path=icon` é o texto `icon`, não a variável. Para dar um CSS a um componente
class, declare uma prop `class_name`: `class` é uma palavra-chave Python.

> [!NOTA]
> uma tag auxiliar sempre fecha automaticamente. Passar conteúdo para `Link` passa por seu
Argumento > `children` (`<Link href="/about" children="About" />`), não por meio do conteúdo do elemento.

## Estilos

`<style>` blocos são emitidos com a página que os declara. Eles não têm escopo: um nome de classe
usado em dois componentes é uma classe. Prefixe ou crie um namespace para suas classes.

## Regras que economizam tempo

- Um componente por arquivo. O nome do arquivo é o nome do componente, em PascalCase (`CopyChip.nexy`). Um
  O componente `.nexy` é importado como um módulo Python: um hífen no nome (`copy-chip.nexy`) não
  compilar.
- Declare props antes de usá-los: uma variável não declarada é renderizada como uma string vazia, porque
  O indefinido de Jinja2 é silencioso aqui.
- Mantenha os efeitos colaterais dentro das funções - o frontmatter é executado novamente a cada solicitação.

## Próximas etapas

- [Markdown e MDX](markdown.md): páginas de conteúdo
- [ISR](../../rendering/isr.md): armazena em cache uma página por caminho
- [CSR](../../rendering/csr.md): renderização do lado do cliente