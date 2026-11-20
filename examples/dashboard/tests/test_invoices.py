from datetime import date

from conftest import TODAY
from src.models.invoice import Invoice, status
from src.services.invoices import PAGE_SIZE, find, mark_paid, search
from src.services.money import money


def _invoice(due: date, paid_on: date | None = None) -> Invoice:
    return Invoice(number="X", customer_id=1, amount_cents=1, issued=due, due=due, paid_on=paid_on)


def test_a_paid_invoice_is_paid():
    assert status(_invoice(date(2026, 1, 1), date(2026, 1, 2)), TODAY) == "paid"


def test_an_unpaid_invoice_past_its_due_date_is_overdue():
    assert status(_invoice(date(2026, 11, 19)), TODAY) == "overdue"


def test_an_unpaid_invoice_due_today_is_pending():
    assert status(_invoice(TODAY), TODAY) == "pending"


def test_the_demo_has_ninety_invoices():
    assert search(today=TODAY).total == 90


def test_a_page_holds_at_most_the_page_size():
    assert len(search(today=TODAY).rows) == PAGE_SIZE


def test_the_newest_invoice_comes_first():
    rows = search(today=TODAY).rows
    assert rows[0].issued >= rows[-1].issued


def test_search_finds_a_customer_by_part_of_its_name():
    assert {row.customer for row in search("kestrel", today=TODAY).rows} == {"Kestrel Labs"}


def test_search_finds_an_invoice_by_its_number():
    assert [row.number for row in search("INV-0042", today=TODAY).rows] == ["INV-0042"]


def test_the_status_filter_keeps_only_that_status():
    rows = search(wanted="overdue", today=TODAY).rows
    assert {row.status for row in rows} == {"overdue"}


def test_a_page_past_the_last_shows_the_last():
    page = search(number=999, today=TODAY)
    assert page.number == page.pages


def test_nothing_found_is_one_empty_page():
    page = search("no such customer", today=TODAY)
    assert (page.total, page.pages, page.rows) == (0, 1, [])


def test_an_invoice_is_found_with_its_customer_email():
    assert find(1, TODAY)[1].endswith(".example")


def test_an_unknown_invoice_is_none():
    assert find(999, TODAY) is None


def test_paying_an_invoice_makes_it_paid():
    unpaid = search(wanted="overdue", today=TODAY).rows[0]
    mark_paid(unpaid.id, TODAY)
    assert find(unpaid.id, TODAY)[0].status == "paid"


def test_an_invoice_is_paid_only_once():
    paid = search(wanted="paid", today=TODAY).rows[0]
    assert mark_paid(paid.id, TODAY) is False


def test_an_unknown_invoice_cannot_be_paid():
    assert mark_paid(999, TODAY) is False


def test_money_shows_dollars_and_cents():
    assert money(123456) == "$1,234.56"
