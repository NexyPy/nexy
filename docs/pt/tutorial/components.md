# Crie um aplicativo de notas com Nexy, parte 4: componentes

A Parte 4 transforma cada nota em um componente reutilizável, um arquivo `.nexy` que você importa como um nome Python e usa como uma tag HTML.

**Antes de começar:** o aplicativo da [parte 3](dynamic-routes.md).

## Escreva o componente

Um componente é um arquivo `.nexy` fora das rotas. Seus adereços são declarados com `prop[...]`, e o chamador os passa como atributos:

```nexy filename="src/componentes/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

O bloco `<style>` é enviado com cada página que usa o cartão. Não tem escopo: `.note` é uma classe para a página inteira, então forneça nomes às classes de um componente que somente ele usa.

## Use-o na lista

<!-- router:fbr,custom -->
```nexy filename="src/rotas/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` é o alias de importação da parte 1: aponta para `src/`. O nome do arquivo é o nome do componente, em PascalCase: `NoteCard.nexy` exporta `NoteCard`.

Abrir <http://localhost:3000/notes>: cada nota agora é um cartão.

## O que você aprendeu

- Um arquivo `.nexy` fora das rotas é um componente; seus `prop[...]` são seus atributos.
- `from "@/components/x.nexy" import X` importa; `<X />` renderiza.
- Um bloco `<style>` não tem escopo: nomeie as classes de um componente depois dele.

## Próximas etapas

- [Parte 5: armazene as notas em SQLite](store-the-notes.md)
- [Componentes](../views/nexy/components.md): `Image`, `Link` e os auxiliares integrados
