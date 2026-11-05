# CLI

El binario es `nx` (también instalado como `nexy`). `uvx nexy new` crea un proyecto (`uvx` viene con uv). Ejecute todos los demás comandos dentro del entorno virtual del proyecto, o mediante `uv run`, por ejemplo `uv run nexy dev`: ahí es donde están sus propios paquetes.

## Comandos

| Comando | Alias | Qué hace |
|---|---|---|
| `nx dev` | `nx d` | servidor de desarrollo: compilar al cambiar, Vite, HMR |
| `nx start` | `nx s` | servidor de producción en la salida compilada |
| `nx build` | `nx b` | construcción de producción |
| `nx new` | `nx n` | estructurar un proyecto |
| `nx init` | `nx i` | agregar Nexy a un proyecto existente |
| `nx add` | - | agregue un componente de interfaz de usuario desde el registro o una URL a `src/components/ui` |
| `nx migrate` | `nx m` | crear o aplicar migraciones de bases de datos con Alembic o Aerich |
| `nx check` | `nx c` | verificación de tipo: mypy en Python, `tsc` en TypeScript |
| `nx format` | `nx f` | formato Python (ruff), JS/TS (más bonito), `.nexy` archivos |
| `nx test` | - | ejecutar pytest; `--client` agrega vitest |
| `nx skills` | - | agregar o actualizar las habilidades, `AGENTS.md` y `CLAUDE.md` para agentes de codificación |

## Banderas

| Comando | Bandera | Predeterminado |
|---|---|---|
| `dev`, `start` | `--port` | `usePort`, `3000` |
| `dev`, `start` | `--host` | `useHost`, `0.0.0.0` |
| `build` | `--check` | off - ejecuta ruff y mypy después de la compilación |
| `format` | `--check` | desactivado: informe en lugar de reescribir |
| `test` | `--client` | desactivado: también ejecute vitest en lugar de pytest solo |
| `test` | `--no-server` | activado: omita pytest cuando solo desee pruebas de cliente |
| `new` | `--template`, `-t` | ninguno - clonar una plantilla registrada sin indicaciones |
| `new` | `--no-agents` | agentes en - omitir `AGENTS.md` y las habilidades del agente |
| `add` | `--ui`, `--url` | desactivado: fuerza un nombre de registro o una URL cuando es ambiguo |
| `add` | `--all`, `-a` | desactivado: agregue todos los componentes del registro |
| `add` | `--sha256` | ninguno: resumen esperado de un componente remoto; una falta de coincidencia aborta |
| `migrate` | `--init` | desactivado: escribe la configuración Alembic o Aerich |
| `migrate` | `--upgrade`, `-u` | desactivado - aplicar las migraciones en lugar de escribir una nueva |
| `migrate` | `--message`, `-m` | vacío - nombre de la nueva revisión |

## Salida

Los pasos largos (instalar paquetes, compilar, agrupar) muestran una rueda con el tiempo transcurrido y luego dejan una línea detrás: `✔ uv sync .venv  1.4s`. Un grupo de pasos (las instalaciones de `nx new`) muestra una barra de progreso con el número de pasos finalizados, `━━━━────  2/5`; un solo paso (`nx add`) muestra una barra que pulsa mientras se ejecuta. Los registros de desarrollo leen `GET » /about 200 in 12ms` para solicitudes y `vite » ...` para Vite. Un paso fallido imprime las últimas líneas del resultado del comando en lugar de ocultarlo. Los terminales que no pueden representar Unicode obtienen `+` y `x`.

## Errores mientras se ejecuta `nx dev`

Guardar un archivo roto nunca detiene el servidor. Se informa un archivo `.py` con un error de sintaxis con su archivo y línea, y el servidor continúa entregando la última versión funcional hasta que lo solucione:

```text
  nexy » error  src/routes/users.py:3
  SyntaxError: invalid syntax

    1 | import json
    2 |
  > 3 | def GET(:
                ^
    4 |     x = 1
    5 |     return {"v": 2}

  Fix it and save: the server keeps its last working version.
```

