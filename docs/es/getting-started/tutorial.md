# Tutorial de Nexy: crea una aplicación de notas paso a paso

El tutorial de Nexy crea una aplicación de notas desde una carpeta vacía hasta una versión de producción, una parte a la vez, y cada parte termina con una aplicación que se ejecuta.

¿Nuevo en Nexy? El [Inicio rápido](quick-start.md) muestra que se ejecuta en tres minutos; Vuelve aquí para aprender cómo funciona.

## Cómo funciona el tutorial

- **Una aplicación que crece.** Cada parte agrega una función a la aplicación de notas de la parte anterior.
- **Tu enrutador.** Las piezas siguen el enrutador elegido en la parte superior del menú: basado en archivos, modular o personalizado. Cambie allí y los archivos de cada sección cambiarán con él.
- **Código que se ejecuta.** Cada archivo con un nombre encima es un archivo completo, y el conjunto de pruebas reproduce las partes en orden en un proyecto nuevo: lo que copias es lo que se ejecuta.
- **Deténgase en cualquier lugar.** Cada parte dura de 10 a 20 minutos y termina con lo que debe verificar en el navegador.

## las partes

### Unidad 1: lo básico

| parte | lo que agregas | lo que aprendes |
|---|---|---|
| [1. Crea el proyecto](../tutorial/create-the-project.md) | un proyecto que se ejecuta | `nexy new`, `nexy dev` |
| [2. Páginas y diseños](../tutorial/pages-and-layouts.md) | la pagina de notas | páginas, vistas, el diseño |
| [3. Rutas dinámicas y una API](../tutorial/dynamic-routes.md) | `/notes/1` y `/api/notes` | Segmentos de URL, rutas JSON, `notFound` |
| [4. Componentes](../tutorial/components.md) | una tarjeta por nota | `.nexy` componentes y sus accesorios |

### Unidad 2: datos

| parte | lo que agregas | lo que aprendes |
|---|---|---|
| [5. Guarde las notas en SQLite](../tutorial/store-the-notes.md) | un modelo, una migración, una semilla | SQLModel, `nx migrate` |
| [6. Crea una nota a partir de un formulario](../tutorial/create-a-note.md) | un formulario que guarda una nota | Acciones, formularios sin JavaScript |
| [7. Mostrar errores de validación](../tutorial/validation-errors.md) | un mensaje encima del formulario | reglas en una Acción, `303`, `useSearchParams` |
| [8. Editar y eliminar una nota](../tutorial/edit-and-delete.md) | las formas de una nota | varias acciones por página, campos ocultos |
| [9. Paginar las notas](../tutorial/paginate-the-notes.md) | cinco notas por página | `offset` y `limit`, enlaces entre páginas |

### Unidad 3: usuarios

| parte | lo que agregas | lo que aprendes |
|---|---|---|
| [10. Crea una cuenta e inicia sesión](../tutorial/accounts.md) | registrarse, iniciar sesión, cerrar sesión | sesiones, hash de contraseñas |
| [11. Dale a cada usuario sus propias notas](../tutorial/own-notes.md) | notas que pertenecen a un usuario | claves foráneas, `redirect`, `401` |
| [12. Restablecer una contraseña olvidada por correo electrónico](../tutorial/password-reset.md) | un enlace de reinicio enviado por correo electrónico | `smtplib`, tokens firmados que caducan |

### Unidad 4: interactividad

| parte | lo que agregas | lo que aprendes |
|---|---|---|
| [13. Busca las notas mientras escribes](../tutorial/search-the-notes.md) | un cuadro de búsqueda que filtra a medida que escribes | React islas, accesorios de Python |
| [14. Marca una nota sin recargar la página](../tutorial/tick-a-note.md) | un botón Listo en cada nota | mejora progresiva, una acción para una forma y para `fetch` |

### Próximamente

| Unidad | Qué gana la aplicación |
|---|---|
| 5. Más allá de la petición | notas compartidas por correo electrónico en segundo plano, un resumen diario, actualizaciones en vivo |
| 6. barco | pruebas, páginas de error y registros, encabezados de seguridad, una compilación Docker |

## Próximos pasos

- [Parte 1: crear el proyecto](../tutorial/create-the-project.md)
- [Conceptos básicos](core-concepts.md): las palabras que utiliza el tutorial
