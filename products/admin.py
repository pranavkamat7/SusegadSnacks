from django.contrib import admin
from .models import Product
from brands.models import Brand

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'mrp', 'margin', 'weight_gms', 'is_active', 'created_at')
    list_filter = ('brand', 'is_active')
    search_fields = ('name',)
    ordering = ('brand', 'name')
