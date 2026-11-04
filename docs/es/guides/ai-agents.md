# Agentes codificadores

Un proyecto realizado con `nx new` incluye las reglas que un agente de codificación necesita para escribir código Nexy a su manera:
el orden de trabajo, el código y las reglas de escritura, y una habilidad por tema. Esta página dice lo que obtienes,
adónde va y cómo mantenerlo actualizado. Trabajar en Nexy en sí es un trabajo diferente: lea el
raíz del repositorio `AGENTS.md`.

## Qué añade `nx new`

| Archivo | Leído por | Retiene |
|---|---|---|
| `AGENTS.md` | Codex, OpenCode | la pila del proyecto, el orden de trabajo, las reglas, la lista de habilidades |
| `CLAUDE.md` | Código Claude | una línea, `@AGENTS.md`, por lo que ambos leen el mismo texto |
| `.agents/skills/` | Codex, OpenCode | las habilidades |
| `.claude/skills/` | Claude Code, OpenCode | las mismas habilidades |

`AGENTS.md` es breve y personalizado. Un proyecto Vue enrutado por el cliente dice "enrutado por el cliente, Vue, con estilo
con viento de cola"; A un proyecto API se le dice que no hay vistas. Sólo se copian las habilidades que encajan:
El proyecto React obtiene `nexy-react` y no tiene habilidad de Vue, un proyecto de servidor obtiene `.nexy` y Markdown
habilidades, un proyecto API no adquiere ninguna habilidad sobre las vistas.

Para omitirlo todo, cree el proyecto con `nx new --no-agents`.

## Las habilidades

| Habilidad | Cubiertas |
|---|---|
| `nexy-principles` | orden de trabajo, reglas del código, reglas de redacción |
| `nexy-ux-audit` | la experiencia y la auditoría de arquitectura de la información que se debe ejecutar antes de cualquier vista |
| `nexy-project` | modos, carpetas, convenciones de archivos, configuración, comandos |
| `nexy-file` | `.nexy` páginas, atrezzo, ganchos, islas |
| `nexy-markdown` | `.md` y `.mdx` contenido |
| `nexy-react`, `nexy-preact`, `nexy-solid`, `nexy-vue`, `nexy-svelte` | código idiomático para el marco del cliente |
| `nexy-styling` | Tailwind, UnoCSS o CSS simple y los tokens de diseño |
| `nexy-backend` | Controladores API, acciones, WebSocket, ISR, middleware |
| `nexy-modular` | controladores, módulos, inyección y guardas del router modular |
| `nexy-security` | dependencias, entradas, sesiones, autorización, secretos |
| `nexy-testing` | el primer bucle de prueba y las puertas |
| `nexy-framework-dev` | cambiando Nexy en sí, en lugar de un proyecto creado con Nexy |

Las reglas que imponen: auditar la experiencia antes de crear una vista, escribir la prueba fallida primero,
una función realiza un tratamiento, una clase conlleva una intención, una carpeta contiene un conjunto de
intenciones relacionadas, sin emoji, íconos SVG reales, texto sin formato escrito para personas y sin escritos a mano
Scripts DOM en React, Vue, Svelte, Solid o Preact.

## Agregarlos a un proyecto existente

```bash
nx skills
```

Ejecútelo en la raíz del proyecto. Lee `nexyconfig.py` y `package.json` para encontrar la pila,
copia las habilidades de emparejamiento y escribe `AGENTS.md` y `CLAUDE.md` cuando faltan.

Nunca sobrescribe un archivo que usted escribió: se conserva un `AGENTS.md` o `CLAUDE.md` existente y el
El comando te lo dice. Agregue la lista de habilidades a su propio archivo manualmente si la desea allí. una habilidad de
el tuyo en `.claude/skills/` o `.agents/skills/` se deja en paz; sólo las habilidades `nexy-*` son
renovado.

Ejecute `nx skills` nuevamente después de actualizar Nexy para actualizar las copias y confirme el resultado para que
Todo el equipo lo comparte.

## Cómo los encuentra un agente

- `AGENTS.md` (o `CLAUDE.md`, que lo importa) se lee al inicio de cada sesión. nombra
  las habilidades.
