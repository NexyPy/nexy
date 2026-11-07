# Construa um aplicativo de notas com Nexy, parte 3: rotas dinâmicas e uma API

A Parte 3 dá a cada nota seu próprio URL, `/notes/1`, e serve as mesmas notas que JSON em `/api/notes`, ambas lidas de um módulo Python.

**Antes de começar:** o aplicativo da [parte 2](pages-and-layouts.md).

## Mantenha as anotações em um módulo

A página e a API lerão a mesma lista. Mova-o para um módulo próprio, com uma função que encontra uma nota:

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## Vincule cada nota à sua página

<!-- router:fbr,custom -->
```nexy filename="src/rotas/notes/index.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

## Adicione uma página por nota

<!-- router:fbr,custom -->
Um nome de pasta ou arquivo entre colchetes é um segmento da URL: `[id].nexy` responde `/notes/1`, `/notes/2` e passa o segmento para a página como um adereço. `id: prop[int]` transforma-o em um número, então `/notes/abc` responde `404` antes da página ser executada.

```nexy filename="src/rotas/notas/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
text = find(id)
if text is None:
    notFound()
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
Um `{id}` no caminho de um controlador é um segmento da URL, passado para o método com esse nome. `id: int` transforma-o em um número, então `/notes/abc` responde `404` antes da execução do método.

```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

`notFound()` interrompe a solicitação com um `404`: uma nota que não existe responde como uma URL que não existe.

## Sirva as notas como JSON

<!-- router:fbr,custom -->
Um arquivo `.py` em `src/routes/` é uma rota de API. Cada função nomeada após um método HTTP responde a esse método:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
Os três controladores das notas, em um arquivo. Cada método nomeado após um método HTTP responde a esse método:

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import NOTES, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        text = find(id)
        if text is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [{"id": id, "text": text} for id, text in NOTES.items()]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController, NoteController, NotesApiController]
```
<!-- /router -->

Verifique os três URLs:

- <http://localhost:3000/notes/1> mostra *Comprar leite*;
- <http://localhost:3000/notes/9> respostas *Página não encontrada*;
- `curl http://localhost:3000/api/notes` imprime `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`.

A API está listada, com seu esquema, em <http://localhost:3000/docs>.

## O que você aprendeu

<!-- router:fbr,custom -->
- `[id].nexy` é um segmento dinâmico; `id: prop[int]` lê e converte.
- Um arquivo `.py` em `src/routes/` responde JSON, uma função por método HTTP.
<!-- /router -->
<!-- router:modular -->
- `{id}` no caminho de um controlador é um segmento dinâmico; `id: int` converte.
- Um método controlador que retorna dados responde JSON; aquele que retorna `useViews` responde uma página.
<!-- /router -->
- `notFound()` responde `404` de qualquer lugar; um módulo compartilhado mantém as páginas e a API em sintonia.

## Próximas etapas

- [Parte 4: componentes](components.md)
- [Exceções e erros](../reference/exceptions.md): `notFound`, `redirect` e as outras saídas
