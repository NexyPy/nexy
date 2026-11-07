# Crie um aplicativo de notas com Nexy, parte 13: pesquise as notas enquanto você digita

A Parte 13 adiciona uma caixa de pesquisa acima das notas: uma ilha React filtra cada nota do usuário a cada pressionamento de tecla, no navegador, sem nenhuma solicitação ao servidor.

**Antes de começar:** o aplicativo da [parte 12](password-reset.md). O projeto foi criado com React na [parte 1](create-the-project.md), então React já está instalado.

## Uma ilha, e por que aqui

O resto da página fica em HTML renderizado pelo servidor: a lista, os formulários, as páginas de notas. Apenas a caixa de pesquisa precisa do navegador, portanto, apenas a caixa de pesquisa é React. Isso é uma *ilha*: um componente cliente dentro de uma página do servidor, que se torna interativo por si só.

## O componente de pesquisa

```tsx filename="src/componentes/NoteSearch.tsx"
import { useState } from "react"

type Note = { id: number; text: string }

export default function NoteSearch({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("")
  const words = query.trim().toLowerCase()
  const found = words ? notes.filter((note) => note.text.toLowerCase().includes(words)) : []
  return (
    <section className="note-search" aria-label="Search the notes">
      <label>
        Search
        <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <div aria-live="polite">
        {words && found.length === 0 && <p>No note matches “{query}”.</p>}
        {found.length > 0 && (
          <ul>
            {found.map((note) => (
              <li key={note.id}>
                <a href={`/notes/${note.id}`}>{note.text}</a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
```

React escreve `{note.text}` como texto: uma nota `<b>x</b>` mostra seus colchetes, sem `| e` para adicionar.

`found` só é computado quando algo é digitado, e isso é importante para a construção: `nx build` renderiza cada ilha uma vez em HTML, com espaços reservados em vez de seus adereços. Um componente que lê uma propriedade list durante a primeira renderização obtém um espaço reservado em vez de uma lista e não envia HTML. Este lê `notes` somente após pressionar uma tecla, então a compilação renderiza sua caixa de pesquisa e a página a mostra antes de qualquer JavaScript ser executado.

`aria-live="polite"` faz com que um leitor de tela leia os resultados quando eles mudam, sem interromper.

## Coloque a ilha na página

A página passa as notas como um adereço: uma lista de dicionários, que o Nexy transforma em JSON para o navegador. Cada nota entra, não apenas as cinco da página atual, então a pesquisa cobre todas elas:

<!-- router:fbr,custom -->
```nexy filename="src/rotas/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`from "@/components/NoteSearch.tsx" import NoteSearch` importa um componente React para uma página `.nexy`; a tag passa seus atributos como adereços. `notes="{{ searchable }}"` passa a lista Python em si, não uma string. `directive="client:idle"` torna a ilha interativa quando o navegador não tem nada mais urgente para fazer.

Abra <http://localhost:3000/notes> e digite algumas letras de uma nota: as notas correspondentes aparecem abaixo da caixa a cada pressionamento de tecla. Limpe a caixa e os resultados desaparecem.

> [!NOTE]
> Os adereços de uma ilha viajam na página, como JSON. Enviar cada nota é adequado para algumas centenas delas; para milhares, pesquise no servidor, com uma consulta e um filtro `LIKE`.

## O que você aprendeu

- Uma ilha é um componente cliente dentro de uma página do servidor: aqui, React apenas para a caixa de pesquisa.
- Uma página `.nexy` importa-o por caminho e passa valores Python como adereços, serializados para JSON.
- A compilação renderiza uma ilha uma vez, com espaços reservados para seus adereços: leia a lista de adereços após a primeira renderização e a ilha envia o HTML.

## Próximas etapas

- [Parte 14: marque uma nota sem recarregar a página](tick-a-note.md)
- [Ilhas e hidratação](../rendering/islands.md): diretrizes, adereços e limitações
