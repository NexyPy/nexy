# Páginas

Um arquivo de página retorna HTML. O tipo de arquivo que você usa altera a forma como ele é produzido: consulte
[visualizações](../../../views/README.md). Esta seção cobre as regras de roteamento que se aplicam a cada página
formato.

| Página | O que cobre |
|---|---|
| [Rotas dinâmicas](dynamic-routes.md) | `[slug]`, `[...path]`, grupos de rotas, segmentos digitados |
| [Páginas de erro](../errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON para clientes API |
| [Layouts](../layouts/README.md) | Uma página por tipo de arquivo de layout |
| [Herança](../inheritance.md) | Como layouts e dependências se acumulam |

## Uma página mínima

```nexy filename="src/rotas/about.nexy"
---
title: prop[str] = "About"
---
<h1>{{ title }}</h1>
```

É servido em `/about`. O frontmatter entre as `---` linhas é Python; a marcação abaixo é
Jinja2. Consulte [arquivos .nexy](../../../views/nexy/README.md).

## Formatos de página

| Modo | Arquivo | Produz |
|---|---|---|
| Servidor | `.nexy` | HTML renderizado por servidor de Python e Jinja2 |
| Servidor | `.md`, `.mdx` | páginas de conteúdo |
| Cliente | `.tsx`, `.jsx`, `.vue`, `.svelte` | componentes do framework, renderizados e navegados no navegador |

Os dois modos não podem ser misturados em um projeto. Consulte [Modo servidor e modo cliente](../modes.md).
Os componentes do cliente ainda podem aparecer no modo servidor, como [ilhas](../../../rendering/islands.md)
dentro de uma página `.nexy`.

## Cache incremental

Adicione `revalidate = 60` a uma página `.nexy` para armazená-la em cache com obsoleto enquanto revalida. Veja
[ISR](../../../rendering/isr.md).

## Lendo a solicitação

Uma página lê o caminho, a string de consulta, os cookies e a sessão por meio de ganchos. Veja
[Ganchos](../navigation/hooks.md).

## Próximas etapas

- [Rotas dinâmicas](dynamic-routes.md)
- [Páginas de erro](../errors/README.md)
- [Roteamento modular](../../modular/README.md): controladores em vez de arquivos