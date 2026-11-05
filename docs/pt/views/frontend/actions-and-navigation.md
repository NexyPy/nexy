# Ações e navegação

A interação no Nexy é feita por meio de um sistema unificado de **Ações** e **Navegação**, garantindo que o frontend e o backend permaneçam sincronizados sem código de colagem manual da API.

## O Contrato de Ação

Uma **Action** é uma função do lado do servidor que lida com uma mutação (por exemplo, atualizar um banco de dados). 

1.  **Entrada digitada**: As ações são definidas em Python com dicas de tipo. Nexy gera um cliente TypeScript correspondente, para que você obtenha preenchimento automático e validação em seu IDE.
2.  **Execução Atômica**: Uma ação é uma única solicitação `POST`.
3.  **Tratamento de resultados**: As ações retornam um resultado digitado que o cliente pode usar para atualizar a UI.

## Navegação do lado do cliente

A navegação no Nexy é "inteligente". Em vez de recarregar completamente o navegador, o Nexy troca o conteúdo da página atual enquanto mantém os layouts ativos montados.

- **O `Link` Componente**: Use o componente específico da estrutura `Link` para realizar transições do lado do cliente.
- **Navegação programática**: Use a função `navigate()` de `@nexy/client` para alterar páginas em resposta à lógica (por exemplo, após um login bem-sucedido).

## Coordenação: Ação → Navegação

O padrão mais comum é executar uma ação e então direcionar o usuário para uma nova página.

**O fluxo de revalidação:**
1.  O cliente chama uma ação.
2.  A Action é executada no servidor e chama `revalidate("/path")`.
3.  O servidor retorna o resultado junto com um sinal para atualizar o caminho especificado.
4.  O cliente atualiza o conteúdo da página para refletir o novo estado.

## Implementação da Estrutura

A API para chamar ações e navegar varia de acordo com a estrutura. Consulte o guia **Diferenças** da tecnologia escolhida:

- [React Diferenças](../react/differences.md)
- [Vue Diferenças](../vue/differences.md)
- [Svelte Diferenças](../svelte/differences.md)
- [Solid Diferenças](../solid/differences.md)
- [Preact Diferenças](../preact/differences.md)
