# ¿Cómo instalo un módulo desde el registro?

Ejecute `nx add @scope/name` en un proyecto Nexy para descargar una versión del registro del módulo, verificarla y aplicar los cambios declarados. Agregue `@1.2.0` para fijar una versión exacta.

## Instalar un módulo

Desde la raíz de un proyecto Nexy:

```bash
nx add @acme/auth
nx add @acme/auth@1.2.0
```

`nx add` lee los metadatos de la versión y el archivo de `useModuleRegistry`, verifica la suma de verificación SHA-256 y verifica los rangos de compatibilidad del módulo `nexy` y `python`. Luego escribe solo los archivos que declara el manifiesto, agrega los paquetes Python declarados con `uv add`, agrega paquetes de Nodo con el administrador de paquetes del proyecto y aplica los enlaces de configuración a `nexyconfig.py` y `package.json`. Las configuraciones y archivos existentes permanecen como están: un archivo declarado que ya existe se omite con una línea `warning:`.

Cada instalación exitosa se registra en `.nexy/modules.json`. Confirme ese archivo para que un compañero de equipo obtenga la misma versión del módulo.

## Actualizar un módulo

Para actualizar, ejecute `nx add @acme/auth` nuevamente después de que el registro tenga una versión más reciente, o establezca un nuevo pin como `@acme/auth@1.3.0`. Un nombre no fijado selecciona la versión más reciente de la respuesta `/versions` del registro. Ejecutar la misma versión nuevamente imprime `is already installed` y no cambia nada.

## Anclar una versión

Un pin es exacto: `nx add @acme/auth@1.2.0` instala `1.2.0` y ninguna otra versión. Utilice un pin en CI y en un `.nexy/modules.json` comprometido para que cada pago instale el mismo código. Sin un pin, una nueva versión cambia la siguiente instalación.

## Ejecutar migraciones

Las migraciones están desactivadas de forma predeterminada. Agregue `--migrate` cuando desee que los comandos declarados de una versión se ejecuten después de que sus archivos y dependencias estén en su lugar:

```bash
nx add @acme/auth@1.2.0 --migrate
```

Cada comando se imprime antes de ejecutarse. El proyecto necesita tener instalada su herramienta de migración antes de que un módulo pueda declarar una.

## Establecer el registro y sus reglas de confianza.

Los valores predeterminados se encuentran en `nexyconfig.py`:

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useModuleRegistry = "https://registry.nexypy.dev"
    useRequireSignedModules = False
```

`useModuleRegistry` es la URL base que lee la CLI. Sólo se aceptan URL https, excepto http de bucle invertido para un registro local durante el desarrollo. `useRequireSignedModules = True` rechaza una autorización sin firmar. Una autorización que lleva una firma también se rechaza hasta que esté disponible un verificador; una vez que uno lo verifica, `nx add` imprime `Verified by` con la identidad del firmante. Mantenga el `False` predeterminado solo para los registros en los que confíe.
