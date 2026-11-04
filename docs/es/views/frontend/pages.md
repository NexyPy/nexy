# Páginas de inicio

Una **Página** es la unidad básica de una aplicación Nexy. Es un recurso direccionable por URL definido por un archivo en `src/routes/`. 

Independientemente del marco de cliente utilizado, cada página sigue el mismo ciclo de vida universal y restricciones arquitectónicas.

## El ciclo de vida de la página

Cuando un usuario navega a una página, Nexy realiza los siguientes pasos:

1.  **Coincidencia de rutas**: El enrutador identifica el archivo correspondiente a la URL.
2.  **Obtención de datos**: el servidor ejecuta la lógica de la página (frontmatter de Python o cargador de marco) para recuperar los datos requeridos.
3.  **Composición**: La página está envuelta en su `layout.nexy` (o diseño de marco) más cercano.
4.  **Representación**: El resultado se representa en HTML (a través de Jinja2, Markdown o framework SSR).
5.  **Hidratación**: Si la página utiliza un marco de cliente, el navegador adjunta la lógica interactiva al HTML estático.

## Enrutamiento y URL

El enrutamiento se basa estrictamente en archivos. La URL está determinada por la ruta del archivo en `src/routes/`, menos la extensión.

### Segmentos dinámicos
Para crear una ruta que varía según el parámetro (por ejemplo, un perfil de usuario), utilice corchetes:
- `src/routes/user/[id].tsx` → `/user/123`

El valor del segmento (`123`) está disponible para la página a través del enlace `useParams()` desde `@nexy/client`.

### Grupos de rutas
El enrutador ignora las carpetas entre paréntesis, pero le permiten agrupar archivos con fines organizativos o diseños compartidos:
- `src/routes/(auth)/login.tsx` → `/login`

## Metadatos de página
Cada página puede definir metadatos (título, descripción, etiquetas OpenGraph) que Nexy inyecta en el shell del documento. En los archivos `.nexy`, esto se hace al principio; en archivos de marco, se proporciona mediante una exportación `metadata`.

## Implementación del marco
Los conceptos anteriores son universales. Para ver cómo implementar una página en su marco específico, consulte la guía **Diferencias**:

- [Reaccionar diferencias](../react/differences.md)
- [Diferencias de Vue](../vue/differences.md)
- [Diferencias esbeltas](../svelte/differences.md)
- [Diferencias sólidas](../solid/differences.md)
- [Preact Diferencias](../preact/differences.md)