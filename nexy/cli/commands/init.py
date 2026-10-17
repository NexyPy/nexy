import sys

import typer

from nexy.utils.init import AlreadyInitializedError, InitProject


def init() -> None:
    try:
        InitProject().run()
    except AlreadyInitializedError:
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        print()
        sys.exit(130)
