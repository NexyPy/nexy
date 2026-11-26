# Como funcionam as transições de página?

Nexy usa a API View Transitions do navegador para navegações do cliente, portanto, um navegador compatível anima a troca de página, a menos que o visitante prefira movimento reduzido.

## Quando uma transição é executada

O primeiro documento é uma resposta normal do servidor e não possui transição. A partir daí, cada navegação realizada pelo roteador cliente troca a página dentro de `document.startViewTransition()`: um link para uma rota do cliente, `router.push()` ou `router.replace()`, e os botões voltar e avançar. O roteador renderiza primeiro a próxima página e seus layouts e, em seguida, move a URL, para que a nova página esteja pronta antes de ser exibida.

React, Preact, Solid, Vue e Svelte compartilham o mesmo roteador, portanto o comportamento é o mesmo em todos os cinco adaptadores. Não há configuração para ativar transições.

## Quando cai de volta

- Um navegador sem `startViewTransition()` renderiza a página diretamente.
- Com `prefers-reduced-motion: reduce`, o roteador renderiza a página diretamente.
- Uma transição ignorada por uma navegação mais recente não registra um erro: a página ainda está correta.

A URL, o histórico, a posição de rolagem e o evento `nexy:navigated` se comportam da mesma maneira com ou sem transição.

## Estilize a transição

Nexy não fornece CSS de animação. O navegador aplica seu cross-fade padrão, que você pode substituir em sua própria folha de estilo:

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 250ms;
}
```

## Próximas etapas

- [Vinculando e navegando](linking-and-navigating.md)
- [Ganchos](hooks.md)
