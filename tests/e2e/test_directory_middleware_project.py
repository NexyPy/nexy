"""middleware.py in a real project: scoped, inherited, and never a route of its own."""

import json

from tests.e2e.project import request, scaffold, write

_MARK = """
async def middleware(request, call_next):
    response = await call_next(request)
    response.headers["x-seen"] = response.headers.get("x-seen", "") + "{name},"
    return response
"""

_GATE = """
from fastapi.responses import JSONResponse


async def middleware(request, call_next):
    if request.headers.get("authorization") != "Bearer ok":
        return JSONResponse({"detail": "login required"}, status_code=401)
    return await call_next(request)
"""


def _project(tmp_path):
    scaffold(tmp_path)
    write(tmp_path, "src/routes/middleware.py", _MARK.format(name="root"))
    write(tmp_path, "src/routes/admin/middleware.py", _GATE)
    write(tmp_path, "src/routes/admin/users/middleware.py", _MARK.format(name="users"))
    write(tmp_path, "src/routes/admin/users/index.py", "async def GET():\n    return {'ok': 1}\n")
    write(tmp_path, "src/routes/open.py", "async def GET():\n    return {'open': 1}\n")
    write(tmp_path, "src/routes/(shop)/middleware.py", _MARK.format(name="shop"))
    write(tmp_path, "src/routes/(shop)/cart.py", "async def GET():\n    return {'cart': 1}\n")


def test_directory_middleware_in_a_real_project(tmp_path):
    _project(tmp_path)
    auth = {"authorization": "Bearer ok"}

    open_, blocked, allowed, cart, as_route = request(
        tmp_path,
        ("/open", {}),
        ("/admin/users", {}),
        ("/admin/users", auth),
        ("/cart", {}),
        ("/middleware", {"accept": "application/json"}),
    )

    assert open_[0] == 200 and open_[1]["x-seen"] == "root,"
    assert blocked[0] == 401 and json.loads(blocked[2]) == {"detail": "login required"}
    assert allowed[0] == 200 and allowed[1]["x-seen"] == "users,root,"
    assert cart[0] == 200 and cart[1]["x-seen"] == "shop,root,"
    assert as_route[0] == 404
