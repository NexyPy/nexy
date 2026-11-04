# Seguridad

Cómo Nexy mantiene pequeña su propia superficie de ataque, qué versiones requiere y cómo verificar un proyecto.

## Versión pisos

Nexy depende de FastAPI, Starlette, Jinja2, Vite y React. Un piso es la versión más baja de Nexy.
permite; cada uno responde a un aviso publicado.

| Paquete | Piso | Por qué |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost): un encabezado `Host` diseñado cambia la ruta que Starlette informa al middleware, lo que omite la autorización escrita en `request.url.path`. Catalogado como explotado por CISA. |
| `fastapi` | 0.133.0 | la primera versión que acepta un Starlette fijo |
| `jinja2` | 3.1.6 | escape del sandbox a través del filtro `attr` (CVE-2025-27516) |
| `vite` (proyectos con scaffolding) | 6.4.3 | `server.fs.deny` omisión de rutas alternativas de Windows (CVE-2026-53571); la anterior omisión de cadena de consulta (CVE-2026-39364) afecta solo a Vite 7.1-7.3.1 y 8.0.0-8.0.4 |
| `react`, `react-dom` | 19.2.5 | los avisos de React 2026 se refieren a los paquetes `react-server-dom-*`, que Nexy no utiliza; el piso mantiene la línea parchada |

Comprueba tus versiones resueltas:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Reglas que sigue Nexy

- **Nunca confíes en el encabezado del Host para las rutas.** Nexy lee `scope["path"]`, no `request.url.path`, en
  su propio middleware (middleware de directorio). Haz lo mismo en el tuyo.
- **Escape de lo que llega a HTML.** Accesorios pasados a componentes del cliente, `Link` atributos, `Image`,
  Los atributos `Audio` y `Video`, los anclajes de la tabla de contenido y los detalles `HTTPException` son todos
  Escapado HTML. `| safe` en una plantilla desactiva esto: nunca lo uses en la entrada del usuario.
- **Los puntos finales del desarrollador son de bucle invertido y estrechos.** El punto final de procesamiento del desarrollador
  (`/__nexy__/render`) solo acepta archivos bajo `src/routes/` con una extensión `.tsx` o `.jsx`, y
  solo se puede acceder a través del servidor de desarrollo, que rechaza encabezados `Host` externos.
- **Los detalles del error no se filtran.** Una página de error que falla muestra solo el código de estado.
- **Las respuestas de producción llevan encabezados seguros.** `X-Content-Type-Options: nosniff` y
  `Referrer-Policy: strict-origin-when-cross-origin`, a menos que tu código establezca el suyo propio. El `Server`
  El encabezado no se envía. Añade `Strict-Transport-Security` y un `Content-Security-Policy` en tu
  proxy o un middleware: dependen de tu dominio.
- **Un bloqueo muestra una referencia, no el error.** Consulte [Páginas de error](../routing/fbr/errors/README.md#unhandled-exceptions).
- **No `eval` ni `shell=True` en el código Python de Nexy.** Los programas externos se ejecutan con una lista de argumentos.

## Ejecución de las auditorías

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

El propio repositorio de Nexy ejecuta el primero y el tercero en sus comprobaciones. Un nuevo aviso en un piso superior se maneja elevando el
piso en `pyproject.toml` o en el andamio `package.json`, regenerando luego la cerradura.

## Implementación segura

- Establece `useTrustedHost` en tus dominios: rechaza encabezados `Host` inesperados antes de cualquier ruta.
- No exponer el servidor de desarrollo de Vite: `nx dev` lo mantiene en bucle detrás del origen Nexy.
- Establezca `useDocs = False` si el esquema de API no debe ser público.

Consulte [Middleware y seguridad](../guides/middleware-and-security.md).

## Fuentes

- [CVE-2026-48710 (BadHost) en Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Aviso Vite GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) y
  [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [Paquetes de servidor React CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## Próximos pasos

- [Middleware y seguridad](../guides/middleware-and-security.md)
- [Implementar](../deployment/README.md)
- [Configuración](config.md)