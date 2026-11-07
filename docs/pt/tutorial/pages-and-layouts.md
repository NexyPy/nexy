# Crie um aplicativo de notas com Nexy, parte 2: páginas e layouts

A Parte 2 adiciona a página que lista as notas e mostra como o layout as envolve no documento HTML.

**Antes de começar:** o projeto da [parte 1](create-the-project.md), com `nexy dev` em execução.

## Adicione a página de notas

<!-- router:fbr,custom -->
Uma página é um arquivo em `src/routes/` e seu caminho é sua URL. Crie a página de notas:

```nexy filename="src/rotas/notes/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` respostas `/notes`.
<!-- /router -->

<!-- router:modular -->
Um controlador responde a uma URL e retorna uma visualização. Dê às notas uma pasta própria, com vista a:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

e o controlador que o renderiza em `/notes`:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

Um controlador responde apenas quando um módulo o lista. Adicione-o ao módulo raiz:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

Abra <http://localhost:3000/notes>: você deverá ver dois marcadores. A parte entre as duas linhas `---` é Python, executada no servidor; o resto é HTML com tags Jinja2 como `{% for %}` e `{{ note }}`.

## Alterar o layout

<!-- router:fbr,custom -->
`src/routes/layout.nexy` possui o documento HTML: `<html>`, `<head>` e `<body>`. Nexy envolve todas as páginas, onde escreve `{{children | safe}}`.
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` possui o documento HTML: `<html>`, `<head>` e `<body>`. O controlador envolve sua visão passando a visão como `children`.
<!-- /router -->

Abra o layout e altere a linha `<title>Nexy App</title>` para:

```html
<title>Notes</title>
```

Salvar: a aba do navegador agora exibe *Notas*, em todas as páginas.

## Dê espaço às páginas abaixo do cabeçalho

O cabeçalho do layout é fixo: fica no topo da janela, acima da página. As páginas do starter definem seu próprio espaço abaixo; as páginas do aplicativo de notas compartilham uma classe para isso, `app-page`, que cada página do tutorial coloca em torno de seu conteúdo. Adicione-o no final de `src/globale.css`, a folha de estilo que cada página já carrega:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind, que o starter utiliza, remove as bordas dos campos do formulário: essas regras as devolvem, para que os formulários das próximas partes possam ser vistos.

## O que você aprendeu

<!-- router:fbr,custom -->
- Um arquivo `.nexy` em `src/routes/` é uma página; sua pasta e nome são seu URL.
- A raiz `layout.nexy` envolve todas as páginas do documento HTML.
<!-- /router -->
<!-- router:modular -->
- Um controlador responde a uma URL e renderiza uma visualização `.nexy` com `useViews`; um módulo o lista.
- O layout também é uma visualização: o controlador passa a visualização da página para ele como `children`.
<!-- /router -->
- Um arquivo `.nexy` é Python entre `---`, depois HTML com Jinja2.
- `src/globale.css` contém os estilos que cada página compartilha, como `app-page`.

## Próximas etapas

- [Parte 3: rotas dinâmicas e uma API](dynamic-routes.md)
- [Arquivos .nexy](../views/nexy/README.md): adereços, componentes e estilos
