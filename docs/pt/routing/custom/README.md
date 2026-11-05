# Integração de roteamento personalizado

Nexy permite incluir um aplicativo FastAPI existente como roteador em seu projeto. Isso é útil quando você deseja reutilizar a lógica de back-end de outro serviço, integrar-se a APIs de terceiros ou criar um aplicativo composto com diversas preocupações de roteamento.

Ao contrário dos roteadores modulares e baseados em arquivo, que são intrínsecos ao Nexy, um roteador personalizado é simplesmente um `APIRouter` que você monta em seu aplicativo.

## Quando usar um roteador personalizado

- **Serviços de terceiros**: você tem um aplicativo FastAPI existente que deseja expor por meio do cliente Nexy.
- **Reutilização de código**: Extraia a lógica de backend de outro projeto em um roteador e inclua-a em um novo.
- **Padrões multilocatários ou microfrontend**: cada locatário ou módulo fornece seu próprio roteador.
- **Migração gradual**: Comece com um `APIRouter` e evolua-o para um módulo Nexy completo posteriormente.

## Como funciona

```python
from fastapi import APIRouter
from nexy import useRouter

# An existing FastAPI router (from another service)
third_party = APIRouter()
@third_party.get("/info")
async def info():
    return {"name": "Foo"}

# In your nexyconfig.py:
useRouter = third_party
```

O roteador é montado automaticamente pelo resolvedor de roteador do Nexy. Suas rotas estão disponíveis no mesmo padrão de URL do aplicativo original. Nenhuma configuração extra é necessária.

## Construindo um roteador personalizado

1. **Crie o roteador**
   ```píton
   da importação fastapi APIRouter

   api = APIRouter()
   @api.get("/status")
   status de definição assíncrona():
       retornar {"status": "ok"}
   ```

2. **Referencie-o em `nexyconfig.py`**
   ```píton
   da API de importação .my_backend

   useRouter = API
   ```

3. **Rotas de acesso**
   - Páginas baseadas em arquivo (`.nexy`, `.md`) e manipuladores modulares podem fazer referência a `/status` como fariam com qualquer outra rota.
   - O roteador é executado no mesmo processo, portanto, dependências, conexões de banco de dados e autenticação funcionam exatamente como no aplicativo original.

## Integração com outros roteadores

Um projeto Nexy pode combinar:

- **Roteamento baseado em arquivo** (`src/routes/`) para páginas e endpoints simples
- **Roteamento modular** (`useRouter = AppModule`) para back-ends estruturados
- **Roteamento personalizado** (`useRouter = APIRouter`) para código de terceiros

Todos os três coexistem; cada rota é registrada apenas uma vez. O roteador baseado em arquivo é sempre verificado quando `src/routes/` existe.

## Acesso CLI ao aplicativo incluído

Os comandos `nexy dev` e `nx` operam no roteador montado como um roteador integrado. Você obtém:

- Recarga a quente para endpoints definidos no roteador personalizado (se ele usar os recursos usuais do servidor de desenvolvimento de `nexy` ou FastAPI)
- Validação em `nexyconfig.py` (qualquer `APIRouter` trabalho)
- Documentos gerados automaticamente para as rotas incluídas (se você ativá-las)

## Segurança e isolamento

Como o roteador está incluído e não montado via `app.mount`, não há camada ASGI extra. O roteador reside no mesmo objeto de aplicativo que suas rotas modulares e baseadas em arquivo. Isso significa:

- O middleware adicionado pelo roteador personalizado se aplica a todas as solicitações.
- Os protetores e a injeção de dependência definidos no roteador personalizado podem acessar o mesmo contêiner que seu próprio código (se você usar injeção modular).
- Não há nenhum prefixo de URL além do que o próprio roteador define.

Se você precisar de isolamento, envolva o roteador em um subaplicativo antes de incluí-lo ou use técnicas padrão FastAPI.

## Exemplo: Incluindo um projeto FastAPI existente

Suponha que você tenha `auth.py` em outro pacote:

```python
from fastapi import FastAPI, APIRouter

auth = FastAPI(title="Auth service")
api = APIRouter()

@api.get("/login")
async def login():
    return {"msg": "Login"}

auth.include_router(api)
```

Em `nexyconfig.py`:

```python
from other_package.auth import api

useRouter = api
```

O endpoint `/login` agora pode ser acessado em seu site Nexy sem mover uma linha de código.

## Como começar

1. Crie seu `APIRouter` (ou encontre um em um pacote existente).
2. Aponte `useRouter` para ele em `nexyconfig.py`.
3. Acesse suas rotas por meio de suas páginas, manipuladores ou estruturas de cliente.
4. Se precisar de mais controle, converta o roteador personalizado em um roteador modular usando `AppModule`.

## Próximas etapas

- [Roteamento baseado em arquivo](../fbr/README.md) – Crie páginas e manipuladores simples a partir de arquivos.
- [Roteamento modular](../modular/README.md) – Backends estruturados com injeção e proteções.
- [Manipuladores de rota](../fbr/handlers/README.md) – Defina Python pontos finais.

O roteador personalizado oferece flexibilidade para reutilizar o código FastAPI existente, mantendo a simplicidade das páginas baseadas em arquivo e da estrutura modular.