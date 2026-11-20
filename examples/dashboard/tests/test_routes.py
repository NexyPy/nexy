def test_the_overview_answers(client):
    assert client.get("/").status_code == 200


def test_the_overview_shows_the_revenue_of_30_days(client):
    assert "$70,228" in client.get("/").text


def test_the_overview_shows_the_window_it_adds_up(client):
    assert "Oct 17 to Nov 15, 2026" in client.get("/").text


def test_the_overview_follows_the_chosen_period(client):
    assert "Nov 9 to Nov 15, 2026" in client.get("/?days=7").text


def test_a_period_the_page_does_not_offer_shows_30_days(client):
    assert "Oct 17 to Nov 15, 2026" in client.get("/?days=9999").text


def test_a_hostile_channel_is_never_written_into_the_page(client):
    assert "alert(1)" not in client.get("/?channel=<script>alert(1)</script>").text


def test_the_overview_mounts_the_chart_with_its_window(client):
    assert "RevenueChart" in client.get("/?days=7").text


def test_the_api_gives_one_point_per_day(client):
    assert len(client.get("/api/revenue/?days=7").json()["series"]) == 7


def test_the_api_keeps_to_the_chosen_channel(client):
    assert client.get("/api/revenue/?channel=Cafe").json()["channel"] == "Cafe"


def test_the_api_drops_a_channel_it_does_not_know(client):
    assert client.get("/api/revenue/?channel=nowhere").json()["channel"] == ""


def test_the_orders_answer(client):
    assert client.get("/orders/").status_code == 200


def test_the_orders_show_the_newest_order_first(client):
    assert "#02750" in client.get("/orders/").text


def test_the_orders_link_to_the_next_page_with_the_channel(client):
    assert 'href="/orders/?channel=Cafe&page=2"' in client.get("/orders/?channel=Cafe").text


def test_a_page_that_is_not_a_number_shows_the_first(client):
    assert "Page 1 of" in client.get("/orders/?page=two").text


def test_no_order_shows_an_empty_table(client, empty):
    assert "No order yet." in client.get("/orders/").text
