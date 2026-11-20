"""What a signed-in user can change: record that an invoice was paid."""

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.actions.accounts import go
from src.services.accounts import signed_in
from src.services.invoices import mark_paid


@Action
async def pay_invoice(invoice_id: int) -> RedirectResponse:
    signed_in()
    if not mark_paid(invoice_id):
        return go(f"/invoices/{invoice_id}", "This invoice is already paid.")
    return go(f"/invoices/{invoice_id}")
