# Seguridad

Cómo Nexy mantiene pequeña su propia superficie de ataque, qué versiones requiere y cómo verificar un proyecto.

## Versión pisos

Nexy depende de FastAPI, Starlette, Jinja2, Vite y React. Un piso es la versión más baja que permite Nexy; cada uno responde a un aviso publicado.

| Paquete | piso | ¿Por qué? |
|---|---|---|
| `starlette` | 1.3.1 | CVE-2026-48710 (BadHost, corregido en 1.0.1): un encabezado `Host` modificado cambia la ruta Starlette informa al middleware, lo que omite la autorización escrita en `request.url.path`; catalogado como explotado por CISA. CVE-2026-48817 y CVE-2026-48818 (despacho de solicitudes, `StaticFiles` en Windows, corregido en 1.1.0), CVE-2026-54282 (ruta de solicitud no validada, 1.3.0) y CVE-2026-54283 (límites de `request.form()`, 1.3.1). |
| `python-dotenv` | 1.2.2 | CVE-2026-28684, en el lector del `.env` se carga el archivo `nx migrate` |
| `fastapi` | 0.133.0 | la primera versión que acepta un Starlette fijo |
| `jinja2` | 3.1.6 | escape del sandbox a través del filtro `attr` (CVE-2025-27516) |
| `vite` (proyectos estructurados) | 6.4.5 | `server.fs.deny` omisiones (CVE-2026-53571 en rutas alternativas de Windows; GHSA-rq7h-c2jc-7f22, corregido en 6.4.4; GHSA-8g5g-mxqh-grgj, una omisión de consulta incorporada en 6.4.4, corregida en 6.4.5), y los avisos `launch-editor` corregidos en 6.4.4 |
| `svelte` (proyectos estructurados) | 5.55.7 | seis avisos XSS de procesamiento de servidor a través de atributos de extensión, nombres de etiquetas dinámicas y `bind:innerText` |
| `esbuild` (proyectos estructurados) | 0.28.1 | archivo arbitrario leído a través del servidor de desarrollo (GHSA-g7r4-m6w7-qqqr) |
| `react`, `react-dom` | 19.2.5 | los avisos de 2026 React se refieren a los paquetes `react-server-dom-*`, que Nexy no utiliza; el piso mantiene la línea parchada |

`python scripts/audit_dependencies.py` verifica cada piso con OSV después del bloqueo, también en CI: un nuevo aviso en un piso no pasa la auditoría.

Comprueba tus versiones resueltas:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Reglas que sigue Nexy

- **Nunca confíes en el encabezado del Host para las rutas.** Nexy lee `scope["path"]`, no `request.url.path`, en su propio middleware (middleware de directorio). Haz lo mismo en el tuyo.
- **Escape de lo que llega a HTML.** Props pasados ​​a los componentes del cliente, `Link` atributos, `Image`, `Audio` y `Video` atributos, anclajes de tabla de contenido y `HTTPException` detalles están todos escapados de HTML. Una plantilla `.nexy` no escapa por sí sola: escriba `{{ value | e }}` para cualquier valor que provenga de un visitante o de la base de datos, y nunca `| safe` en la entrada del usuario.
- **Los puntos finales de desarrollador son de bucle invertido y estrechos.** El punto final de procesamiento de desarrollo (`/__nexy__/render`) solo acepta archivos bajo `src/routes/` con una extensión `.tsx` o `.jsx`, y solo se puede acceder a él a través del servidor de desarrollo, que rechaza encabezados `Host` externos.
- **Los detalles del error no se filtran.** Una página de error que falla muestra solo el código de estado.
- **Las respuestas de producción llevan encabezados seguros.** `X-Content-Type-Options: nosniff` y `Referrer-Policy: strict-origin-when-cross-origin`, a menos que su código establezca el suyo propio. El encabezado `Server` no se envía. Agrega `Strict-Transport-Security` y un `Content-Security-Policy` en tu proxy o un middleware: dependen de tu dominio.
- **Un bloqueo muestra una referencia, no el error.** Consulte [Páginas de error](../routing/fbr/errors/README.md#unhandled-exceptions).
- **No `eval` ni `shell=True` en el código Python de Nexy.** Los programas externos se ejecutan con una lista de argumentos.

## Ejecución de las auditorías

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

El propio repositorio de Nexy ejecuta el primero y el tercero en sus comprobaciones. Un nuevo aviso en un piso de arriba se maneja elevando el piso en `pyproject.toml` o en el andamio `package.json`, luego regenerando la cerradura.

## Implementación segura

- Establezca `useTrustedHost` en sus dominios: rechaza encabezados `Host` inesperados antes de cualquier ruta.
- No exponga el servidor de desarrollo Vite: `nx dev` lo mantiene en bucle detrás del origen Nexy.
- Establezca `useDocs = False` si el esquema de API no debe ser público.

Consulte [Middleware y seguridad](../guides/middleware-and-security.md).

## Fuentes

- [CVE-2026-48710 (BadHost) en Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite aviso GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) y [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React paquetes de servidor CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## Próximos pasos

- [Middleware y seguridad](../guides/middleware-and-security.md)
- [Implementar](../deployment/README.md)
- [Configuración](config.md)
