# Como adiciono sitemap.xml e robots.txt a um site Nexy?

Defina `useSiteUrl` em `nexyconfig.py`: Nexy então veicula `/sitemap.xml`, que lista todas as páginas estáticas do projeto, e um `/robots.txt` que aponta os mecanismos de pesquisa para ela.

## Ative-o com `useSiteUrl`

`useSiteUrl` é a origem pública do site, aquela que os motores de busca veem:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` e `nx start` então respondem ambos os arquivos. Sem `useSiteUrl` nenhum dos dois existe, então um projeto nunca publica a URL de seu servidor de desenvolvimento por engano.

## O que o mapa do site lista

O mapa do site fornece cada página como um URL absoluto em `useSiteUrl`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

Uma rota é listada quando responde HTML a um `GET` em um caminho fixo:

<!-- router:fbr,custom -->
- uma página (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`) é listada;
- uma página dinâmica, como `src/routes/users/[id].nexy`, é deixada de fora: Nexy não pode saber seus valores;
- um manipulador de rota Python responde JSON, portanto é deixado de fora.
<!-- /router -->

<!-- router:modular -->
- uma rota de controlador que responde a HTML, com `@UseResponse(response_class=HTMLResponse)`, é listada;
- uma rota com um parâmetro de caminho, como `/users/{id}`, é deixada de fora: Nexy não pode saber seus valores;
- uma rota que responde a JSON é deixada de fora.
<!-- /router -->

Uma rota oculta do esquema da API (`include_in_schema=False`) também foi deixada de fora.

## O `robots.txt` que serve

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## Em vez disso, escreva o seu próprio

Seu próprio arquivo sempre vence e o Nexy nunca o sobrescreve:

- `public/robots.txt` ou `public/sitemap.xml` é servido como está, da mesma forma que todo arquivo de `public/` é;
- uma rota do projeto em `/robots.txt` ou `/sitemap.xml` mantém seu caminho.

Escreva seu próprio mapa do site para listar páginas dinâmicas, como um URL por postagem do blog.

## Próximas etapas

- [Metadados da página](../routing/fbr/pages/metadata.md): o título e a descrição que os mecanismos de pesquisa mostram
- [Configuração](../reference/config.md): todas as configurações de `nexyconfig.py`
- [Implantação](../deployment/README.md): servir o projeto em produção
