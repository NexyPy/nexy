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

## Limitación de velocidad

`useRateLimit` responde `429 Too Many Requests` a una dirección de cliente que envía más de `requests` solicitudes en una ventana de `per` segundos.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy garantiza que una solicitud que supere el límite recibirá un `429` con un encabezado `Retry-After`, los segundos que quedan en la ventana, y nunca llegará a sus rutas, acciones o middleware.

Nexy garantiza que sin `useRateLimit` no se agrega middleware con límite de velocidad.

Nexy garantiza que las sondas `useHealth` nunca serán limitadas.

`paths` es opcional: sin él, cada camino es limitado. Las acciones del servidor se sirven bajo `/_nx_`, por lo que el prefijo las limita a todas.

La ventana es fija y compartida por todos los clientes: los conteos comienzan nuevamente en cada múltiplo de `per` segundos. Por lo tanto, un cliente puede enviar hasta dos veces `requests` a lo largo del borde de una ventana.

Los conteos viven en la memoria de cada trabajador. Con `useWorkers` encima de uno, un cliente puede enviar `requests` a cada trabajador y los recuentos comienzan de nuevo cuando se reinicia el servidor.

La dirección del cliente es la que uvicorn proporciona la solicitud. Detrás de un proxy inverso en la misma máquina, uvicorn lo lee desde `X-Forwarded-For`; para un proxy en otra máquina, indique su dirección en la variable de entorno `FORWARDED_ALLOW_IPS`, o cada cliente comparte la dirección del proxy.

Tu aplicación es responsable de un límite compartido por varios trabajadores o servidores: un proxy inverso o una tienda como Redis.

## HTTPS

Sirva HTTPS directamente con `useSslKeyfile` y `useSslCertfile`, o finalice TLS en un proxy inverso y configure `useHTTPSRedirect`. En desarrollo, el servidor de desarrollo Vite permanece en bucle invertido HTTP detrás del origen Nexy, por lo que TLS nunca lo alcanza.

## Lista de verificación de producción

- `useDocs = False` si el esquema OpenAPI no debe ser público.
- `useTrustedHost` configurado en tus dominios, para bloquear ataques al encabezado del host.
- `useCORS` con orígenes explícitos, nunca `["*"]` junto con credenciales.
- Un auténtico `secret_key` para sesiones, leído desde el entorno.
- Nexy escapa HTML de los Props pasados ​​a los componentes del cliente. No marque la entrada del usuario `| safe` en las plantillas.

## Guardias y dependencias

La protección por ruta utiliza FastAPI dependencias. Un `dependencies.py` en un directorio de rutas se aplica a todo lo que se encuentra debajo de él: consulte [Dependencias](../routing/fbr/dependencies/README.md). En el enrutador modular utilice [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Próximos pasos

- [Configuración](../reference/config.md): cada campo de middleware
- [Implementar](../deployment/README.md)
- [Rendimiento](../deployment/performance.md)
