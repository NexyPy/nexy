# Roteamento

Nexy possui dois roteadores nativos. Você pode escolher um por recurso; eles podem coexistir no mesmo aplicativo.

**Não tem certeza? Use roteamento baseado em arquivo.** Abrange páginas e endpoints de API sem configuração. Adicione o roteador modular quando um back-end precisar de controladores, serviços injetados ou protetores.

| Você está construindo | Use |
|---|---|
| Páginas, conteúdo, um site com alguns endpoints | Baseado em arquivo |
| Uma grande API com serviços compartilhados entre rotas | Modular |
| Ambos: páginas para pessoas, uma API estruturada para máquinas | Baseado em arquivo e modular juntos |

```diagram filename="O roteador baseado em arquivo, em resumo"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```

| Roteador | Fonte | Habilitado por |
|---|---|---|
| [Baseado em arquivo (FBR)](fbr/README.md) | todo arquivo em `src/routes/` | o diretório existe |
| [Modular](modular/README.md) | controladores e módulos | `useRouter = AppModule` em `nexyconfig.py` |

FBR é verificado sempre `src/routes/` existe, mesmo com um roteador modular montado.

## Coexistência e prioridades

Você pode combinar integração FBR, modular e personalizada. Nexy registra essas rotas na ordem em que são descobertas. Se dois roteadores definirem o mesmo caminho de URL, o primeiro registrado vence. 

*Observação: Nexy atualmente não fornece diagnóstico para colisões de URL; a primeira rota para reivindicar um caminho simplesmente obscurece as outras.*

## Roteamento baseado em arquivo

Uma rota é um arquivo. A URL é o caminho em `src/routes/`, menos a extensão. Como Next.js, um
o projeto está em um dos dois modos, escolhidos com `useCSR`:

| | `useCSR = False` (padrão) | `useCSR = True` |
|---|---|---|
| Páginas | `.nexy`, `.md`, `.mdx` | arquivos de sua estrutura de cliente |
| Layout raiz | `layout.nexy` | `layout.tsx` (Reagir) |
| Componentes do cliente | permitidos, como ilhas dentro das páginas | as próprias páginas |
| Rotas de API | `.py` | `.py` |

Consulte [Modo servidor e modo cliente](fbr/modes.md).

| Seção | O que ela cobre |
|---|---|
| [fbr/pages](fbr/pages/README.md) | páginas, [rotas dinâmicas](fbr/pages/dynamic-routes.md) e grupos de rotas |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` manipuladores de rota, [validação e erros](fbr/handlers/validation-and-errors.md) |
| [fbr/dependencies](fbr/dependencies/README.md) | `dependencies.py` e guardas, herdados pelo diretório |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, herdado pelo diretório |
| [fbr/erros](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, erros JSON |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | vinculação, navegação do cliente, [hooks](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | Manipuladores WebSocket |
| [fbr/inheritance](fbr/inheritance.md) | como layouts, dependências e páginas de erro herdam |

## Roteamento modular

Controladores, módulos e injeção de dependências, no estilo NestJS. Veja
[Roteamento modular](modular/README.md) e [Nexy e NestJS](modular/vs-nestjs.md).

## Integração personalizada

Você também pode integrar um roteador FastAPI existente em seu projeto Nexy. Consulte [Integração de roteamento personalizado](custom/README.md).

## Próximas etapas

- [Roteamento baseado em arquivo](fbr/README.md)
- [Renderização](../rendering/README.md)
- [Visualizações](../views/README.md): o que há dentro dos arquivos