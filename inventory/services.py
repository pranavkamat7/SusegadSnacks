from .models import Inventory, StockMovement
from django.db import transaction

class InventoryService:

    @staticmethod
    @transaction.atomic
    def add_stock(product, location, quantity, reference='', notes=''):
        inventory, created = Inventory.objects.get_or_create(product=product, location=location)
        # Update current stock
        inventory.quantity += quantity
        inventory.save()
        # Record stock movement
        StockMovement.objects.create(
            product=product,
            location=location,
            movement_type='in',
            quantity=quantity,
            reference=reference,
            notes=notes
        )
        return inventory

    @staticmethod
    @transaction.atomic
    def remove_stock(product, location, quantity, reference='', notes=''):
        inventory = Inventory.objects.get(product=product, location=location)
        if inventory.quantity < quantity:
            raise ValueError('Insufficient stock to remove')
        inventory.quantity -= quantity
        inventory.save()
        StockMovement.objects.create(
            product=product,
            location=location,
            movement_type='out',
            quantity=quantity,
            reference=reference,
            notes=notes
        )
        return inventory

    @staticmethod
    def get_stock_level(product, location):
        inventory = Inventory.objects.filter(product=product, location=location).first()
        return inventory.quantity if inventory else 0
