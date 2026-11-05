# Rendimiento

Qué hace `nx start` de forma predeterminada, qué activar y qué se midió.

## Valores predeterminados

| Preocupación | Predeterminado | Cámbielo |
|---|---|---|
| Procesa | un Uvicorn trabajador por CPU en Linux y macOS, uno en Windows | `nx start` ejecuta la aplicación a través de Uvicorn |
| Compresión | desactivada | `useGZip = {"minimum_size": 1000}` en [Config](../reference/config.md), o comprimir en el proxy inverso |
| Archivos estáticos | servidos con `ETag` y `Last-Modified`, sin `Cache-Control` | configurar el almacenamiento en caché de larga duración en el proxy inverso o CDN para paquetes hash |
| Páginas HTML | renderizadas por solicitud, sin caché | [ISR](../rendering/isr.md) con `revalidate = N` |
| Documentos API | en | `useDocs = False` en producción |
| Nodo en tiempo de ejecución | ninguno | `nx build` pre-renderiza los componentes del cliente |

## medido

Una ejecución local, un trabajador Uvicorn, Windows, Python 3.13, conexiones de mantenimiento de actividad desde un generador de carga Python en la misma máquina. Trate las cifras como una base para comparar los cambios, no como un punto de referencia con respecto a otros marcos.

| Ruta | Simultaneidad | Solicitudes por segundo | p50 | p99 |
|---|---|---|---|---|
| Ruta JSON desnuda FastAPI | 16 | ~4500 | 3,4 ms | 5,1 ms |
| Ruta Nexy JSON (`src/routes/api/ping.py`) | 16 | ~2900 | 5,2 ms | 9,8 ms |
| Página Nexy SSR (16 KB, 16 componentes) | 1 | ~500 | 1,9 ms | 3,0 ms |
| Página Nexy SSR (16 KB, 16 componentes) | 64 | ~670 | 94 ms | 126 ms |

Leyendo la tabla:

- Las propias capas de Nexy (contexto de ruta, middleware) cuestan aproximadamente un tercio del rendimiento de una ruta simple FastAPI.
- Una página renderizada por un servidor cuesta alrededor de 2 ms de CPU, repartidos en aproximadamente 16 renderizaciones de plantillas (una por componente). Las páginas con menos componentes son proporcionalmente más baratas.
- El rendimiento aumenta con los trabajadores. En Linux, `nx start` ya inicia uno por CPU.

## Consejos prácticos

1. Coloque Nginx, Caddy o la ventaja de su plataforma al frente: TLS, HTTP/2, Brotli y el almacenamiento en caché de larga duración para `/__nexy__/client/` activos son sus puntos fuertes. Consulte [Implementar](README.md).
2. Utilice [ISR](../rendering/isr.md) para páginas que cambian menos de una vez por minuto.
3. Hidrátate lentamente con [islas](../rendering/islands.md) para que la primera carga envíe menos JavaScript.
4. Mantenga razonable el número de `.nexy` componentes por página: cada uno es una representación de plantilla independiente.
5. Mide tus propias rutas. Un generador de carga local que mantenga vivas las conexiones es suficiente para comparar dos versiones de una página.

## Próximos pasos

- [Implementar](README.md)
- [Representación](../rendering/README.md)
- [Configuración](../reference/config.md)
