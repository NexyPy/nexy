# Modo servidor e modo cliente

Um projeto Nexy é **renderizado por servidor** ou **roteado por cliente**, assim como um projeto Next.js é
páginas renderizadas no servidor ou em um aplicativo cliente. `useCSR` em `nexyconfig.py` escolhe.

## Modo servidor (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- As páginas são arquivos `.nexy`, `.md` ou `.mdx` em `src/routes/`.
- A raiz `layout.nexy` possui `<!DOCTYPE html>`, `<html>`, `<head>` e `<body>`.
- Os componentes do cliente (React, Vue, Svelte, Solid ou Preact) são permitidos como **ilhas**: você importa uma
  de uma página `.nexy` e hidrata no navegador. Veja [Ilhas](../../rendering/islands.md).
- Um componente cliente nunca é uma rota. Mantenha-os em `src/components/`.
- Uma estrutura de cliente por vez.

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## Modo cliente (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- Páginas são os arquivos da sua estrutura cliente: `.tsx` para React, `.vue`, `.svelte`.
Os arquivos - `.md` e `.mdx` permanecem rotas válidas: Nexy os renderiza no servidor dentro do cliente
  layout e o roteador do cliente assume a navegação a partir daí.
- O layout raiz de qualquer framework (`layout.tsx`, `layout.vue`, `layout.svelte`) pertence a `<!DOCTYPE html>`, `<html>`, `<head>` e `<body>`, como o
  layout raiz do Next.js App Router. Nexy renderiza em Node para a primeira resposta e o
  estrutura hidrata todo o documento. Consulte [layout.tsx](../../views/react/differences.md).
- `.py` arquivos são manipuladores de API servidos por FastAPI, próximos às rotas do cliente.
- Não existe nenhum arquivo `.nexy` e não há `layout.nexy`.
- A navegação entre as páginas acontece no navegador.

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## O que é rejeitado

Nexy verifica o projeto antes de `nx dev`, `nx start` e `nx build` e para com a lista de arquivos:

| Modo | Rejeitado | Mensagem |
|---|---|---|
| servidor | `.tsx`, `.jsx`, `.vue` ou `.svelte` em `src/routes/` | mover componentes para `src/components/` ou definir `useCSR = True` |
| cliente | qualquer arquivo `.nexy` em `src/routes/` | escreva-os como componentes da estrutura ou defina `useCSR = False` |
| ambos | mais de uma estrutura de front-end em `useFF` | `useFF must configure exactly one frontend framework` |
| cliente | `useRouter` (roteador modular) | `useCSR requires file-based routing` |
| cliente | não `useFF` | `useCSR requires a client framework` |

Arquivos e pastas começando com `_` ou `.` são ignorados por esta verificação.

## Qual

- **Conteúdo, marketing, documentos, sites SEO-first**: modo de servidor com ilhas.
- **Painéis e aplicativos com navegação rich client**: modo cliente.
- **Uma API Python com um aplicativo cliente na parte superior**: modo cliente, com `.py` manipuladores próximos às páginas.

## Próximas etapas

- [Layouts](layouts/README.md)
- [Renderização](../../rendering/README.md)
- [Configuração](../../reference/config.md)