# Agentes codificadores

Un proyecto realizado con `nx new` incluye las reglas que un agente codificador necesita para escribir código Nexy a su manera: el orden de trabajo, el código y las reglas de escritura, y una habilidad por tema. Esta página dice lo que obtiene, adónde va y cómo mantenerlo actualizado. Trabajar en Nexy en sí es un trabajo diferente: leer la raíz del repositorio `AGENTS.md`.

## Lo que `nx new` agrega

| Archivo | Leído por | Retiene |
|---|---|---|
| `AGENTS.md` | Codex, OpenCode | la pila del proyecto, el orden de trabajo, las reglas, la lista de habilidades |
| `CLAUDE.md` | Claude Code | una línea, `@AGENTS.md`, por lo que ambos leen el mismo texto |
| `.agents/skills/` | Codex, OpenCode | las habilidades |
| `.claude/skills/` | Claude Code, OpenCode | las mismas habilidades |

`AGENTS.md` es breve y personalizado. Un proyecto Vue enrutado por el cliente dice "enrutado por el cliente, Vue, con el estilo Tailwind"; A un proyecto API se le dice que no hay vistas. Solo se copian las habilidades que encajan: un proyecto React obtiene `nexy-react` y ninguna habilidad Vue, un proyecto de servidor obtiene las habilidades `.nexy` y Markdown, un proyecto API no obtiene ninguna habilidad sobre las vistas.

Para omitirlo todo, cree el proyecto con `nx new --no-agents`.

## las habilidades

| Habilidad | Cubiertas |
|---|---|
| `nexy-principles` | orden de trabajo, reglas del código, reglas de redacción |
| `nexy-ux-audit` | la experiencia y la auditoría de arquitectura de la información para ejecutar antes de cualquier vista |
| `nexy-project` | modos, carpetas, convenciones de archivos, configuración, comandos |
| `nexy-file` | `.nexy` páginas, atrezzo, ganchos, islas |
| `nexy-markdown` | `.md` y `.mdx` contenido |
| `nexy-react`, `nexy-preact`, `nexy-solid`, `nexy-vue`, `nexy-svelte` | código idiomático para el marco del cliente |
| `nexy-styling` | Tailwind, UnoCSS o CSS simple, y los tokens de diseño |
| `nexy-backend` | Controladores API, acciones, WebSocket, ISR, middleware |
| `nexy-modular` | controladores, módulos, inyección y guardas del router modular |
| `nexy-security` | dependencias, entradas, sesiones, autorización, secretos |
| `nexy-testing` | el bucle de prueba primero y las puertas |
| `nexy-framework-dev` | cambiando Nexy en sí, en lugar de un proyecto creado con Nexy |

Las reglas que imponen: auditar la experiencia antes de crear una vista, escribir la prueba fallida primero, una función realiza un tratamiento, una clase conlleva una intención, una carpeta contiene un conjunto de intenciones relacionadas, sin emoji, íconos SVG reales, texto sin formato escrito para personas y sin scripts DOM escritos a mano en React, Vue, Svelte, Solid o Preact.

## Agréguelos a un proyecto existente

```bash
nx skills
```

Ejecútelo en la raíz del proyecto. Lee `nexyconfig.py` y `package.json` para encontrar la pila, copia las habilidades correspondientes y escribe `AGENTS.md` y `CLAUDE.md` cuando faltan.

Nunca sobrescribe un archivo que usted escribió: un `AGENTS.md` o `CLAUDE.md` existente se conserva y el comando se lo indica. Agregue la lista de habilidades a su propio archivo manualmente si la desea allí. Una habilidad propia en `.claude/skills/` o `.agents/skills/` se deja sola; sólo se actualizan las habilidades `nexy-*`.

Ejecute `nx skills` nuevamente después de actualizar Nexy para actualizar las copias y confirme el resultado para que todo el equipo lo comparta.

## Cómo los encuentra un agente

- `AGENTS.md` (o `CLAUDE.md`, que lo importa) se lee al inicio de cada sesión. Nombra las habilidades.
- Cada habilidad comienza con un nombre y una descripción que dice qué cubre y cuándo cargarla. El agente los lee primero y abre una habilidad solo cuando la tarea coincide.

