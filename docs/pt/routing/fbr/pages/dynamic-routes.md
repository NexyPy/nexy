# Rotas dinâmicas

Um segmento de caminho escrito entre colchetes corresponde a qualquer valor e o entrega à página ou ao manipulador.

## Segmentos dinâmicos

`blog/[slug].nexy` serve `/blog/{slug}`. Numa página, declare o segmento como uma propriedade; em um Python
manipulador, tome isso como um argumento.

```nexy filename="src/rotas/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/rotas/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## Segmentos digitados

A anotação decide o tipo.

| Onde | Conversão |
|---|---|
| `.py` manipulador | qualquer anotação de tipo FastAPI (`int`, `UUID`, `Enum`...) |
| `.nexy` páginas | `int` e `float` são convertidas; todo o resto permanece uma string |

Um valor que não corresponde à anotação é **não encontrado**: `/api/users/abc` respostas `404`, porque
uma rota dinâmica captura qualquer URL e uma URL que não pode ser convertida simplesmente não existe. Veja
[Validação e erros](../handlers/validation-and-errors.md).

## Segmentos abrangentes

`docs/[...path].nexy` serve `/docs/{path:path}`. Os segmentos restantes chegam como uma string,
barras incluídas.

```nexy filename="src/routes/docs/[...caminho].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` dá `path == "a/b/c"`.

## Grupos de rotas

Um diretório entre parênteses organiza os arquivos sem aparecer na URL. Ainda participa
[herança](../inheritance.md): seus `layout.*` e `dependencies.py` se aplicam ao que está dentro.

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

Use grupos para fornecer layouts diferentes a seções diferentes sem alterar seus URLs.

## Prioridade

As rotas estáticas vencem as dinâmicas, e as dinâmicas vencem as abrangentes:
`/blog/new` corresponde a `blog/new.nexy` antes de `blog/[slug].nexy`.

## Um arquivo por URL

Dois arquivos que resolvem para o mesmo URL são registrados. Não coloque `blog.nexy` próximo a
`blog/index.nexy`, ou misture `index.nexy` e `index.py` para o mesmo caminho.

## Próximas etapas

- [Páginas](README.md)
- [Páginas de erro](../errors/README.md)
- [Convenções de arquivo](../../../reference/file-conventions.md)