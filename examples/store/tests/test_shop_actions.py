def test_the_catalog_answers_every_product(call):
    assert len(call("catalog").json()["products"]) == 8


def test_the_catalog_answers_the_categories_with_their_count(call):
    assert call("catalog").json()["categories"][0] == {"name": "Kitchen", "count": 3}


def test_the_catalog_answers_one_category(call):
    products = call("catalog", category="Wear").json()["products"]
    assert [product["slug"] for product in products] == ["wool-beanie"]


def test_the_catalog_answers_a_search(call):
    products = call("catalog", search="notebook").json()["products"]
    assert [product["slug"] for product in products] == ["dot-notebook"]


def test_a_product_answers_its_details(call):
    product = call("product", slug="pencil-set").json()["product"]
    assert product["details"] == ["2H, H, HB, B, 2B, 4B", "Cedar wood", "Sharpened"]


def test_a_product_answers_others_of_its_category(call):
    related = call("product", slug="ceramic-mug").json()["related"]
    assert [product["slug"] for product in related] == ["pour-over", "linen-apron"]


def test_a_product_the_shop_does_not_sell_answers_404(call):
    assert call("product", slug="nowhere").status_code == 404


def test_an_action_without_its_input_answers_422(call):
    assert call("product").status_code == 422
