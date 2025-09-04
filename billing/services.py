from .models import Invoice
from orders.models import SalesOrder
import uuid

class BillingService:

    @staticmethod
    def generate_invoice(order_id):
        order = SalesOrder.objects.get(pk=order_id)
        if hasattr(order, 'invoice'):
            return order.invoice

        invoice_number = str(uuid.uuid4()).replace('-', '').upper()[:12]
        invoice = Invoice.objects.create(
            order=order,
            invoice_number=invoice_number,
            total=order.total_amount,
            payment_status='unpaid'
        )
        return invoice
