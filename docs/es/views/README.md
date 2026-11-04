# Vistas

Antes de elegir un formato de archivo, es importante distinguir entre cómo Nexy maneja los recursos y cómo los representa.

| Término | Definición |
|---|---|
| **Página** | Un recurso direccionable por URL de la aplicación. Está definido por un archivo en `src/routes/`. |
| **Ver** | El proceso de producir el cuerpo de respuesta para una página. Una vista transforma la lógica y los datos en HTML o JSON. |
| **Componente** | Un bloque de construcción de interfaz de usuario reutilizable que se utiliza para componer una vista. Los componentes pueden ser ayudantes nativos de Nexy o específicos del marco (React, Vue, etc.). |
| **Manejador de ruta** | Una función de Python que maneja una solicitud HTTP para un método específico (por ejemplo, `GET`, `POST`). |
| **Punto final** | La combinación única de una URL y un método HTTP que responde un controlador de ruta. |

**¿No estás seguro? Escribe un archivo `.nexy`.** No necesita un marco de cliente, y puedes agregar un componente React, Vue, Svelte, Solid o Preact dentro de él más tarde, como una isla.

```diagram filename="¿Qué archivo para qué página?"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## Formatos

| Formato | Archivo | Representación del servidor | Marco del cliente | Notas |
|---|---|---|---|---|
| `.nexy` | [archivos .nexy](nexy/README.md) | Lógica Jinja2 + Python, transmitida | opcional | Formato de página Nexy nativo |
| `.md` | [Markdown y MDX](nexy/markdown.md) | cmargfm en el momento de la solicitud | opcional mediante diseño | Markdown puro, GFM, envuelto en diseño |
| `.mdx` | [Markdown y MDX](nexy/markdown.md) | framework SSR | React o Preact | Markdown con componentes |
| `.tsx` | [React](react/differences.md), [Solid](solid/differences.md) o [Preact](preact/differences.md) | modo cliente: el marco, renderizado en Node | React, Solid o Preact | Rutas de componentes |
| `.vue` | [Vue](vue/differences.md) | modo cliente: el framework, renderizado en Node | Vue | rutas SFC |
| `.svelte` | [Svelte](svelte/differences.md) | modo cliente: el marco, renderizado en Node | Svelte | Rutas SFC |

Ayudantes `Image`, `Link`, `Audio`, `Video` y `Import` integrados: [Componentes](nexy/components.md).

## Mezcla de formatos

Puedes mezclar diferentes tecnologías dentro de un mismo proyecto:
- **Islas**: Puedes importar un componente React o Vue dentro de una `.nexy` página. El servidor representa el shell y el marco hidrata el componente en el cliente.
- **Lógica compartida**: Los controladores de ruta en archivos `.py` pueden proporcionar datos a páginas en cualquier formato a través del estado de la aplicación compartida o llamadas API.

## Habilitar un marco

Establezca `useFF` en `nexyconfig.py` y ejecute `nexy new` para agregar dependencias:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

Con un marco habilitado, Vite maneja sus paquetes de clientes. En modo cliente sus extensiones se vuelven
rutas; en modo servidor, los mismos archivos son componentes que usted importa como islas: un archivo de marco en
`src/routes/` se rechaza allí. Consulte [modo servidor y modo cliente](../routing/fbr/modes.md).

> [!NOTA]
> en modo [CSR](../rendering/csr.md), solo los archivos de ruta del marco son navegables
> del lado del cliente.

## Diseños

Un `layout.*` en un directorio envuelve las páginas debajo de él. Ver [diseños](../routing/fbr/layouts/README.md).

## Próximos pasos

- [archivos .nexy](nexy/README.md): Python + Jinja2 + accesorios
- [Markdown y MDX](nexy/markdown.md): páginas de contenido
- [Componentes](nexy/components.md): asistentes HTML integrados