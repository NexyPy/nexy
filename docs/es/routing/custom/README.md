# Integración de enrutamiento personalizado

Nexy le permite incluir una aplicación FastAPI existente como enrutador en su proyecto. Esto resulta útil cuando desea reutilizar la lógica de backend de otro servicio, integrarla con API de terceros o crear una aplicación compuesta con múltiples problemas de enrutamiento.

A diferencia de los enrutadores modulares y basados ​​en archivos, que son intrínsecos a Nexy, un enrutador personalizado es simplemente un `APIRouter` que usted monta en su aplicación.

## Cuándo usar un enrutador personalizado

- **Servicios de terceros**: Tienes una aplicación FastAPI existente que deseas exponer a través del cliente de Nexy.
- **Reutilización de código**: extrae la lógica de backend de otro proyecto a un enrutador e inclúyela en uno nuevo.
- **Patrones multiinquilino o microfrontend**: Cada inquilino o módulo proporciona su propio enrutador.
- **Migración gradual**: Comience con un `APIRouter` y evolucione a un módulo Nexy completo más adelante.

## Cómo funciona

```python
from fastapi import APIRouter
from nexy import useRouter

# An existing FastAPI router (from another service)
third_party = APIRouter()
@third_party.get("/info")
async def info():
    return {"name": "Foo"}

# In your nexyconfig.py:
useRouter = third_party
```

El enrutador lo monta automáticamente el solucionador de enrutadores de Nexy. Sus rutas están disponibles bajo el mismo patrón de URL que en la aplicación original. No se necesita ninguna configuración adicional.

## Construyendo un enrutador personalizado

1. **Crear el enrutador**
   ```pitón
   desde fastapi importar APIRouter

   api = APIRouter()
   @api.get("/estado")
   estado de definición asíncrono():
       devolver {"estado": "ok"}
   ```

2. **Haz referencia a él en `nexyconfig.py`**
   ```pitón
   desde .my_backend api de importación

   usar enrutador = api
   ```

3. **Rutas de acceso**
   - Las páginas basadas en archivos (`.nexy`, `.md`) y los controladores modulares pueden hacer referencia a `/status` como lo harían con cualquier otra ruta.
   - El enrutador se ejecuta en el mismo proceso, por lo que las dependencias, las conexiones de la base de datos y la autenticación funcionan exactamente como en la aplicación original.

## Integración con otros enrutadores

Un proyecto Nexy puede combinar:

- **Enrutamiento basado en archivos** (`src/routes/`) para páginas y puntos finales simples
- **Enrutamiento modular** (`useRouter = AppModule`) para backends estructurados
- **Enrutamiento personalizado** (`useRouter = APIRouter`) para código de terceros

Los tres coexisten; cada ruta se registra sólo una vez. El enrutador basado en archivos siempre se analiza cuando existe `src/routes/`.

## Acceso CLI a la aplicación incluida

Los comandos `nexy dev` y `nx` funcionan en el enrutador montado como un enrutador integrado. Obtienes:

- Recarga en caliente para los puntos finales definidos en el enrutador personalizado (si usa `nexy` o las funciones habituales del servidor de desarrollo de FastAPI)
- Validación en `nexyconfig.py` (cualquier `APIRouter` obra)
- Documentos generados automáticamente para las rutas incluidas (si las habilitas)

## Seguridad y aislamiento

Debido a que el enrutador está incluido, no montado mediante `app.mount`, no hay una capa ASGI adicional. El enrutador reside en el mismo objeto de aplicación que sus rutas modulares y basadas en archivos. Esto significa:

- El middleware agregado por el enrutador personalizado se aplica a todas las solicitudes.
- Las protecciones y la inyección de dependencia definidas en el enrutador personalizado pueden acceder al mismo contenedor que su propio código (si usa inyección modular).
- No hay ningún prefijo de URL distinto del que define el propio enrutador.

Si necesita aislamiento, envuelva el enrutador en una subaplicación antes de incluirlo o utilice técnicas FastAPI estándar.

## Ejemplo: incluir un proyecto FastAPI existente

Supongamos que tiene `auth.py` en otro paquete:

```python
from fastapi import FastAPI, APIRouter

auth = FastAPI(title="Auth service")
api = APIRouter()

@api.get("/login")
async def login():
    return {"msg": "Login"}

auth.include_router(api)
```

En `nexyconfig.py`:

```python
from other_package.auth import api

useRouter = api
```

Ahora se puede acceder al punto final `/login` desde su sitio Nexy sin mover una línea de código.

## Cómo empezar

1. Crea tu `APIRouter` (o busca uno en un paquete existente).
2. Señala `useRouter` en `nexyconfig.py`.
3. Acceda a sus rutas a través de sus páginas, controladores o marcos de cliente.
4. Si necesita más control, convierta el enrutador personalizado en un enrutador modular usando `AppModule`.

## Próximos pasos

- [Enrutamiento basado en archivos](../fbr/README.md) – Cree páginas y controladores simples a partir de archivos.
- [Enrutamiento modular](../modular/README.md) – Backends estructurados con inyección y protecciones.
- [Manejadores de ruta](../fbr/handlers/README.md) – Definir puntos finales de Python.

El enrutador personalizado le brinda la flexibilidad de reutilizar el código FastAPI existente manteniendo la simplicidad de las páginas basadas en archivos y la estructura modular.