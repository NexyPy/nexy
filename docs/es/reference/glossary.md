# Glosario

Las palabras que utilizan estos documentos, una línea cada una, en orden alfabético. Un término que necesita más de una línea tiene una página: sigue el enlace. Para saber cómo encajan las nociones, lea [Conceptos básicos](../getting-started/core-concepts.md).

## Términos

| Término | En una línea |
|---|---|
| Acción | una función Python marcada `@Action`, servida como `POST` y invocable desde el cliente ([acciones](../guides/actions.md)) |
| ASGI | la interfaz Uvicorn habla, implementada por FastAPI y Starlette |
| Modo cliente | `useCSR = True`: los archivos framework son las rutas y el navegador navega ([modos](../routing/fbr/modes.md)) |
| Componente | un bloque de construcción de interfaz de usuario reutilizable que se utiliza para componer una vista ([vistas](../views/README.md)) |
| CSR | renderizado del lado del cliente: el navegador renderiza las páginas después del primer documento ([CSR](../rendering/csr.md)) |
| Dependencia | una función FastAPI se ejecuta antes de un controlador, por ruta o por carpeta ([dependencias](../routing/fbr/dependencies/README.md)) |
| Documento shell | los `<html>`, `<head>` y `<body>` alrededor de una página, propiedad del diseño más cercano o de Nexy ([diseños](../routing/fbr/layouts/README.md)) |
| Punto final | la combinación única de una URL y un método HTTP ([vistas](../views/README.md)) |
| FBR | enrutamiento basado en archivos: un archivo en `src/routes/` es una ruta ([enrutamiento](../routing/fbr/README.md)) |
| Frontmatter | el bloque Python entre las dos `---` líneas de un archivo `.nexy` o `.md` (archivos [.nexy](../views/nexy/README.md)) |
| Guarda | una dependencia que rechaza una solicitud levantando `HTTPException` ([guardas](../routing/modular/guards-and-metadata.md)) |
| Controlador | una función Python que maneja una solicitud HTTP para un método específico ([vistas](../views/README.md)) |
| Reemplazo de módulo en caliente HMR |: el servidor de desarrollo intercambia los módulos que cambiaron, sin una recarga completa ([frontend](../guides/frontend.md)) |
| Hidratación | el navegador adjuntando un framework al HTML el servidor ya envió ([islas](../rendering/islands.md)) |
| Isla | un componente de cliente montado dentro de una página renderizada por el servidor ([islas](../rendering/islands.md)) |
| ISR | regeneración estática incremental: una página almacenada en caché por ruta, actualizada en segundo plano ([ISR](../rendering/isr.md)) |
| Diseño | un archivo `layout.*` que envuelve las páginas debajo de su carpeta ([diseños](../routing/fbr/layouts/README.md)) |
| Rutas del enrutador modular | declaradas con `@Module` y `@Controller` en `src/apps/` ([modular](../routing/modular/README.md)) |
| Página | un recurso direccionable por URL definido por un archivo en `src/routes/` ([vistas](../views/README.md)) |
| Precargar | cargar la página detrás de un enlace antes de que el lector haga clic en él ([enlaces](../routing/fbr/navigation/linking-and-navigating.md)) |
| Props | los valores que un padre pasa a un componente ([archivos .nexy](../views/nexy/README.md)) |
| Revalidar | el número de segundos después de los cuales se reconstruye una página ISR en segundo plano ([ISR](../rendering/isr.md)) |
| Ruta | un patrón de URL, producido por la ruta de un archivo de ruta ([enrutamiento](../routing/README.md)) |
| Grupo de rutas | una carpeta entre paréntesis que agrupa rutas sin agregar un segmento ([rutas dinámicas](../routing/fbr/pages/dynamic-routes.md)) |
| Controlador de ruta | la función `GET`, `POST`, … de un archivo de ruta `.py` ([manejadores](../routing/fbr/handlers/README.md)) |
| Modo de servidor | `useCSR = False`, el valor predeterminado: el servidor representa las páginas `.nexy` y `.md` ([modos](../routing/fbr/modes.md)) |
| Habilidad | una carpeta con un `SKILL.md` que le enseña a un agente de codificación una parte de Nexy ([agentes de codificación](../guides/ai-agents.md)) |
| SSG | generación de sitios estáticos; **no es un modo Nexy**: el servidor siempre lee el HTML creado con anticipación ([renderizado](../rendering/README.md)) |
| Representación del lado del servidor SSR |: el servidor representa cada página para su solicitud, y es el valor predeterminado ([SSR](../rendering/ssr.md)) |
| Ver | el proceso de producción del cuerpo de respuesta de una página ([vistas](../views/README.md)) |

## Archivos y carpetas

| Nombre | En una línea |
|---|---|
| `__nexy__/` | salida generada: páginas compiladas, la entrada del cliente y la acción del cliente; nunca editado, nunca comprometido |
| `nexyconfig.py` | la configuración del proyecto, una clase de `use*` campos ([configuración](config.md)) |
| `public/` | archivos servidos en la raíz, como `public/logo.svg` → `/logo.svg` ([convenciones de archivos](file-conventions.md)) |
| `src/apps/` | controladores y módulos del enrutador modular ([modular](../routing/modular/README.md)) |
| `src/components/` | componentes importados por páginas; nunca enruta ([convenciones de archivo](file-conventions.md)) |
| `src/routes/` | las rutas de la aplicación ([convenciones de archivos](file-conventions.md)) |

## Próximos pasos

- [Conceptos centrales](../getting-started/core-concepts.md): el modelo al que pertenecen estas palabras
- [Índice de documentación](../README.md): la página de la tarea en cuestión
- [Convenciones de archivo](file-conventions.md): los nombres reservados detrás de estas definiciones
- [Para agentes de IA](../guides/ai-agents.md): las mismas invariantes, escritas para un agente
