from src.services.catalog_service import CatalogService, containing


def slugs(products):
    return [product.slug for product in products]


def test_the_shelves_hold_the_eight_products_of_the_migration():
    assert len(CatalogService.browse()) == 8


def test_a_category_holds_its_products_only():
    assert slugs(CatalogService.browse("Bags")) == ["canvas-tote", "field-bag"]


def test_a_search_finds_a_word_of_the_name():
    assert slugs(CatalogService.browse(text="mug")) == ["ceramic-mug"]


def test_a_search_finds_a_word_of_the_summary():
    assert slugs(CatalogService.browse(text="laptop")) == ["canvas-tote"]


def test_a_search_ignores_case():
    assert slugs(CatalogService.browse(text="LINEN")) == ["linen-apron"]


def test_a_search_ignores_the_spaces_around_it():
    assert slugs(CatalogService.browse(text="  beanie ")) == ["wool-beanie"]


def test_a_search_and_a_category_both_apply():
    assert CatalogService.browse("Paper", "mug") == []


def test_a_percent_sign_is_searched_as_itself():
    assert containing("100%") == "%100\\%%"


def test_a_product_is_found_by_its_slug():
    assert CatalogService.find("pour-over").name == "Pour-over dripper"


def test_an_unknown_slug_finds_nothing():
    assert CatalogService.find("nowhere") is None


def test_categories_are_counted_in_shelf_order():
    assert CatalogService.categories() == [("Kitchen", 3), ("Paper", 2), ("Bags", 2), ("Wear", 1)]


def test_a_product_shows_its_picture_from_public():
    assert CatalogService.find("field-bag").image == "/products/field-bag.svg"
