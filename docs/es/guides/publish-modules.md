# ¿Cómo publico un módulo en el registro de Nexy?

Ejecute `nx publish` desde un directorio de módulo con un `nx.toml` válido, un token de registro y todos los archivos que declara el manifiesto; el comando verifica la versión, crea un archivo y carga una versión inmutable.

## preparar el manifiesto

Un módulo fuente enumera cada archivo que envía. El archivo contiene `nx.toml` y exactamente esos archivos.

```toml filename="nx.toml"
name = "@acme/auth"
version = "1.2.0"
kind = "source"

[compatibility]
nexy = ">=2.0.0"
python = ">=3.12"

[dependencies]
python = []
node = []

[source]
files = ["src/auth.py", "src/helpers.py"]
```

El campo `name` debe estar en minúscula `@scope/name`. El campo `version` debe tener tres números separados por puntos. Los archivos deben ser rutas relativas dentro del módulo. Un módulo de paquete declara `source.package` en lugar de `source.files`.

## Compruébalo antes de subir

Utilice `--dry-run` para validar el manifiesto, archivar los archivos declarados e imprimir la suma de verificación sin cargar:

```bash
nx publish --dry-run
```

Un ensayo no necesita token. Imprime una línea `warning:` para cada importación relativa que apunta a un archivo que el manifiesto no declara. Por ejemplo, `from .helpers import token` en `src/auth.py` necesita `src/helpers.py` en `source.files`; de lo contrario, una instalación obtendría una importación interrumpida.

## Establecer la ficha

`nx publish` lee `NEXY_REGISTRY_TOKEN`, luego `~/.config/nexy/registry-token`. El token se envía en el encabezado `Authorization` y nunca se imprime.

```bash
export NEXY_REGISTRY_TOKEN="your-token"
nx publish
```

El archivo token permite que un futuro `nx login` escriba la misma credencial. Sin ninguna fuente, el comando imprime `error: No registry token` y sale con el estado 1.

## Publicar

```bash
nx publish
```

El comando imprime el nombre, la versión y la suma de comprobación SHA-256 de la versión que publicó. Un par de nombre y versión es inmutable: publicarlo nuevamente genera un error de conflicto. En su lugar, publique una nueva versión.

## Utilice otro registro

De forma predeterminada, el comando se envía a `https://registry.nexypy.dev`. Utilice `--registry` para otro registro, por ejemplo uno local durante el desarrollo:

```bash
nx publish --registry http://localhost:8000
```

Solo se aceptan URL https, además de http simple en `localhost`, `127.0.0.1` y `::1`. Las respuestas transitorias `429` y `5xx` se reintentan dos veces; un manifiesto incorrecto, un token faltante o un conflicto no se reintenta.

## Verificar la liberación

```bash
nx add @acme/auth@1.2.0
```

Consulte [Instalar módulos](install-modules.md) para obtener actualizaciones, pines y configuraciones de confianza.
