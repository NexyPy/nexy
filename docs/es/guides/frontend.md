# Interfaz

Nexy no envía su propio sistema de componentes para el cliente. Se basa en Vite: React, Vue, Svelte, Solid y Preact son ​​compatibles, y las páginas básicas funcionan sin ningún marco de cliente.

## Habilitar un marco

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()   # vue(), svelte(), solid(), preact()
```

`useVite` por defecto es `True`; manténgalo encendido cuando se configure un marco.

## Archivos de ruta

| Extensión | Representada |
|---|---|
| `.nexy`, `.md` | por Nexy en el momento de la solicitud |
| `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte` | por el marco del cliente; pre-renderizado a HTML en el momento de la compilación, luego asumido por el paquete del cliente |

Una ruta de marco es una página normal, no una isla exclusiva de cliente: el HTML existe antes de que se ejecute el paquete, por lo que la primera pintura no espera a JavaScript.

Configuración por marco: [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md).

## Desarrollo

`nx dev` inicia un servidor en un puerto:

1. la aplicación recompila las rutas que cambias, servidor y cliente;
2. Vite se ejecuta en un puerto interno y sirve módulos de marco;
3. Nexy representa los puntos finales de Vite a través de su propio origen.

El navegador sólo habla con el puerto `3000`. No hay una segunda URL para abrir ni CORS para configurar.

## construir

`nx build` produce:

- HTML prerenderizado para rutas de marco;
- el paquete de clientes, con activos bajo `__nexy__/client/`;
- las rutas compiladas Python.

Vite maneja el paquete del cliente; SSR HTML se produce por archivo mediante esbuild.

> [!NOTA]
> una ruta cuyo procesamiento del servidor falla se informa como una ruta solo para el cliente en lugar de fallar en toda la compilación.

## Estilo

`nexy new` solicita un modo de estilo y lo configura para el marco de trabajo del cliente que elijas: Tailwind, UnoCSS o CSS simple. Los tokens de diseño (colores, fuentes, el tema oscuro) son variables CSS en `src/globale.css`, el archivo que crea el andamio.

| Modo | Las páginas de inicio se escriben con |
|---|---|
| Tailwind, UnoCSS | clases de utilidad en el marcado, con los tokens asignados a nombres de clases |
| Nombres de clases semánticas de CSS simple | y CSS en `src/globale.css` |

Siga el modo de su proyecto cuando agregue una página: clases de utilidad en un proyecto de utilidad, CSS en uno de CSS simple. Mantenga el CSS del componente que las utilidades no puedan expresar en el bloque `<style>` del componente. En un proyecto de servidor (`.nexy` páginas) UnoCSS lee los `.nexy` archivos para las clases; Tailwind los encuentra por sí solo.

## Fuentes, imágenes, guiones.

Coloque los archivos estáticos en `public/`; se sirven desde `/` tanto en desarrollo como en producción.

## Próximos pasos

- [Vistas](../views/README.md): elige un formato de página
- [Configuración](../reference/config.md): `useFF`, `useVite`, alias
- [Implementar](../deployment/README.md): lo que produce la compilación
