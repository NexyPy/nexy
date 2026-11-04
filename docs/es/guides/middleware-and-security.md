# Middleware y seguridad

Nexy se ejecuta en FastAPI y Starlette, por lo que se aplica su middleware. Los comunes son una línea en
`nexyconfig.py`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

Cada diccionario `use*` se pasa como argumentos de palabras clave al middleware Starlette correspondiente:
`CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Tu propio middleware

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` toma clases de middleware ASGI.

## HTTPS

Sirve HTTPS directamente con `useSslKeyfile` y `useSslCertfile`, o finaliza TLS en un proxy inverso
y establezca `useHTTPSRedirect`. En desarrollo, el servidor de desarrollo de Vite permanece en bucle invertido HTTP detrás del
Origen Nexy, por lo que TLS nunca llega a él.

## Lista de verificación de producción

- `useDocs = False` si el esquema OpenAPI no debe ser público.
- `useTrustedHost` configurado en tus dominios, para bloquear ataques al encabezado del host.
- `useCORS` con orígenes explícitos, nunca `["*"]` junto con credenciales.
- Un verdadero `secret_key` para sesiones, leído desde el entorno.
- Nexy escapa en formato HTML a los accesorios pasados ​​a los componentes del cliente. No marcar la entrada del usuario `| safe` en
  plantillas.

## Guardias y dependencias

La protección por ruta utiliza dependencias FastAPI. Un `dependencies.py` en un directorio de rutas se aplica a
todo lo que hay debajo: consulte [Dependencias](../routing/fbr/dependencies/README.md). En el uso del enrutador modular.
[`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Próximos pasos

- [Config](../reference/config.md): cada campo de middleware
- [Implementar](../deployment/README.md)
- [Rendimiento](../deployment/performance.md)