from django.urls import path
from .views import InvoiceListView, InvoiceDetailView, GenerateInvoiceView, add_expense, expense_list, generate_invoice, invoice_detail, invoice_list, mark_invoice_as_paid, mark_paid, record_payment

app_name = 'billing'

urlpatterns = [
    path('', invoice_list, name='invoice_list'), 
    path('<int:pk>/', InvoiceDetailView.as_view(), name='detail'),
    path('generate/<int:order_id>/', GenerateInvoiceView.as_view(), name='generate'),
    path('expenselist', expense_list, name='expense_list'),
    path('add/', add_expense, name='add_expense'),
    path('mark-paid/<int:split_id>/', mark_paid, name='mark_paid'),
    path('generate-invoice/<int:order_id>/', generate_invoice, name='generate_invoice'),
    path('invoice/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('mark-as-paid/<int:invoice_id>/', mark_invoice_as_paid, name='mark_invoice_as_paid'),
    path('record-payment/<int:invoice_id>/', record_payment, name='record_payment'),
]
