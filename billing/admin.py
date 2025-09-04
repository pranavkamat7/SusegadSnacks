from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'total', 'payment_status', 'payment_mode', 'created_at')
    list_filter = ('payment_status', 'payment_mode', 'created_at')
    search_fields = ('invoice_number', 'order__id')
    ordering = ('-created_at',)
