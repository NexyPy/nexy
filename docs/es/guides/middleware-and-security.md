# Middleware y seguridad

Nexy se ejecuta en FastAPI y Starlette, por lo que se aplica su middleware. Los más comunes son una línea en `nexyconfig.py`.

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

Cada diccionario `use*` se pasa como argumentos de palabras clave al middleware Starlette coincidente: `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Tu propio middleware

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` toma clases de middleware ASGI.

## HTTPS

Sirva HTTPS directamente con `useSslKeyfile` y `useSslCertfile`, o finalice TLS en un proxy inverso y configure `useHTTPSRedirect`. En desarrollo, el servidor de desarrollo Vite permanece en bucle invertido HTTP detrás del origen Nexy, por lo que TLS nunca lo alcanza.

## Lista de verificación de producción

- `useDocs = False` si el esquema OpenAPI no debe ser público.
- `useTrustedHost` configurado en tus dominios, para bloquear ataques al encabezado del host.
- `useCORS` con orígenes explícitos, nunca `["*"]` junto con credenciales.
- Un auténtico `secret_key` para sesiones, leído desde el entorno.
- Nexy escapa de HTML a los accesorios pasados ​​a los componentes del cliente. No marque la entrada del usuario `| safe` en las plantillas.

## Guardias y dependencias

La protección por ruta utiliza FastAPI dependencias. Un `dependencies.py` en un directorio de rutas se aplica a todo lo que se encuentra debajo de él: consulte [Dependencias](../routing/fbr/dependencies/README.md). En el enrutador modular utilice [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Próximos pasos

- [Configuración](../reference/config.md): cada campo de middleware
- [Implementar](../deployment/README.md)
- [Rendimiento](../deployment/performance.md)
