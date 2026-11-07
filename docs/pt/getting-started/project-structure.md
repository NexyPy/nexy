# Estrutura do projeto

Cada arquivo em um projeto Nexy tem um trabalho, e para onde ele vai depende do roteador: `src/routes/` para roteamento baseado em arquivo, `src/apps/` para o roteador modular.

## Nível superior

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Para escolher uma pasta, pergunte qual é o arquivo:

- **Algo que o navegador pode abrir** - uma rota: `src/routes/`.
- **Uma peça usada por diversas rotas** - um componente ou módulo: `src/components/`, `src/`.
- **Um arquivo servido como está** - `public/`.
- **Gerado** - `__nexy__/`; nunca edite.

> [!WARNING]
> `src/routes/` é escaneado: um ajudante ali colocado se torna uma rota. Coloque um helper que não seja uma rota fora de `src/routes/`, ou inicie seu nome com `_`.
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Para escolher uma pasta, pergunte qual é o arquivo:

- **Uma URL** - método de um controlador em `src/apps/`, registrado por seu módulo.
- **Uma página** - uma visualização `.nexy` próxima ao seu controlador, retornada com `useViews`.
- **Uma peça usada por diversas visualizações** - `src/components/`.
- **Um arquivo servido como está** - `public/`.
- **Gerado** - `__nexy__/`; nunca edite.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Para escolher uma pasta, pergunte qual é o arquivo:

- **Uma rota do aplicativo incluído** - onde já está, aqui `src/legacy/`.
- **Uma nova página ou rota** - `src/routes/`, próxima ao roteador incluído.
- **Um arquivo servido como está** - `public/`.
- **Gerado** - `__nexy__/`; nunca edite.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

Cada arquivo se torna uma rota, exceto os nomes reservados abaixo. O caminho do arquivo menos a extensão é o URL - consulte [roteamento baseado em arquivo](../routing/fbr/README.md).

| Arquivo | Função |
|---|---|
| `layout.nexy` | envolve páginas irmãs e filhas |
| `errors.nexy` | 500 páginas para o diretório |
| `notfound.nexy` | Página 404 para o diretório |
| `dependencies.py` | dependências compartilhadas FastAPI para o diretório |
| `__init__.py` | Python marcador de pacote |
| `loading.nexy` | reservado - excluído das rotas, mas ainda não tem efeito de tempo de execução |

Cada nome de página também existe por estrutura. Com `react()` configurado, `layout.jsx` e `layout.tsx` são reservados exatamente como `layout.nexy`. As listas são construídas em `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` e `errors.nexy` só são instalados quando existe uma cópia na raiz das rotas. Uma cópia em um subdiretório refina a página para esse prefixo.
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

Um controlador responde URLs, um módulo agrupa controladores e provedores e o módulo raiz é montado com `useRouter` em `nexyconfig.py`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

Nenhum arquivo em `src/apps/` é uma rota pelo seu nome: apenas os controladores que um módulo lista respondem. Consulte [roteamento modular](../routing/modular/README.md).
<!-- /router -->

## `public/`

Os arquivos aqui são servidos a partir da raiz do site: `/favicon.ico`, `/robots.txt`, imagens, fontes.

## `__nexy__/`

Gerado por `nx build` (e por `nx dev` para as peças necessárias). Ele contém:

- os arquivos `.nexy` compilados, como um pacote Python (`__nexy__/src/...`);
- os pontos de entrada do cliente gerados (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` após uma compilação Vite - ativos, manifesto, HTML pré-renderizado;
- `build-cache.json`.

Trate todo o diretório como descartável: exclua-o e reconstrua-o. Editá-lo manualmente perde a alteração na próxima compilação. Adicione-o a `.gitignore`.

## Próximas etapas

<!-- router:fbr -->
- [Roteamento baseado em arquivo](../routing/fbr/README.md): como um caminho se torna uma URL
<!-- /router -->
<!-- router:modular -->
- [Roteamento modular](../routing/modular/README.md): controladores, módulos e provedores
<!-- /router -->
<!-- router:custom -->
- [Roteamento personalizado](../routing/custom/README.md): inclua um roteador FastAPI existente
<!-- /router -->
- [Configuração](../reference/config.md): todas as opções do projeto
- [Frontend](../guides/frontend.md): Vite, estilo e construção do cliente