Las habilidades siguen el [formato de habilidades del agente](https://agentskills.io/specification) abierto, por lo que otros agentes que leen las carpetas `SKILL.md` también pueden usarlas.

## lo que no hacen

Las habilidades le dicen a un agente cómo trabajar; no hacen que su salida sea correcta. Guarde sus propios cheques:

- Lea lo que cambió el agente.
- Ejecute `nx check`, `nx test` y `nx build`. Las habilidades exigen esto y que se informe del resultado, no que se resuma.
- Auditar las dependencias que agrega el agente (`nexy-security` explica cómo).

Los ejemplos en las habilidades son verificados por las propias pruebas de Nexy: las importaciones existen, los campos de configuración existen, los comandos existen, los Python análisis. Eso capta la deriva, no el error de juicio.

## Mapa

Un agente responde más rápido cuando sabe qué página contiene la respuesta.

| Necesitas | Leer |
|---|---|
| el producto, en una sola página | [README](../README.md) |
| para ejecutar un proyecto | [introducción](../getting-started/quick-start.md) |
| la URL de un archivo | [enrutamiento](../routing/README.md) |
| segmentos dinámicos, diseños, páginas de error | [páginas](../routing/fbr/pages/README.md) |
| la ruta actual, consulta, cookies, sesión | [hooks](../routing/fbr/navigation/hooks.md) |
| para editar una página | [archivos .nexy](../views/nexy/README.md) o [vistas](../views/README.md) |
| Markdown o MDX | [rebaja](../views/nexy/markdown.md) |
| asistentes HTML integrados | [componentes](../views/nexy/components.md) |
| modo de renderizado | [SSR](../rendering/ssr.md), [CSR](../rendering/csr.md), [ISR](../rendering/isr.md) |
| a WebSocket | [websocket](../routing/fbr/realtime/websocket.md) |
| controladores y módulos | [modulares](../routing/modular/README.md) |
| para agregar un punto final | [API](../routing/fbr/handlers/README.md) |
| un formulario publicado desde una página | [acciones](actions.md) |
| por qué falló una solicitud y qué página la responde | [excepciones](../reference/exceptions.md) |
| traducciones | [i18n](i18n.md) |
| un campo de configuración | [configuración](../reference/config.md) |
| para probar la aplicación | [pruebas](testing.md) |
| la compilación del cliente | [frontend](frontend.md) |

## Invariantes del proyecto

1. Se genera `__nexy__/`. Nunca lo edites, nunca lo confirmes. Elimínelo para forzar una compilación limpia.
2. Un archivo por URL. `index.nexy` y `index.py` para la misma ruta es un error, no una regla de prioridad.
3. Nombres reservados dentro de `src/routes/`: `layout.nexy`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `__init__.py`. No los utilices para contenido.
4. `.nexy` el front-matter es Python que se ejecuta por solicitud. Sin efectos secundarios a nivel de módulo: sin identificadores de archivos, sin conexiones de bases de datos, sin llamadas de red al importar.
5. `.py` en `src/routes/` es un controlador de API. Los métodos son nombres de funciones (`GET`, `POST`, ...).
6. La configuración se encuentra en `nexyconfig.py`, no en variables de entorno ni en constantes dispersas.
7. El escape automático está desactivado en las plantillas `.nexy`: escape de los valores que no son de confianza con `| e`.

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

Cuando los documentos y el código no estén de acuerdo, confíe en el código y dígalo: `nexy/core/config.py` contiene todas las opciones, `nexy/modules/routers/fbrouter/` las reglas de enrutamiento, `nexy/modules/compiler/` cómo `.nexy` los archivos se convierten en módulos.

## Próximos pasos

- [CLI](../reference/cli.md): `nx new` y `nx skills`
- [Convenciones de archivo](../reference/file-conventions.md): nombres reservados y reglas de enrutamiento
- [Glosario](../reference/glossary.md): las palabras en las que se basan estas reglas
- [Seguridad](../reference/security.md): la versión reduce los puntos de habilidad de seguridad a