- Cada habilidad comienza con un nombre y una descripción que dice qué cubre y cuándo cargarla. el
  El agente los lee primero y abre una habilidad solo cuando la tarea coincide.

Las habilidades siguen el [formato de Habilidades del Agente](https://agentskills.io/specification) abierto, por lo que otras
Los agentes que leen carpetas `SKILL.md` también pueden usarlas.

## Lo que no hacen

Las habilidades le dicen a un agente cómo trabajar; no hacen que su salida sea correcta. Guarde sus propios cheques:

- Lea lo que cambió el agente.
- Ejecute `nx check`, `nx test` y `nx build`. Las habilidades exigen esto y que el resultado sea
  informado, no resumido.
- Auditar las dependencias que agrega el agente (`nexy-security` explica cómo).

Los ejemplos en las habilidades son verificados por las propias pruebas de Nexy: las importaciones existen, la configuración
Los campos existen, los comandos existen, los análisis de Python. Eso capta la deriva, no el error de juicio.

## Mapa

Un agente responde más rápido cuando sabe qué página contiene la respuesta.

| Necesitas | Leer |
|---|---|
| el producto, en una sola página | [README](../README.md) |
| para ejecutar un proyecto | [introducción](../getting-started/quick-start.md) |
| URL de un archivo | [enrutamiento](../routing/README.md) |
| segmentos dinámicos, diseños, páginas de error | [páginas](../routing/fbr/pages/README.md) |
| la ruta actual, consulta, cookies, sesión | [hooks](../routing/fbr/navigation/hooks.md) |
| para editar una página | [archivos .nexy](../views/nexy/README.md) o [vistas](../views/README.md) |
| Markdown o MDX | [markdown](../views/nexy/markdown.md) |
| asistentes HTML integrados | [componentes](../views/nexy/components.md) |
| modo de renderizado | [SSR](../rendering/ssr.md), [CSR](../rendering/csr.md), [ISR](../rendering/isr.md) |
| un WebSocket | [websocket](../routing/fbr/realtime/websocket.md) |
| controladores y módulos | [modulares](../routing/modular/README.md) |
| para agregar un punto final | [API](../routing/fbr/handlers/README.md) |
| un formulario publicado desde una página | [acciones](actions.md) |
| por qué falló una solicitud y qué página la responde | [excepciones](../reference/exceptions.md) |
| traducciones | [i18n](i18n.md) |
| un campo de configuración | [config](../reference/config.md) |
| para probar la aplicación | [probando](testing.md) |
| la compilación del cliente | [frontend](frontend.md) |

## Invariantes del proyecto

Se genera 1. `__nexy__/`. Nunca lo edites, nunca lo confirmes. Elimínelo para forzar una compilación limpia.
2. Un archivo por URL. `index.nexy` y `index.py` para la misma ruta es un error, no una regla de prioridad.
3. Nombres reservados dentro de `src/routes/`: `layout.nexy`, `loading.nexy`, `errors.nexy`,
   `notfound.nexy`, `dependencies.py`, `__init__.py`. No los utilices para contenido.
4. `.nexy` el frontmatter es Python que se ejecuta por solicitud. Sin efectos secundarios a nivel de módulo: sin archivo
   identificadores, sin conexiones a bases de datos, sin llamadas de red en el momento de la importación.
5. `.py` en `src/routes/` es un controlador de API. Los métodos son nombres de funciones (`GET`, `POST`, ...).
6. La configuración vive en `nexyconfig.py`, no en variables de entorno ni en lugares dispersos.
   constantes.
7. El escape automático está desactivado en las plantillas `.nexy`: escape de valores que no son de confianza con `| e`.

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

Cuando los documentos y el código no estén de acuerdo, confíe en el código y dígalo: `nexy/core/config.py` cumple con todos
opción, `nexy/modules/routers/fbrouter/` las reglas de enrutamiento, `nexy/modules/compiler/` cómo `.nexy`
Los archivos se convierten en módulos.

## Próximos pasos

- [CLI](../reference/cli.md): `nx new` y `nx skills`
- [Convenciones de archivo](../reference/file-conventions.md): nombres reservados y reglas de enrutamiento
- [Glosario](../reference/glossary.md): las palabras en las que se basan estas reglas
- [Seguridad](../reference/security.md): la versión reduce los puntos de habilidad de seguridad a