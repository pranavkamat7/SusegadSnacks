from django.db import models

class CustomerType(models.Model):
    """
    Customer type model for extensibility (e.g. Retail, Wholesale, Distributor).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    Core customer info with FK to CustomerType for dynamic types.
    """
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    customer_type = models.ForeignKey(CustomerType, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.customer_type.name})"


class CustomerAddress(models.Model):
    """
    Support multiple addresses per customer if needed.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.address_line1}, {self.city}"
