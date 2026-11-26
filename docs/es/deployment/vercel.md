# ¿Cómo implemento una aplicación Nexy en Vercel?

Ejecute `nx add vercel`, confirme los archivos generados junto con su salida `nx build` y apunte el tiempo de ejecución de Vercel Python a `src/server.py:app`.

## Agregar los archivos de la plataforma

Desde la raíz de un proyecto Nexy:

```bash
nx add vercel
nx build
```

`nx add vercel` escribe `src/server.py` y `vercel.json`. También agrega reglas de ignorar para los archivos que cambian mientras se ejecuta la aplicación: `__nexy__/build-cache.json`, `__nexy__/server.port`, `__nexy__/.temp/` y `__pycache__/`. Al ejecutar el comando nuevamente se mantienen los archivos que ya existen y no se duplican las reglas de ignorar.

## Punto Vercel en la aplicación

En la configuración del proyecto Vercel, seleccione el tiempo de ejecución Python y use `src/server.py:app` como punto de entrada. Vercel descubre el nombre `app` en ese módulo; `nx start` no está involucrado.

El `src/server.py` generado importa el `nexy.app.app` diferido después de haber preparado la carpeta de trabajo. Puede utilizar el mismo punto de entrada con `uvicorn src.server:app` localmente.

## Confirmar el resultado de la compilación

Cuando Vercel no tiene un comando de compilación, recibe solo lo que contiene el repositorio. Confirme `__nexy__/` después de cada `nx build`, con las rutas compiladas, el paquete de cliente en `__nexy__/client/` y el manifiesto en `__nexy__/client/.vite/manifest.json`.

Mantenga `vite.config.ts` en la raíz del proyecto y confírmelo. En producción, Nexy lee el manifiesto Vite para escribir la hoja de estilo y las etiquetas del script, pero emite esas etiquetas solo cuando `vite.config.ts` existe. Sin ese archivo la página todavía responde 200 y llega sin CSS ni cliente JavaScript.

No confirme `__nexy__/build-cache.json`: contiene rutas absolutas de la máquina que ejecutó la compilación. `__nexy__/server.port` pertenece a `nx start` y `__nexy__/.temp/` es espacio temporal.

## Aceptar un sistema de archivos de solo lectura

Vercel monta el proyecto en modo de solo lectura mientras se inicia una aplicación Python. Nexy escribe los archivos generados durante el inicio, por lo que un simple `from nexy.app import app` puede fallar con `OSError: [Errno 30] Read-only file system`.

El punto de entrada generado copia seis elementos del proyecto en una carpeta temporal grabable antes de importar la aplicación: `src`, `__nexy__`, `public`, `nexyconfig.py`, `pyproject.toml` y `vite.config.ts`. Cambia el directorio de trabajo y coloca la copia primero en `sys.path`, porque Nexy resuelve las rutas desde el directorio actual. Agregue manualmente cualquier otro archivo que su aplicación lea en tiempo de ejecución a esa lista.

## Caché de activos estáticos

El `vercel.json` generado contiene las dos reglas de caché que utiliza un sitio Nexy implementado: los archivos en `/assets/` son inmutables durante un año, y las imágenes y fuentes en `public/` se mantienen actualizadas durante un día con una ventana de una semana de obsolescencia mientras se revalida. Agregue otras reglas en el mismo archivo si su proyecto las necesita.

## Verifique el despliegue

Antes de presionar, importe el punto de entrada y solicítele una página:

```bash
uv run python -c "from src.server import app; print(type(app).__name__)"
uv run uvicorn src.server:app
```

Luego abra `/`, una ruta generada y un archivo en `/assets/`. Compare la respuesta con `nx start` localmente: el estado, el tipo de contenido y el tamaño deben coincidir. Una página que es más pequeña que la local exactamente por las dos etiquetas de cliente significa que faltaba `vite.config.ts` en el proyecto copiado.
