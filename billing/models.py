from django.db import models
from orders.models import SalesOrder

class Invoice(models.Model):
    order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=32, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=32, choices=[('unpaid','Unpaid'),('paid','Paid')], default='unpaid')
    payment_mode = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Order {self.order.pk}"
