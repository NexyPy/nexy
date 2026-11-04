# Roteamento modular

O roteamento modular usa classes com decoradores em vez de arquivos em `src/routes/`: controladores
lidam com solicitações, os módulos as agrupam e os provedores são injetados. Monte o `APIRouter` resultante
com `useRouter` em `nexyconfig.py`.

**Antes de começar:** um projeto Nexy e uma página de trabalho. O roteador modular substitui o
baseado em arquivo, então leia [Routing](../README.md) primeiro se você ainda não escolheu um roteador.

| Página | O que cobre |
|---|---|
| Esta página | Montar um módulo, escrever um controlador, agrupar controladores |
| [Injeção de dependência](dependency-injection.md) | `@Injectable`, escopos, o contêiner |
| [Guardas e metadados](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [Nexy e NestJS](vs-nestjs.md) | O que corresponde ao NestJS e o que não corresponde |

## Configure o roteador

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTA]
> o roteamento baseado em arquivo continua funcionando. Se `src/routes/` existir, ele será verificado mesmo
> quando `useRouter` está definido.

## Escreva um controlador

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Os métodos são combinados por nome, sem distinção entre maiúsculas e minúsculas: `get`, `post`, `put`, `patch`, `delete`, `options`,
`head`, `trace`.

Um controlador declara um manipulador por método HTTP; uma duplicata aumenta na inicialização. Adicione um prefixo com
`@Controller(prefix="/users")` - todo manipulador é montado em `prefix/`. `async def SOCKET(...)` em um
controlador registra um WebSocket no mesmo caminho.

## Agrupar controladores em um módulo

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` retorna um `APIRouter`. `controllers` é obrigatório; `providers`, `imports`
e `exports` são opcionais. Os módulos importados são montados como sub-roteadores e seus provedores exportados
são resolvidos na inicialização.

## Visualizações de um controlador

Um controlador pode retornar uma página. `useViews` renderiza uma visualização `.nexy`; aninhe um dentro do outro para embrulhá-lo
em um layout:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

Consulte [Layouts](../fbr/layouts/README.md).

## Exemplo

Veja `examples/Modular/api/minimal/`.

## Próximas etapas

- [Injeção de dependência](dependency-injection.md): serviços e escopos
- [Guardas e metadados](guards-and-metadata.md): proteger e documentar rotas
- [Routing](../README.md): o roteador baseado em arquivo
- [Config](../../reference/config.md): todas as opções, incluindo `useRouter`