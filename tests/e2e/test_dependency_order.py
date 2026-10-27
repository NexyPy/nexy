"""dependencies.py inherit from the routes root down, like layouts; handler guards run last."""

import json

from tests.e2e.project import request, scaffold, write

_DEPENDENCY = """
from src.log import CALLS


def {name}() -> None:
    CALLS.append("{name}")


dependencies = [{name}]
"""


def test_directory_dependencies_run_root_first_then_the_handler(tmp_path):
    scaffold(tmp_path)
    write(tmp_path, "src/log.py", "CALLS: list[str] = []\n")
    write(tmp_path, "src/routes/dependencies.py", _DEPENDENCY.format(name="root"))
    write(tmp_path, "src/routes/admin/dependencies.py", _DEPENDENCY.format(name="admin"))
    write(tmp_path, "src/routes/admin/users/dependencies.py", _DEPENDENCY.format(name="users"))
    write(
        tmp_path,
        "src/routes/admin/users/index.py",
        """
from nexy.decorators import Middleware, UseGuard
from src.log import CALLS


def guard() -> None:
    CALLS.append("guard")


def middleware() -> None:
    CALLS.append("middleware")


@UseGuard(guard)
@Middleware(middleware)
async def GET():
    CALLS.append("handler")
    return {"calls": list(CALLS)}
""",
    )

    ((status, _headers, body),) = request(tmp_path, ("/admin/users", {}))

    assert status == 200
    assert json.loads(body)["calls"] == [
        "root",
        "admin",
        "users",
        "guard",
        "middleware",
        "handler",
    ]


def test_a_route_group_directory_takes_part(tmp_path):
    scaffold(tmp_path)
    write(tmp_path, "src/log.py", "CALLS: list[str] = []\n")
    write(tmp_path, "src/routes/(shop)/dependencies.py", _DEPENDENCY.format(name="shop"))
    write(
        tmp_path,
        "src/routes/(shop)/cart.py",
        "from src.log import CALLS\n\n\nasync def GET():\n    return {'calls': list(CALLS)}\n",
    )

    ((status, _headers, body),) = request(tmp_path, ("/cart", {}))

    assert status == 200
    assert json.loads(body)["calls"] == ["shop"]
