from nexy.http import FileResponse, HTTPException
from src.content import ASSETS


async def GET(name: str) -> FileResponse:
    """The stylesheet, the script and the icon, shared with the vanilla site."""
    target = (ASSETS / name).resolve()
    if not target.is_relative_to(ASSETS.resolve()) or not target.is_file():
        raise HTTPException(status_code=404, detail="No such file")
    return FileResponse(target)
