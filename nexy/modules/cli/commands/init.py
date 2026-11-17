import sys

import typer
from rich.markup import escape

from nexy.helpers.common.messages import error
from nexy.modules.cli.init import AlreadyInitializedError, InitProject
from nexy.modules.i18n import t


def init() -> None:
    try:
        InitProject().run()
    except AlreadyInitializedError:
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        print()
        sys.exit(130)
    except Exception as failure:
        cause = escape(str(failure)) or type(failure).__name__
        error(t("cli.init.failed", "Could not initialize the project"), cause=cause)
        raise typer.Exit(code=1) from None
