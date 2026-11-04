# Atualizando para 2.2

O que muda em um projeto existente quando você passa da versão 2.1 para a 2.2 e o que fazer a respeito. O
a lista completa está no [changelog](../../CHANGELOG.md).

```bash
uv add "nexy>=2.2"            # or: uv tool upgrade nexy
nx build
nx test
```

## O que você pode precisar mudar

| Alterar | Faça isso |
|---|---|
| **`.mdx` é compilado apenas pelo Vite.** O compilador Python não o renderiza mais | Mantenha React ou Preact em `useFF` e instale `@mdx-js/rollup`, `remark-gfm` e `@mdx-js/react`. Uma página sem componentes pode ser um arquivo `.md` em vez disso |
| **`useBadge` desapareceu.** A tag "Built with Nexy" não existe mais | Exclua a linha de `nexyconfig.py`. Uma linha restante é ignorada |
| **`nx check` não compila mais `.mdx`** | Nada: Vite relata erros de MDX na compilação |

## O que permanece o mesmo

- Suas rotas, layouts, ações e configuração.
- Os projetos existentes mantêm suas próprias páginas iniciais. O novo design inicial só se aplica a projetos
  criado após a atualização.
- A barra de ferramentas de desenvolvimento e `useDevTools`.

## Novo na versão 2.2

- **Arquivos do agente.** `nx new` escreve `AGENTS.md`, `CLAUDE.md` e as habilidades para codificação de agentes. Por um
  projeto que você já possui, execute `nx skills`. Ele nunca substitui um arquivo que você escreveu. Veja
  [Agentes de codificação](../guides/ai-agents.md).
- **Um servidor de desenvolvimento que continua em execução.** Quando seu aplicativo não pode ser iniciado, `nx dev` relata o motivo e
  espera pela próxima alteração em vez de sair.
- **Um novo starter** para cada framework em Tailwind ou UnoCSS, com as mesmas páginas e componentes.
- **UnoCSS lê `.nexy` arquivos** em um projeto de servidor. Se você usa UnoCSS com `.nexy` páginas, adicione o
  Bloco `content` mostrado em [Solução de problemas](../guides/troubleshooting.md).

## Documentação corrigida

Três páginas diziam algo que o código não faz. Se você os seguiu, verifique seus arquivos:

- Um componente `.nexy` coloca seus filhos com `<Slot />` (S maiúsculo), não `<slot />`.
- Um arquivo de componente `.nexy` é nomeado em PascalCase: ele é importado como um módulo Python, portanto, um hífen
  não compila.
- Para `.mdx`, o framework é Preact quando o arquivo importa `preact`, caso contrário, React.

## Onde será o próximo

- [Índice de documentação](../README.md): a página do que você está construindo
- [Solução de problemas](../guides/troubleshooting.md): os problemas que as pessoas enfrentam primeiro
- [Config](../reference/config.md): cada campo `use*` e seu padrão