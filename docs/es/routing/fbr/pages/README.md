# Páginas

Un archivo de página devuelve HTML. El tipo de archivo que utilice cambia la forma en que se produce: consulte
[vistas](../../../views/README.md). Esta sección cubre las reglas de enrutamiento que se aplican a cada página.
formato.

| Página | Qué cubre |
|---|---|
| [Rutas dinámicas](dynamic-routes.md) | `[slug]`, `[...path]`, grupos de rutas, segmentos tipificados |
| [Páginas de error](../errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON para clientes API |
| [Diseños](../layouts/README.md) | Una página por tipo de archivo de diseño |
| [Herencia](../inheritance.md) | Cómo se acumulan los diseños y las dependencias |

## Una página mínima

```nexy filename="src/rutas/about.nexy"
---
title: prop[str] = "About"
---
<h1>{{ title }}</h1>
```

Se sirve en `/about`. El tema principal entre las líneas `---` es Python; el marcado debajo es
Jinja2. Consulte [archivos .nexy](../../../views/nexy/README.md).

## Formatos de página

| Modo | Archivo | Produce |
|---|---|---|
| Servidor | `.nexy` | HTML renderizado por servidor desde Python y Jinja2 |
| Servidor | `.md`, `.mdx` | páginas de contenido |
| Cliente | `.tsx`, `.jsx`, `.vue`, `.svelte` | componentes del framework, renderizados y navegados en el navegador |

Los dos modos no se pueden mezclar en un solo proyecto. Consulte [Modo servidor y modo cliente](../modes.md).
Los componentes del cliente aún pueden aparecer en modo servidor, como [islas](../../../rendering/islands.md)
dentro de una página `.nexy`.

## Caché incremental

Agregue `revalidate = 60` a una página `.nexy` para almacenarla en caché con obsoleto mientras se revalida. Ver
[ISR](../../../rendering/isr.md).

## Leyendo la solicitud

Una página lee la ruta, la cadena de consulta, las cookies y la sesión a través de ganchos. Ver
[Ganchos](../navigation/hooks.md).

## Próximos pasos

- [Rutas dinámicas](dynamic-routes.md)
- [Páginas de error](../errors/README.md)
- [Enrutamiento modular](../../modular/README.md): controladores en lugar de archivos