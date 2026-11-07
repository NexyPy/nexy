# Cree una aplicación de notas con Nexy, parte 1: cree el proyecto

La parte 1 del tutorial crea el proyecto que convertirá en una aplicación de notas y lo ejecuta en su navegador en aproximadamente cinco minutos.

**Antes de comenzar:** [uv](https://docs.astral.sh/uv/) y Node.js 20 o más reciente. El tutorial sigue el enrutador elegido en la parte superior del menú: cámbielo allí y cada parte mostrará los archivos de ese enrutador.

## que construiras

Al final del tutorial, la aplicación tiene páginas y una API JSON para notas, una base de datos, cuentas, notas compartidas por correo electrónico, actualizaciones en vivo, pruebas y una versión de producción. Cada parte termina con una aplicación que se ejecuta, por lo que puedes detenerte después de cualquiera de ellas.

## Crear el proyecto

```bash
uvx nexy new notes
```

Responde las preguntas de esta manera:

| Pregunta | respuesta |
|---|---|
| ¿Enrutador basado en archivos? | `Yes` para los enrutadores personalizados y basados en archivos, `No` para el modular |
| Tipo de proyecto | `Web` |
| Enrutamiento del lado del cliente | `No`: el servidor renderiza las páginas |
| Marco de cliente | `React`: vuelve en la unidad 4, para islas |
| Estilo | `Tailwind CSS` |
| Importar alias | `@` |
| ORM | `No database`: la parte 5 agrega uno |

<!-- router:custom -->
El enrutador personalizado es el basado en archivos más un `APIRouter` que ya tiene. El tutorial crea la aplicación con archivos; [Incluir un enrutador FastAPI existente](../routing/custom/README.md) muestra cómo montar el suyo junto a ellos.
<!-- /router -->

## ejecutarlo

```bash
cd notes
source .venv/bin/activate    # Windows: .venv\Scripts\activate
nexy dev
```

Abrir <http://localhost:3000>. Deberías ver la página de bienvenida. Deja `nexy dev` ejecutándose: a partir de ahora, cada archivo que guardes recargará el navegador.

## lo que aprendiste

- `uvx nexy new` crea un proyecto e instala sus paquetes Python y JavaScript.
- `nexy dev` lo sirve y se recarga al guardar.
<!-- router:fbr,custom -->
- Las páginas viven en `src/routes/`: la siguiente parte agrega una.
<!-- /router -->
<!-- router:modular -->
- Los controladores y sus vistas viven en `src/apps/`: la siguiente parte agrega una.
<!-- /router -->

## Próximos pasos

- [Parte 2: páginas y diseños](pages-and-layouts.md)
- [Estructura del proyecto](../getting-started/project-structure.md): para qué sirve cada archivo del proyecto
