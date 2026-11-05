# Herança

Vários arquivos em `src/routes/` se aplicam a tudo abaixo de seu diretório. Todos eles resolvem da mesma maneira: Nexy começa no diretório da rota e caminha até `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| Arquivo | Regra |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | cada layout da raiz até a página envolve-o, **mais externo primeiro** |
| `middleware.py` | cada arquivo da raiz até a rota envolve a solicitação, **mais externo primeiro**, antes das dependências |
| `dependencies.py` | cada arquivo da raiz até a rota é executado, **o mais externo primeiro**, depois os próprios guardas do manipulador |
| `notfound.nexy`, `errors.nexy` | o **mais próximo** vence, por código de status |

Para a página acima, os layouts são aninhados como `root layout > (shop) layout > cart layout > page` e as dependências são executadas como `root > (shop) > cart > handler guards`.

## Por que o mais externo primeiro

Um layout externo desenha a moldura e uma dependência externa decide quem pode entrar. Colocá-los em primeiro lugar significa que os internos podem confiar neles: um diretório que requer autenticação é executado antes de um manipulador que lê o usuário.

## Layouts

Todos os arquivos de layout de uma pilha de família de pastas: consulte [Layouts](layouts/README.md). Famílias diferentes não se misturam: um `layout.vue` nunca quebra uma página `.tsx`, e um projeto tem `layout.nexy` ou layouts de cliente, nunca ambos ([modos](modes.md)).

## Arquivos de middleware

Veja [Arquivos de middleware](middleware/README.md): eles rodam antes das dependências e podem responder sem atingir a rota.

## Dependências

Consulte [Dependências](dependencies/README.md) para a ordem em um arquivo manipulador, incluindo `@UseGuard` e `@Middleware`.

## Páginas de erro

`notfound.nexy` e `errors.nexy` são instalados uma vez na raiz das rotas; uma cópia em um subdiretório refina a página para esse prefixo. Consulte [Páginas de erro](errors/README.md).

## Próximas etapas

- [Layouts](layouts/README.md)
- [Dependências](dependencies/README.md)
- [Páginas de erro](errors/README.md)
