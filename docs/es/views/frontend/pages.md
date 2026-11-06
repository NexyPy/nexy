# Páginas frontales

Una **Página** es la unidad básica de una aplicación Nexy. Es un recurso direccionable por URL definido por un archivo en `src/routes/`. 

Independientemente del marco de cliente utilizado, cada página sigue el mismo ciclo de vida universal y restricciones arquitectónicas.

## El ciclo de vida de la página

Cuando un usuario navega a una página, Nexy realiza los siguientes pasos:

1.  **Coincidencia de rutas**: El enrutador identifica el archivo correspondiente a la URL.
2.  **Obtención de datos**: el servidor ejecuta el front-matter de la página Python para recuperar los datos que necesita.
3.  **Composición**: la página se ajusta a su `layout.nexy` más cercano (o diseño de marco).
4.  **Representación**: el resultado se representa en HTML (a través de Jinja2, Markdown o framework SSR).
5.  **Hidratación**: si la página utiliza un marco de cliente, el navegador adjunta la lógica interactiva al HTML estático.

Pasos 2 a 4 en una página en modo servidor: el frontmatter busca, la plantilla representa y el diseño raíz envuelve el resultado.

```nexy filename="src/rutas/usuarios.nexy"
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

## Enrutamiento y URL

El enrutamiento se basa estrictamente en archivos. La URL está determinada por la ruta del archivo en `src/routes/`, menos la extensión.

```text
src/routes/
├─ index.tsx            /
├─ about.tsx            /about
└─ blog/
   ├─ index.tsx         /blog
   └─ [slug].tsx        /blog/hello-world
```

### Segmentos dinámicos
Para crear una ruta que varía según el parámetro (por ejemplo, un perfil de usuario), utilice corchetes:
- `src/routes/user/[id].tsx` → `/user/123`

El valor del segmento (`123`) está disponible para la página a través del enlace `useParams()` desde `@nexy/client`.

```tsx filename="src/rutas/usuario/[id].tsx"
import { useParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  return <h1>User {id}</h1>;
}
```

### Grupos de rutas
El enrutador ignora las carpetas entre paréntesis, pero le permiten agrupar archivos con fines organizativos o diseños compartidos:
- `src/routes/(auth)/login.tsx` → `/login`

```text
src/routes/
├─ layout.tsx
└─ (auth)/
   ├─ layout.tsx        wraps /login and /signup only
   ├─ login.tsx         /login
   └─ signup.tsx        /signup
```

## Metadatos de página
Cada página puede definir metadatos (título, descripción, etiquetas OpenGraph) que Nexy inyecta en el shell del documento. Una página `.nexy` lo establece en su portada, con un literal o con `setMetadata`:

```nexy filename="src/rutas/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

`setMetadata` es Python: una página `.tsx`, `.vue` o `.svelte` no tiene exportación `metadata`, por lo que en modo cliente escriba el título y las metaetiquetas en el diseño raíz. Consulte [Metadatos de la página](../../routing/fbr/pages/metadata.md) para cada campo.

## Implementación del marco
Los conceptos anteriores son universales. Para ver cómo implementar una página en su marco específico, consulte la guía **Diferencias**:

- [React Diferencias](../react/differences.md)
- [Vue Diferencias](../vue/differences.md)
- [Svelte Diferencias](../svelte/differences.md)
- [Solid Diferencias](../solid/differences.md)
- [Preact Diferencias](../preact/differences.md)
