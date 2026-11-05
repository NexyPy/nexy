# Tutorial: crie uma página de notas em 10 minutos

Você criará um projeto, adicionará uma página, adicionará um endpoint Python, compartilhará dados entre eles e construirá para produção. Você termina com uma lista de notas servidas como página e como JSON.

Novo no Nexy? Faça o [Início rápido](quick-start.md) primeiro: leva três minutos.

```diagram filename="O tutorial completo em uma linha"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. Crie o projeto

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` vem com [uv](https://docs.astral.sh/uv/) e apenas cria o projeto. Cada comando após ser executado dentro do ambiente virtual do projeto (ou como `uv run nexy dev`).

Escolha o roteador baseado em arquivo, um projeto web e qualquer estrutura de cliente (ou nenhuma). Abrir
<http://localhost:3000>. Etapas longas imprimem uma linha cada uma com sua duração, como faz `uv`.

<!-- router:modular -->
Responda `No` ao prompt do roteador baseado em arquivo: `nx new` estrutura o roteador modular em `src/apps/` em vez de `src/routes/`.
<!-- /router -->

<!-- router:custom -->
Responda `Yes` ao prompt do roteador baseado em arquivo para as páginas e, em seguida, monte seu `APIRouter` existente em `nexyconfig.py`: os dois roteadores coexistem.
<!-- /router -->

## 2. Edite o layout

<!-- router:fbr,custom -->
`src/routes/layout.nexy` possui o documento HTML (com React roteamento do cliente é `layout.tsx`). Altere o `<title>`:

```nexy
<title>Notes</title>
```

Salvar: o navegador recarrega. Consulte [Layouts](../routing/fbr/layouts/README.md).
<!-- /router -->

<!-- router:modular -->
O controlador renderiza `src/apps/layout.nexy` em torno da visualização, e esse arquivo possui o documento HTML. Altere o `<title>`:

```nexy
<title>Notes</title>
```

Salvar: o navegador recarrega. Consulte [Visualizações de um controlador](../routing/modular/README.md#views-from-a-controller).
<!-- /router -->

## 3. Adicione uma página

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Abra <http://localhost:3000/notes>: você deverá ver dois marcadores. É servido em `/notes`. A parte entre `---` é Python, o resto é Jinja2.
<!-- /router -->

<!-- router:modular -->
Um controlador retorna uma visualização. Criar `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Declare a rota em `src/apps/app_controller.py` e adicione o controlador ao módulo:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

Abra <http://localhost:3000/notes>: você deverá ver dois marcadores. A parte entre `---` é Python, o resto é Jinja2.
<!-- /router -->

## 4. Adicione um terminal

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

Você deve obter `[{"id":1,"text":"Buy milk"}]`. O nome da função é o método HTTP. Os documentos interativos da API estão em `/docs`.
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

Adicione `NotesApiController` a `controllers` em `src/apps/app_module.py` e execute:

```bash
curl http://localhost:3000/api/notes
```

Você deve obter `[{"id":1,"text":"Buy milk"}]`. O nome do método é o método HTTP. Os documentos interativos da API estão em `/docs`.
<!-- /router -->

## 5. Compartilhe os dados

Mova a lista para um módulo Python e use-a em ambos os arquivos:

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. Construir e servir

```bash
nx build
nx start
```

`nx build` imprime cada fase com sua duração. `nx start` fornece a saída compilada com Uvicorn: no Node process at runtime.

## Onde será o próximo

- [Roteamento](../routing/README.md): segmentos e grupos dinâmicos
- [Ações](../guides/actions.md): chame Python de um formulário ou do cliente
- [Teste](../guides/testing.md): páginas de teste e endpoints
- [Implantar](../deployment/README.md): contêineres e proxies reversos
