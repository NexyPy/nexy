# Componentes

Nexy exporta um pequeno conjunto de auxiliares que retornam strings HTML. Cada um é usado de duas maneiras em um
Modelo `.nexy`: como uma chamada Jinja ou como uma tag estilo HTML.

## Duas sintaxes, uma função

```nexy filename="src/rotas/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

Ambas as linhas produzem a mesma marcação:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

O compilador reescreve `<Audio ... />` para `{{ Audio(...) }}`, portanto o formato da tag não é uma segunda API:
atributos são os argumentos de palavra-chave da função.

## Regras do formulário de tag

| Na tag | Torna-se |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, um verdadeiro booleano |
| `width=640` | `width=640`, um número |
| `src="{{ url }}"` | `src=(url)`, avaliado em Jinja |
| qualquer outro `value` | `"value"`, uma string |

- A tag deve iniciar com letra maiúscula e ser importada no frontmatter; caso contrário, o
  compilador aumenta `Missing Import: <Name> used but not declared.`
- O formato da tag é **de fechamento automático**. `<Audio src="/a.mp3" />` e
  `{{ Audio("/a.mp3") }}` são equivalentes; escrever filhos dentro de uma tag auxiliar não é suportado.
- Um atributo HTML simples não é um booleano aqui: `controls` torna-se `controls=""`, o que é falso.
  Escreva `controls=True`.

> [!NOTA]
> `class_name` é a palavra-chave documentada para classes CSS. Argumentos extras de palavras-chave
> tornam-se atributos HTML, então `class="nav"` também atinge a saída.

## Imagem

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` renderiza um
`<img>` com carregamento lento por padrão.

## Link

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` renderiza um `<a data-nexy-link>`
manipulado pelo roteador cliente. Com `prefetch=True`, passar o mouse ou tocar no link aquece o alvo
através de `window.__nexy_prefetch`.

> [!NOTA]
> o formato da tag leva o rótulo como `children`, não como conteúdo do elemento:
> `<Link href="/about" children="About" />`. Para colocar marcação dentro de um link, use o formulário de chamada com
> `children=` ou um componente `.nexy` que renderiza um `<Slot />`.

## Áudio e Vídeo

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Áudio(src, controles=True, autoplay=False, loop=False, muted=False, preload="metadata",
class_name=Nenhum, fontes=Nenhum, **attrs)` and `Video(src, largura=Nenhum, altura=Nenhum, ...)` renderizar nativo
jogadores. `sources` adiciona tags `<source>` com o tipo MIME derivado de cada extensão.

## Um componente que você mesmo escreve

Um componente reutilizável `.nexy` é um arquivo em `src/components/`: Python props no topo, HTML abaixo.
É importado como qualquer outro módulo Python.

```nexy filename="src/componentes/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rotas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```

`title` não tem padrão, então a página deve passá-lo; `tone` volta para `"neutral"`. A marcação
entre as tags chega dentro de `<Slot />` (S maiúsculo). Veja
[.arquivos nexy](README.md#components) para adereços, slots e as regras do formulário de tag.

## Importando um componente cliente

De um arquivo `.nexy`, importe um componente da estrutura por caminho; o compilador monta-o no cliente e
passa os atributos como adereços:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` faz o mesmo em Python:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

A mesma sintaxe de importação resolve `.json`, `.css` e arquivos de imagem para seus URLs.

## Modelo e Vite

`Template().render(path, context)` renderiza um arquivo de modelo (Jinja2 ou Markdown renderizado em HTML para
`.md` rotas). `Template().invalidate(path)` remove-o do cache.

`Vite()` retorna as tags do cliente para o modo atual: o script HMR em desenvolvimento, o compilado
pacote do cliente em produção. Nexy chama isso para cada página; você raramente precisa dele diretamente.

## Ainda não implementado

`Form` e `Script` são espaços reservados exportados sem comportamento. Não confie neles.

## Próximas etapas

- [.arquivos nexy](README.md): onde esses auxiliares são usados
- [React](../react/differences.md): importando `.tsx` componentes
- [Frontend](../../guides/frontend.md): como os componentes do cliente são agrupados