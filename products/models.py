from django.db import models
from brands.models import Brand

class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    mrp = models.DecimalField(max_digits=8, decimal_places=2)
    ptr = models.DecimalField(max_digits=8, decimal_places=2,blank=True,null=True)
    margin = models.DecimalField(max_digits=8, decimal_places=2)
    weight_gms = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand.name} - {self.name}"
