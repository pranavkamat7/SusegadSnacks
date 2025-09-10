from django.db import models
from orders.models import SalesOrder
from django.conf import settings
from django.contrib.auth.models import User

class Invoice(models.Model):
    order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=32, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=32, choices=[('unpaid','Unpaid'),('paid','Paid')], default='unpaid')
    payment_mode = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Order {self.order.pk}"



class Expense(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_incurred = models.DateField()
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')
    
    def total_split_amount(self):
        return sum(split.amount for split in self.splits.all())
    
    def __str__(self):
        return f"{self.description} - {self.amount} paid by {self.paid_by}"


class Split(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_splits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # New fields for payment tracking
    is_paid = models.BooleanField(default=False)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} owes {self.amount} for {self.expense.description}"