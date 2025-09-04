from django.db import models
from products.models import Product
from django.utils.translation import gettext_lazy as _

class StockLocation(models.Model):
    """
    Optional: Physical location like warehouse, store, etc.
    """
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    """
    Tracks current stock level for a product at a location.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    location = models.ForeignKey(StockLocation, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)  # Can be negative during reconciliation if needed
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'location')

    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.quantity}"

class StockMovement(models.Model):
    """
    Records stock additions/removals for audit trail.
    """
    MOVEMENT_TYPE_CHOICES = [
        ('in', _('Stock In')),
        ('out', _('Stock Out')),
        ('adjustment', _('Adjustment')),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    location = models.ForeignKey(StockLocation, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, blank=True)  # e.g., Order ID, Supplier invoice
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.quantity} of {self.product.name} at {self.location.name}"
