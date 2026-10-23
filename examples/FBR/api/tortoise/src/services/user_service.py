
from src.models.user_model import UserModel


class UserService:
    @staticmethod
    async def get_all() -> list[UserModel]:
        return await UserModel.all()

    @staticmethod
    async def create(name: str, email: str) -> UserModel:
        return await UserModel.create(name=name, email=email)
