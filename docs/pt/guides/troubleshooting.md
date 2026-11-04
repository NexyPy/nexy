# Solução de problemas

Os problemas que as pessoas enfrentam primeiro, com o que você vê e o que fazer. Cada um vem de uma corrida real.

## Uma página responde 404 mas seu arquivo existe

Veja o terminal que executa `nx dev` ou `nx start`. Quando uma página não pode ser importada, Nexy relata
o erro com seu arquivo e linha, e a rota não está registrada:

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

Corrija a importação nomeada lá. As causas usuais são um componente cujo nome de função não corresponde
o que você importa (veja o próximo item) e um erro de digitação no caminho.

## Uma página `.nexy` não compila: "Erro de análise lógica"

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

Um componente `.nexy` é importado como um módulo Python, portanto, seu nome de arquivo deve ser um nome válido. Um hífen
não é. Nomeie-o em PascalCase, `LivePanel.nexy` e importe-o com o mesmo nome:

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## Um componente renderiza seus filhos como o texto `<slot />`

Um componente `.nexy` coloca seus filhos com `<Slot />`, com S maiúsculo. Um `<slot />` minúsculo é
deixado na página como está. O Vue, que possui seu próprio `<slot />`, não é afetado.

## Uma prop mostra o nome da variável

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

Um atributo sem colchetes é o texto. Coloque a expressão Jinja no atributo para passar um cálculo
valor.

## Um valor em `{{ ... }}` fica vazio

Jinja2 esconde uma variável indefinida. Declare todas as propriedades que você usa no frontmatter
(`title: prop[str] = ""`) e verifique a ortografia.

## As classes utilitárias não têm efeito em uma página `.nexy` (UnoCSS)

UnoCSS lê um arquivo somente quando sua extensão está em seu pipeline de conteúdo. Um projeto de servidor criado
por `nx new` com UnoCSS já lista `.nexy`; um mais velho precisa disso em `uno.config.ts`:

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

Tailwind encontra `.nexy` arquivos por conta própria.

## Uma página `.mdx` solicita pacotes

```text
[nexy] MDX support requires optional packages that are not installed.
```

Instale-os no projeto: `@mdx-js/rollup`, `remark-gfm` e `@mdx-js/react` (mais
`@mdx-js/esbuild` para `nx build`). MDX precisa de React ou Preact em `useFF`. Sem uma estrutura de cliente,
escreva a página como `.md`. Consulte [Markdown e MDX](../views/nexy/markdown.md).

## `No module named 'sqlmodel'` (ou qualquer pacote) quando um comando é iniciado

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

O comando foi executado no Python errado. Os pacotes do seu projeto (seu ORM, suas bibliotecas) estão em
seu `.venv`, e `uvx nexy` ou um `nexy` global é executado em um ambiente próprio que não possui nenhum dos
eles.

Ative o ambiente virtual do projeto, na pasta do projeto, e execute novamente o comando:

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

O prompt começa com `(.venv)` quando está ativo. Ou pule a ativação com
`uv run nexy dev`. Se o pacote estiver realmente faltando no projeto, adicione-o com `uv add sqlmodel`.

## `nx dev` mostra um erro e espera

Quando sua aplicação não pode ser iniciada, `nx dev` informa o motivo e aguarda a próxima alteração no arquivo; isso acontece
não sair. Corrija o arquivo e salve. Apenas Ctrl+C interrompe isso.

## A porta está ocupada

`nx dev` pega a próxima porta livre e a imprime. Para escolher um, use `--port` ou defina `usePort` em
`nexyconfig.py`.

## O tema pisca em branco em uma página escura

O tema salvo deve ser aplicado antes da primeira pintura. Mantenha o pequeno script do starter no
`<head>` do layout raiz e coloque `suppressHydrationWarning` em `<html>` no React.

## Ainda preso

- Leia a página do recurso no [índice da documentação](../README.md).
- Se os documentos e o código discordam, o código está certo: abra um
  [problema](https://github.com/NexyPy/nexy/issues) nomeando a página.