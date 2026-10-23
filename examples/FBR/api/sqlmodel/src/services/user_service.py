
from sqlmodel import Session, select
from src.configs.db import engine
from src.models.user_model import UserModel


class UserService:
    @staticmethod
    def get_all() -> list[UserModel]:
        with Session(engine) as session:
            return session.exec(select(UserModel)).all()

    @staticmethod
    def create(name: str, email: str) -> UserModel:
        user = UserModel(name=name, email=email)
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