Un archivo que se analiza pero falla cuando se carga la aplicación (una importación faltante, un error a nivel de módulo) se informa de la misma manera y `nx dev` espera su siguiente guardado; no se sirve nada hasta que la aplicación se carga nuevamente. Un guardado válido dice `nexy » update <file>` mientras el servidor se recarga. Los archivos Markdown fuera de `src/routes`, como `README.md`, no son páginas y no activan nada. `nx start` es más estricto: sale con el código 1 y no inicia nada si no se puede cargar un archivo de ruta.

## Preguntas de `nx new`

`nx new` pregunta, en este orden: enrutador basado en archivos, tipo de proyecto (web o API), enrutamiento del lado del cliente, marco del cliente, cómo diseñar la aplicación, alias de importación, ORM, base de datos y URL de la base de datos. Cada opción tiene una breve descripción y la actual está resaltada. Las preguntas que no se aplican se omiten (un proyecto API no tiene marco ni estilo; al elegir **Sin base de datos**, el ORM omite la base de datos y la URL). Moverse con las teclas de flecha (o `j`/`k`, o un número), confirmar con `enter`, volver a la pregunta anterior con `←` o `esc`, salir con `ctrl+c`.

| Pregunta | Opciones |
|---|---|
| Importe el alias | `@` (`@/components/...` apunta a `src/`), u otro prefijo como `~` o `#app` |
| Estilo | Tailwind CSS, UnoCSS, Vanilla CSS, Otro (sin herramienta CSS, la misma hoja de estilo simple que Vanilla) |
| ORM | SQLModel, SQLAlchemy, Tortoise-ORM, Sin base de datos |
| Base de datos (con un ORM) | SQLite, PostgreSQL, Neon, MySQL/MariaDB, Otros (escribes la URL) |

El controlador de base de datos para el ORM elegido se instala con él (`psycopg`, `pymysql`, `asyncpg` o `aiomysql`), y la URL se escribe en `.env`.

Antes de instalar paquetes, `nx new` verifica la conexión. Sin uno, omite las instalaciones y le indica que ejecute `uv sync` y la instalación del administrador de paquetes más tarde. Con uno, imprime la latencia y la velocidad de descarga, y avisa cuando la conexión es lenta (más de 400 ms o menos de 100 KB/s). Cada línea de instalación nombra la herramienta y la carpeta que llena, por ejemplo `pnpm install node_modules` o `uv sync .venv`.

## Qué crean `dev`, `build` y `start`

Antes de ejecutarse, los tres comandos crean un `__init__.py` vacío en `src/` y en cada carpeta debajo que contenga un archivo `.py` o `.nexy`, por lo que una ruta como `src/routes/users.py` se importa de la misma manera en todos ellos. Los archivos existentes nunca se modifican y `nx dev` vuelve a hacer lo mismo cuando agrega una carpeta. El código de bytes Python va a `__nexy__/__pycache__`, por lo que no aparece ninguna carpeta `__pycache__` junto a tus fuentes.

## Idioma

La línea de comando habla inglés, chino, hindi, español, portugués, francés, alemán, japonés, ruso, coreano, indonesio y árabe. Utiliza el primero de estos que admite:

1. la variable de entorno `NEXY_LANG` (`NEXY_LANG=ja nx dev`);
2. las variables locales de su shell (`LC_ALL`, `LC_MESSAGES`, `LANG`, luego `LANGUAGE`);
3. el idioma de su sistema operativo.

Todo lo demás es inglés, al igual que cualquier mensaje que un idioma no tenga todavía. Sólo lo que `nx` imprime se traduce: los errores del compilador, los rastreos y el resultado de las herramientas que ejecuta permanecen como están. Las traducciones aún no han sido revisadas por hablantes nativos: las correcciones son bienvenidas como solicitudes de extracción a `nexy/modules/i18n/<language>.json`.

## Comportamiento de construcción

`nx build` compila las rutas y luego agrupa el cliente cuando `useVite` está activado.

> [!NOTE]
> no hay ninguna bandera `--static`. El alojamiento estático es una opción de implementación, no un modo de compilación; consulte [Implementar](../deployment/README.md).

## Trabajando en Nexy

Dentro de este repositorio las puertas son:

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Próximos pasos

- [Comenzando](../getting-started/quick-start.md): primer proyecto
- [Pruebas](../guides/testing.md): qué `nx test` ejecuta
- [Implementar](../deployment/README.md): `build` y `start` en producción
