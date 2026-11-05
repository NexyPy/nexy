# Atualizando para 2.2

O que muda em um projeto existente quando você passa da versão 2.1 para a 2.2 e o que fazer a respeito. A lista completa está no [registro de alterações](https://github.com/NexyPy/nexy/blob/main/CHANGELOG.md).

```bash
uv add "nexy>=2.2"            # or: uv tool upgrade nexy
nx build
nx test
```

## O que você pode ter que mudar

| Altere | Faça isso |
|---|---|
| **`.mdx` é compilado apenas por Vite.** O compilador Python não o renderiza mais | Mantenha React ou Preact em `useFF` e instale `@mdx-js/rollup`, `remark-gfm` e `@mdx-js/react`. Uma página sem componentes pode ser um arquivo `.md` em vez disso |
| **`useBadge` desapareceu.** A tag "Built with Nexy" não existe mais | Exclua a linha de `nexyconfig.py`. Uma linha restante é ignorada |
| **`nx check` não compila mais `.mdx`** | Nada: Vite relata MDX erros na compilação |

## O que permanece o mesmo

- Suas rotas, layouts, ações e configuração.
- Os projetos existentes mantêm suas próprias páginas iniciais. O novo design inicial só se aplica a projetos criados após a atualização.
- A barra de ferramentas de desenvolvimento e `useDevTools`.

## Novo em 2.2

- **Arquivos de agente.** `nx new` escreve `AGENTS.md`, `CLAUDE.md` e as habilidades para agentes de codificação. Para um projeto que você já possui, execute `nx skills`. Ele nunca substitui um arquivo que você escreveu. Consulte [Agentes de codificação](../guides/ai-agents.md).
- **Um servidor de desenvolvimento que continua em execução.** Quando seu aplicativo não pode ser iniciado, `nx dev` informa o motivo e aguarda a próxima alteração em vez de sair.
- **Um novo starter** para cada framework em Tailwind ou UnoCSS, com as mesmas páginas e componentes.
- **UnoCSS lê `.nexy` arquivos** em um projeto de servidor. Se você usar UnoCSS com `.nexy` páginas, adicione o bloco `content` mostrado em [Solução de problemas](../guides/troubleshooting.md).

## Documentação corrigida

Três páginas diziam algo que o código não faz. Se você os seguiu, verifique seus arquivos:

- Um componente `.nexy` coloca seus filhos com `<Slot />` (S maiúsculo), não `<slot />`.
- Um arquivo componente `.nexy` é nomeado em PascalCase: ele é importado como um módulo Python, portanto, um hífen não é compilado.
- Para `.mdx`, a estrutura é Preact quando o arquivo importa `preact`, React caso contrário.

## Onde será o próximo

- [Índice de documentação](../README.md): a página do que você está construindo
- [Solução de problemas](../guides/troubleshooting.md): os problemas que as pessoas enfrentam primeiro
- [Configuração](../reference/config.md): cada campo `use*` e seu padrão
