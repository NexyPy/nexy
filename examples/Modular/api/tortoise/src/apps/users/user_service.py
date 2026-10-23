
from nexy.decorators import Injectable
from .user_model import UserModel


@Injectable()
class UserService:
    async def get_all(self) -> list[UserModel]:
        return await UserModel.all()

    async def create(self, name: str, email: str) -> UserModel:
        return await UserModel.create(name=name, email=email)
