# Tutorial Nexy: crie um aplicativo de notas passo a passo

O tutorial Nexy cria um aplicativo de notas a partir de uma pasta vazia para uma construção de produção, uma parte de cada vez, e cada parte termina com um aplicativo em execução.

Novo no Nexy? O [Início rápido](quick-start.md) mostra ele funcionando em três minutos; volte aqui para saber como funciona.

## Como funciona o tutorial

- **Um aplicativo que cresce.** Cada parte adiciona um recurso ao aplicativo de notas da parte anterior.
- **Seu roteador.** As peças seguem o roteador escolhido no topo do menu: baseado em arquivo, modular ou personalizado. Mude para lá e os arquivos de cada parte mudam com ele.
- **Código que é executado.** Cada arquivo com um nome acima é um arquivo inteiro, e o conjunto de testes reproduz as partes em ordem em um novo projeto: o que você copia é o que é executado.
- **Pare em qualquer lugar.** Cada parte leva de 10 a 20 minutos e termina com o que verificar no navegador.

## As peças

### Unidade 1: o básico

| Parte | O que você adiciona | O que você aprende |
|---|---|---|
| [1. Crie o projeto](../tutorial/create-the-project.md) | um projeto que funciona | `nexy new`, `nexy dev` |
| [2. Páginas e layouts](../tutorial/pages-and-layouts.md) | a página de notas | páginas, visualizações, o layout |
| [3. Rotas dinâmicas e uma API](../tutorial/dynamic-routes.md) | `/notes/1` e `/api/notes` | Segmentos de URL, rotas JSON, `notFound` |
| [4. Componentes](../tutorial/components.md) | um cartão por nota | `.nexy` componentes e seus adereços |

### Unidade 2: dados

| Parte | O que você adiciona | O que você aprende |
|---|---|---|
| [5. Armazene as notas em SQLite](../tutorial/store-the-notes.md) | um modelo, uma migração, uma semente | SQLModel, `nx migrate` |
| [6. Crie uma nota a partir de um formulário](../tutorial/create-a-note.md) | um formulário que salva uma nota | Ações, formulários sem JavaScript |
| [7. Mostrar erros de validação](../tutorial/validation-errors.md) | uma mensagem acima do formulário | regras em uma ação, `303`, `useSearchParams` |
| [8. Edite e exclua uma nota](../tutorial/edit-and-delete.md) | as formas de uma nota | várias ações por página, campos ocultos |
| [9. Paginar as notas](../tutorial/paginate-the-notes.md) | cinco notas por página | `offset` e `limit`, links entre páginas |

### Unidade 3: usuários

| Parte | O que você adiciona | O que você aprende |
|---|---|---|
| [10. Crie uma conta e faça login](../tutorial/accounts.md) | inscrever-se, entrar, sair | sessões, hash de senha |
| [11. Dê a cada usuário suas próprias notas](../tutorial/own-notes.md) | notas que pertencem a um usuário | chaves estrangeiras, `redirect`, `401` |
| [12. Redefinir uma senha esquecida por e-mail](../tutorial/password-reset.md) | um link de redefinição enviado por e-mail | `smtplib`, tokens assinados que expiram |

### Unidade 4: interatividade

| Parte | O que você adiciona | O que você aprende |
|---|---|---|
| [13. Pesquise as notas enquanto você digita](../tutorial/search-the-notes.md) | uma caixa de pesquisa que filtra conforme você digita | React ilhas, adereços de Python |
| [14. Marque uma nota sem recarregar a página](../tutorial/tick-a-note.md) | um botão Concluído em cada nota | aprimoramento progressivo, uma ação para uma forma e para `fetch` |

### Em seguida

| Unidade | O que o aplicativo ganha |
|---|---|
| 5. Além do pedido | notas compartilhadas por e-mail em segundo plano, um resumo diário, atualizações ao vivo |
| 6. Navio | testes, páginas de erro e logs, cabeçalhos de segurança, uma compilação Docker |

## Próximas etapas

- [Parte 1: crie o projeto](../tutorial/create-the-project.md)
- [Conceitos básicos](core-concepts.md): as palavras que o tutorial usa
