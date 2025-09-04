from django.contrib import admin
from .models import Customer, CustomerType, CustomerAddress

@admin.register(CustomerType)
class CustomerTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'phone', 'email', 'created_at')
    list_filter = ('customer_type',)
    search_fields = ('name', 'phone', 'email')
    ordering = ('name',)

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address_line1', 'city', 'state', 'pincode', 'is_primary')
    list_filter = ('city', 'state', 'is_primary')
    search_fields = ('address_line1', 'city', 'state', 'pincode')
