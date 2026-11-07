# Crie um aplicativo de notas com Nexy, parte 6: crie uma nota a partir de um formulário

A Parte 6 adiciona um formulário acima da lista: ele posta em uma função Python marcada como `@Action`, que salva a nota, e o visitante volta à lista com a nova nota nela.

**Antes de começar:** o aplicativo da [parte 5](store-the-notes.md), com seu banco de dados.

## Salvar uma nota

Adicione uma função que salva uma nota e a retorna, ao lado das duas que as leem:

<!-- router:fbr,custom -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note
```
<!-- /router -->

## Transforme isso em uma ação

Uma ação é uma função Python que o navegador pode chamar. `@Action` serve como um `POST`, verifica a entrada em relação às dicas de tipo e a executa:

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

Na inicialização, Nexy importa todos os módulos de `src/` e serve as ações que encontra: não há rota a ser declarada, para nenhum roteador. `src/actions/` é onde este tutorial os mantém.

## Poste o formulário nele

Um modelo `.nexy` conhece o caminho de cada ação como `__actions_path["name"]`. Um formulário HTML simples é postado lá, para que a página funcione antes de qualquer script ser carregado:

<!-- router:fbr,custom -->
```nexy filename="src/rotas/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

A entrada é chamada `text`, assim como o parâmetro de `create_note`: é assim que o campo chega até ela.

## Mostrar uma nota como texto, não como HTML

A partir de agora, uma nota é o que o visitante digitou. Um modelo `.nexy` escreve um valor como ele é, então uma nota `<script>…</script>` seria executada no navegador de todos que abrirem a lista. `| e` escapa: `<` torna-se `&lt;`, e a nota aparece como texto.

```nexy filename="src/componentes/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text | e }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

<!-- router:fbr,custom -->
```nexy filename="src/rotas/notas/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
---
<section class="app-page">
  <h1>{{ note.text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

Escape de todo valor proveniente de um visitante ou do banco de dados. `| safe` faz o oposto: guarde para o HTML que você mesmo escreveu.

## Experimente

Digite *Leia os documentos* e pressione **Adicionar**. A ação salva a nota, depois responde `303` de volta para `/notes`, e o navegador mostra a lista novamente, com a terceira nota na parte inferior.

## O que você aprendeu

- `@Action` transforma uma função Python em um endpoint `POST`, com suas dicas de tipo como entrada.
- Um formulário é postado nele através de `__actions_path["name"]`, sem JavaScript e retorna com `303`.
- Os nomes dos campos do formulário são os nomes dos parâmetros da Ação.
- `| e` mostra o que um visitante digitou como texto: escape de todos os valores que não vieram de você.

## Próximas etapas

- [Parte 7: mostrar erros de validação](validation-errors.md)
- [Ações](../guides/actions.md): chamadas digitadas do navegador, erros e segurança
