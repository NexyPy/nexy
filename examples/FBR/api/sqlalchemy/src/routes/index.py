
from src.services.user_service import UserService


def GET():
    return UserService.get_all()
