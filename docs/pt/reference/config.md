# Configuração

A configuração é uma classe em `nexyconfig.py` na raiz do projeto. Nexy carrega-o do diretório em que é executado; um projeto sem o arquivo usa os padrões.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## Servidor

| Campo | Padrão | Significado |
|---|---|---|
| `usePort` | `3000` | porta para `dev` e `start` |
| `useHost` | `"0.0.0.0"` | endereço de ligação |
| `useSslKeyfile`, `useSslCertfile` | `None` | servir HTTPS diretamente |
| `useDevTools` | `True` | a barra de ferramentas `nexy dev` adiciona informações a cada página (informações da página, rotas, erros, configuração); `False` remove-o. Nunca presente na produção |
| `useWorkers` | `0` | processos `nx start` executados; `0` é um por CPU no Linux e macOS, um no Windows |
| `useCSR` | `False` | modo de roteamento do lado do cliente; `.nexy` rotas estão desativadas |

## Rotas

| Campo | Padrão | Significado |
|---|---|---|
| `useRouter` | `None` | uma instância ou classe `APIRouter` montada próxima às rotas baseadas em arquivo; `None` significa apenas baseado em arquivo |
| `excludeDirs` | `["templates", "extension", "docs"]` | diretórios ignorados ao verificar rotas |
| `useAliases` | `None` | aliases de importação, por ex. `{"@": "src"}` (`@/components/Counter.tsx` significa `src/components/Counter.tsx`); `nx new` escreve o que você escolheu e Vite e `tsconfig.json` seguem-no |

## Interface

| Campo | Padrão | Significado |
|---|---|---|
| `useFF` | `None` | fábrica de estrutura do cliente: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | construir e servir pacotes de clientes com Vite |
| `useMarkdownExtensions` | `[]` | extensões extras para renderização `.md`/`.mdx` |
| `useWatchExtensions` | `None` | extensões extras que o servidor de desenvolvimento observa |
| `useWatchExcludePatterns` | `None` | padrões glob que o servidor de desenvolvimento ignora |

> **É bom saber**: `NexyConfigModel` declara `useVite = False`; o tempo de execução `Config` padrão é `True`.

## Nomes de arquivos reservados

Cada campo adiciona extensões a uma função reservada. `useLayoutExtensions = ["md"]` torna `layout.md` reservado, exatamente como `layout.nexy`.

| Campo | Adiciona extensões a |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## Documentação da API

| Campo | Padrão | Significado |
|---|---|---|
| `useDocs` | `True` | servir a página de referência escalar; `/openapi.json` é servido de qualquer maneira |
| `useDocsUrl` | `"/docs"` | caminho da página de referência da API |
| `useRedocsUrl` | `"/redocs"` | declarada mas nenhuma rota está montada |
| `useTitle` | `"Nexy App"` | OpenAPI título e título da página (`"Nexy"` em `NexyConfigModel`) |

### Grátis `/docs` para uma página do projeto

A referência da API responde `/docs` antes de qualquer rota, então `src/routes/docs.nexy` ou `src/routes/docs/[[...slug]].nexy` nunca é servido lá. `nx dev` e `nx start` nomeiam essa página na inicialização. Mova a referência com `useDocsUrl`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

Ou desligue-o com `useDocs = False`. `/openapi.json` permanece atendido em ambos os casos: manter as rotas do projeto fora desse caminho.

## Middleware

| Campo | Padrão | Significado |
|---|---|---|
| `useMiddlewares` | `[]` | Classes de middleware ASGI |
| `useCORS` | `None` | kwargs para `CORSMiddleware` |
| `useGZip` | `None` | kwargs para `GZipMiddleware` |
| `useTrustedHost` | `None` | kwargs por `TrustedHostMiddleware` |
| `useSession` | `None` | kwargs para `SessionMiddleware` |
| `useAuth` | `None` | configuração de middleware de autenticação |
| `useHTTPSRedirect` | `False` | redirecionar HTTP para HTTPS |

## Markdown

| Campo | Padrão | Significado |
|---|---|---|
| `useTocDepth` | `"2-6"` | níveis de títulos incluídos no índice |
| `useTocTitle` | `"Table of Contents"` | Título do sumário |
| `useTocAuto` | `True` | gerar o índice para Markdown páginas |

## Rotas fora da árvore de arquivos

Construa um FastAPI `APIRouter` e monte-o com `useRouter`. É servido próximo às rotas baseadas em arquivo:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Os padrões acima são lidos em `nexy/core/config.py`.

## Declarado, ainda não lido

Esses campos existem em `NexyConfigModel` mas nenhum código os consome. Configurá-los não tem efeito:

`useViteDevUrl`, `useRTL`.

## Próximas etapas

- [i18n](../guides/i18n.md): internacionalização
- [Frontend](../guides/frontend.md): `useFF` e a construção do cliente
- [Implantar](../deployment/README.md): opções de produção
