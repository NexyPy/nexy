
from src.services.user_service import UserService


async def GET():
    return await UserService.get_all()
