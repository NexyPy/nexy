# Crie um aplicativo de notas com Nexy, parte 7: mostre erros de validação

A parte 7 recusa nota em branco ou muito longa, e mostra porque acima do formulário, na mesma página, ainda sem JavaScript.

**Antes de começar:** o aplicativo da [parte 6](create-a-note.md).

## Dois tipos de erros

As dicas de tipo de uma Action já recusam uma forma errada: um formulário sem um campo `text` responde `422` antes de `create_note` ser executado. Uma regra sobre o valor em si, como "não em branco", cabe a você escrever na Ação.

## Confira a nota na Ação

Uma falha envia o visitante de volta à lista com o motivo na URL; um sucesso volta para a lista sem ele:

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` diz ao navegador para carregar a próxima página com um `GET`, para que uma atualização não poste o formulário uma segunda vez.

## Mostre o motivo acima do formulário

`useSearchParams()` lê a string de consulta da solicitação atual:

<!-- router:fbr,custom -->
```nexy filename="src/rotas/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
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
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`| e` escapa da mensagem: a string de consulta vem do visitante, portanto nunca é escrita na página como HTML. `role="alert"` faz um leitor de tela anunciar isso.

`required` e `maxlength` permitem que o navegador evite a maioria dos erros antes que eles saiam dele. A Ação verifica novamente: uma solicitação não precisa vir do seu formulário.

Adicione uma nota de três espaços: a lista volta com *Uma nota não pode ficar em branco.* acima do formulário.

## O que você aprendeu

- As dicas de tipo recusam uma forma errada com `422`; regras sobre o valor vão para a Ação.
- Uma ação pode responder com um `RedirectResponse`; `303` após um formulário evita uma segunda postagem.
- `useSearchParams()` lê a string de consulta e `| e` escapa do que o visitante enviou.

## Próximas etapas

- [Parte 8: editar e excluir uma nota](edit-and-delete.md)
- [Exceções e erros](../reference/exceptions.md): cada status que uma ação e uma página podem responder
