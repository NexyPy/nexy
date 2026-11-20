"""Every read of the products. The actions of `src/actions/shop.py` call nothing else."""

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from src.configs.db import engine
from src.models.product_model import ProductModel


def containing(text: str) -> str:
    """A LIKE pattern that finds `text` as it is written: `%` and `_` match themselves."""
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def shelf(category: str, text: str) -> Select[tuple[ProductModel]]:
    query = select(ProductModel).order_by(ProductModel.id)
    if category:
        query = query.where(ProductModel.category == category)
    if text:
        pattern = containing(text)
        query = query.where(
            or_(
                ProductModel.name.ilike(pattern, escape="\\"),
                ProductModel.summary.ilike(pattern, escape="\\"),
            )
        )
    return query


class CatalogService:
    @staticmethod
    def browse(category: str = "", text: str = "") -> list[ProductModel]:
        """The products of `category` whose name or summary holds `text`, in shelf order."""
        with Session(engine) as session:
            return list(session.scalars(shelf(category, text.strip())))

    @staticmethod
    def find(slug: str) -> ProductModel | None:
        with Session(engine) as session:
            return session.scalar(select(ProductModel).where(ProductModel.slug == slug))

    @staticmethod
    def categories() -> list[tuple[str, int]]:
        """Each category and how many products it holds, in shelf order."""
        query = (
            select(ProductModel.category, func.count())
            .group_by(ProductModel.category)
            .order_by(func.min(ProductModel.id))
        )
        with Session(engine) as session:
            return [(name, count) for name, count in session.execute(query)]
