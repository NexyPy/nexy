from src.store.catalog import CATEGORIES, PRODUCTS, browse, find, money


def test_a_product_is_found_by_its_slug():
    assert find("ceramic-mug").name == "Ceramic mug"


def test_an_unknown_slug_finds_nothing():
    assert find("nope") is None


def test_every_slug_is_unique():
    assert len({product.slug for product in PRODUCTS}) == len(PRODUCTS)


def test_browsing_with_nothing_shows_every_product():
    assert len(browse()) == len(PRODUCTS)


def test_search_reads_the_name_without_case():
    assert [product.slug for product in browse("MUG")] == ["ceramic-mug"]


def test_search_reads_the_summary():
    assert [product.slug for product in browse("groceries")] == ["canvas-tote"]


def test_a_category_keeps_only_its_products():
    assert {product.category for product in browse(category="Paper")} == {"Paper"}


def test_categories_are_listed_once_in_catalog_order():
    assert CATEGORIES == ("Kitchen", "Paper", "Bags", "Wear")


def test_money_shows_dollars_and_cents():
    assert money(1800) == "$18.00"
