# Conceptos centrales

El modelo mental, antes de la API: cuatro niveles de lectura, luego las nociones que regresan en cada página. Cada noción tiene una línea aquí y un enlace a la página que profundiza.

## Cómo leer estos documentos

| Nivel | La pregunta que responde | Comienza con |
|---|---|---|
| Arquitectura de aplicación | qué capa responde a una solicitud y qué se niega a hacer | [Arquitectura](../architecture.md) |
| Estructura de la aplicación | dónde reside el código y en qué se convierte un archivo | [Estructura del proyecto](project-structure.md) |
| Presentación y renderizado | lo que ve el lector y quién produce el HTML | [Vistas](../views/README.md), [Renderizado](../rendering/README.md) |
| Interacción de la aplicación | qué hace el lector y qué se ejecuta en respuesta | [Acciones](../guides/actions.md) |

Los niveles se leen en ese orden una vez. Después de eso, la página que necesita es una búsqueda, no un curso.

## Arquitectura de aplicaciones

Tres formas de decidir qué código responde a una URL. Son alternativas, no capas:

- **Enrutamiento basado en archivos (FBR)**: un archivo en `src/routes/` es una ruta. El valor predeterminado.
- **Enrutador modular**: controladores y módulos bajo `src/apps/`, declarados con decoradores, para una base de código estilo NestJS.
- **Enrutador personalizado**: un FastAPI `APIRouter` existente incluido en la aplicación.

Elegir uno de los tres es una decisión. La elección de un marco de interfaz de usuario es otra opción independiente: consulte [Elija un enrutador](../routing/README.md) y [Vistas](../views/README.md).

## Estructura de la aplicación

Cinco nociones que un lector procedente de Next.js suele fusionar en una sola. No son lo mismo y la diferencia explica la mayoría de las preguntas de "por qué mi página no muestra".

| Noción | Qué es | Qué no es |
|---|---|---|
| **Ruta** | un patrón de URL, producido por la ruta de un archivo | un archivo: un archivo puede responder a varias URL (`[slug]`) |
| **Página** | un archivo de ruta que representa una vista: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | un punto final: responde a un documento, no a datos |
| **Vista** | lo que produce el cuerpo de una página: Jinja2 y Python, Markdown, o un componente cliente | una ruta: la misma vista puede servir varias páginas |
| **Componente** | una pieza reutilizable una página importa | una ruta: en modo servidor un componente nunca se sirve por sí solo |
| **Controlador de ruta** | la función de un archivo de ruta `.py`, llamado así por el método HTTP (`GET`, `POST`, …) | una página: devuelve JSON, un archivo o un `Response` |
| **Punto final** | el par (URL, método) que responde un controlador | un controlador: un archivo puede responder a varios puntos finales |

En una frase: **una página es un archivo de ruta, una vista es lo que la representa, un componente es lo que una página reutiliza, un controlador responde a un punto final.**

Dos palabras más que vuelven por todas partes:

- **Diseño**: un archivo `layout.*` que envuelve las páginas debajo de su carpeta; el raíz posee el documento HTML. Consulte [Diseños](../routing/fbr/layouts/README.md).
- **Dependencia**: una función que se ejecuta antes de un controlador, se aplica por ruta o por carpeta. Consulte [Dependencias](../routing/fbr/dependencies/README.md).

## Presentación y renderizado

Dos decisiones independientes, a menudo confundidas:

- **El formato** decide qué archivo representa la página: [Vistas](../views/README.md).
- **El modo** decide quién produce el HTML y cuándo: [Renderizado](../rendering/README.md).

| Noción | Una línea |
|---|---|
| Modo servidor | el servidor representa `.nexy` y `.md` páginas; los componentes son islas ([modos](../routing/fbr/modes.md)) |
| Modo cliente | `useCSR = True`: los archivos de marco son las rutas y la navegación se realiza en el navegador |
| SSR, ISR, CSR, islas | cuatro modos de renderizado, decididos por página excepto CSR, que es por proyecto ([renderizado](../rendering/README.md)) |
| Hidratación | el navegador adjuntando un framework al HTML el servidor ya envió ([islas](../rendering/islands.md)) |
| Props | los valores que un padre pasa a un componente, declarados `name: prop[type]` en un archivo `.nexy` (archivos [.nexy](../views/nexy/README.md)) |

## Interacción de la aplicación

| Noción | Una línea |
|---|---|
| Acción | una función Python marcada `@Action`, servida como `POST`, invocable desde un formulario o como una función escrita ([acciones](../guides/actions.md)) |
| Formulario | un formulario HTML que se publica en una acción, con errores de validación que regresan a la página ([acciones](../guides/actions.md)) |
| Enlaces de navegación | que precargan y enlaces que leen la ruta, la consulta, las cookies y la sesión ([hooks](../routing/fbr/navigation/hooks.md)) |
| Obtención de datos | realizada por la página o el controlador que lo necesita; Nexy no incluye ninguna capa de datos del cliente ([manejadores](../routing/fbr/handlers/README.md)) |

## Lo que Nexy no hace

La autenticación, autorización, base de datos, internacionalización, trabajos en segundo plano, correo electrónico, pagos y búsqueda son **responsabilidad de su aplicación**, no del marco. Nexy proporciona los puntos de extensión y dice dónde conectar cada uno: consulte [los límites](../architecture.md#boundaries).

La razón no es el minimalismo en sí: un marco que elige su ORM o su biblioteca de autenticación ha decidido algo que solo su aplicación puede decidir.

## Próximos pasos

- [Arquitectura](../architecture.md): las capas, y quién construye qué
- [Estructura del proyecto](project-structure.md): cada carpeta y archivo de un proyecto
- [Glosario](../reference/glossary.md): las mismas palabras, en un índice alfabético
- [Cómo funciona Nexy](how-nexy-works.md): una solicitud, paso a paso
