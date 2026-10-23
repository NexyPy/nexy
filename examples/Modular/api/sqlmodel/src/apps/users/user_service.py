
from nexy.decorators import Injectable
from sqlmodel import Session, select
from src.configs.db import engine
from .user_model import UserModel


@Injectable()
class UserService:
    def get_all(self) -> list[UserModel]:
        with Session(engine) as session:
            return session.exec(select(UserModel)).all()

    def create(self, name: str, email: str) -> UserModel:
        user = UserModel(name=name, email=email)
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
