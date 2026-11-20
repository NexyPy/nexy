"""The actions the shop pages call to read the shelves."""

from nexy import notFound
from nexy.decorators import Action
from pydantic import BaseModel, ConfigDict

from src.services.catalog_service import CatalogService

RELATED = 3


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    category: str
    price_cents: int
    summary: str
    details: list[str]
    stock: int
    image: str


class Category(BaseModel):
    name: str
    count: int


class Shelf(BaseModel):
    products: list[Product]
    categories: list[Category]


class ProductPage(BaseModel):
    product: Product
    related: list[Product]  # from the same category


@Action
def catalog(category: str = "", search: str = "") -> Shelf:
    """The products of a category whose name or summary holds `search`, and every category."""
    found = CatalogService.browse(category, search)
    counted = CatalogService.categories()
    return Shelf(
        products=[Product.model_validate(product) for product in found],
        categories=[Category(name=name, count=count) for name, count in counted],
    )


@Action
def product(slug: str) -> ProductPage:
    """One product and a few of its category; a 404 for a product the shop does not sell."""
    found = CatalogService.find(slug)
    if found is None:
        notFound()
    others = [item for item in CatalogService.browse(found.category) if item.slug != slug]
    return ProductPage(
        product=Product.model_validate(found),
        related=[Product.model_validate(item) for item in others[:RELATED]],
    )
