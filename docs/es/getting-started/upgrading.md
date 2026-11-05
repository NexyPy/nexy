# Actualizando a 2.2

Qué cambia en un proyecto existente cuando se pasa de 2.1 a 2.2 y qué hacer al respecto. La lista completa está en el [registro de cambios](../../CHANGELOG.md).

```bash
uv add "nexy>=2.2"            # or: uv tool upgrade nexy
nx build
nx test
```

## Lo que quizás tengas que cambiar

| Cambiar | Hacer esto |
|---|---|
| **`.mdx` es compilado por Vite únicamente.** El compilador Python ya no lo procesa | Mantenga React o Preact en `useFF` e instale `@mdx-js/rollup`, `remark-gfm` y `@mdx-js/react`. Una página sin componentes puede ser un archivo `.md` en lugar de |
| **`useBadge` desapareció.** La etiqueta "Construido con Nexy" ya no existe | Elimina la línea de `nexyconfig.py`. Se ignora una línea sobrante |
| **`nx check` ya no compila `.mdx`** | Nada: Vite informa MDX errores en la compilación |

## que sigue igual

- Tus rutas, trazados, acciones y configuración.
- Los proyectos existentes mantienen sus propias páginas de inicio. El nuevo diseño inicial solo se aplica a proyectos creados después de la actualización.
- La barra de herramientas de desarrollo y `useDevTools`.

## Nuevo en 2.2

- **Archivos de agentes.** `nx new` escribe `AGENTS.md`, `CLAUDE.md` y las habilidades para codificar agentes. Para un proyecto que ya tienes, ejecuta `nx skills`. Nunca sobrescribe un archivo que usted escribió. Ver [Agentes codificadores](../guides/ai-agents.md).
- **Un servidor de desarrollo que sigue ejecutándose.** Cuando su aplicación no puede iniciarse, `nx dev` informa el motivo y espera el siguiente cambio en lugar de salir.
- **Un nuevo iniciador** para cada marco en Tailwind o UnoCSS, con las mismas páginas y componentes.
- **UnoCSS lee `.nexy` archivos** en un proyecto de servidor. Si utiliza UnoCSS con páginas `.nexy`, agregue el bloque `content` que se muestra en [Solución de problemas](../guides/troubleshooting.md).

## Documentación corregida

Tres páginas decían algo que el código no hace. Si los seguiste, revisa tus archivos:

- Un componente `.nexy` coloca a sus hijos con `<Slot />` (S mayúscula), no con `<slot />`.
- Un archivo de componente `.nexy` tiene un nombre en PascalCase: se importa como un módulo Python, por lo que un guión no se compila.
- Para `.mdx`, el marco es Preact cuando el archivo importa `preact`, React en caso contrario.

## donde sigue

- [Índice de documentación](../README.md): la página de lo que estás creando
- [Solución de problemas](../guides/troubleshooting.md): los problemas a los que se enfrenta primero la gente
- [Configuración](../reference/config.md): cada campo `use*` y su valor predeterminado
