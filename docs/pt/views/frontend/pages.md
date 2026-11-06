# Páginas de front-end

Uma **Página** é a unidade básica de um aplicativo Nexy. É um recurso endereçável por URL definido por um arquivo em `src/routes/`. 

Independentemente da estrutura do cliente usada, cada página segue o mesmo ciclo de vida universal e restrições arquitetônicas.

## O ciclo de vida da página

Quando um usuário navega para uma página, Nexy executa as seguintes etapas:

1.  **Route Matching**: O roteador identifica o arquivo correspondente à URL.
2.  **Busca de dados**: O servidor executa o frontmatter da página Python para buscar os dados necessários.
3.  **Composição**: A página é agrupada em seu `layout.nexy` mais próximo (ou layout de estrutura).
4.  **Renderização**: O resultado é renderizado em HTML (via Jinja2, Markdown ou framework SSR).
5.  **Hidratação**: Se a página usa uma estrutura cliente, o navegador anexa a lógica interativa ao HTML estático.

Etapas 2 a 4 em uma página no modo servidor: o frontmatter busca, o modelo é renderizado e o layout raiz envolve o resultado.

```nexy filename="src/routes/users.nexy"
---
from src.users import all_users

users = all_users()
---
<h1>Users</h1>
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Roteamento e URLs

O roteamento é estritamente baseado em arquivo. A URL é determinada pelo caminho do arquivo em `src/routes/`, menos a extensão.

```text
src/routes/
├─ index.tsx            /
├─ about.tsx            /about
└─ blog/
   ├─ index.tsx         /blog
   └─ [slug].tsx        /blog/hello-world
```

### Segmentos Dinâmicos
Para criar uma rota que varia de acordo com o parâmetro (por exemplo, um perfil de usuário), use colchetes:
- `src/routes/user/[id].tsx` → `/user/123`

O valor do segmento (`123`) está disponível para a página através do gancho `useParams()` de `@nexy/client`.

```tsx filename="src/rotas/usuário/[id].tsx"
import { useParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  return <h1>User {id}</h1>;
}
```

### Grupos de rotas
As pastas entre parênteses são ignoradas pelo roteador, mas permitem agrupar arquivos para fins organizacionais ou layouts compartilhados:
- `src/routes/(auth)/login.tsx` → `/login`

```text
src/routes/
├─ layout.tsx
└─ (auth)/
   ├─ layout.tsx        wraps /login and /signup only
   ├─ login.tsx         /login
   └─ signup.tsx        /signup
```

## Metadados da página
Cada página pode definir metadados (título, descrição, tags OpenGraph) que Nexy injeta no shell do documento. Uma página `.nexy` define-o em seu frontmatter, com um literal ou com `setMetadata`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

`setMetadata` é Python: uma página `.tsx`, `.vue` ou `.svelte` não tem exportação `metadata`, portanto, no modo cliente, escreva o título e as meta tags no layout raiz. Consulte [Metadados da página](../../routing/fbr/pages/metadata.md) para cada campo.

## Implementação da Estrutura
Os conceitos acima são universais. Para ver como implementar uma página em seu framework específico, consulte o guia **Diferenças**:

- [React Diferenças](../react/differences.md)
- [Vue Diferenças](../vue/differences.md)
- [Svelte Diferenças](../svelte/differences.md)
- [Solid Diferenças](../solid/differences.md)
- [Preact Diferenças](../preact/differences.md)
