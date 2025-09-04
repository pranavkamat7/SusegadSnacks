from django.contrib import admin
from .models import StockLocation, Inventory, StockMovement

@admin.register(StockLocation)
class StockLocationAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'quantity', 'updated_at')
    list_filter = ('location',)

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'movement_type', 'quantity', 'timestamp', 'reference')
    list_filter = ('movement_type', 'location')
    search_fields = ('product__name', 'reference')
