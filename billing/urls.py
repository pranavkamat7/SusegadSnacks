from django.urls import path
from .views import InvoiceListView, InvoiceDetailView, GenerateInvoiceView, add_expense, expense_list, mark_paid

app_name = 'billing'

urlpatterns = [
    path('', InvoiceListView.as_view(), name='list'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='detail'),
    path('generate/<int:order_id>/', GenerateInvoiceView.as_view(), name='generate'),
    path('expenselist', expense_list, name='expense_list'),
    path('add/', add_expense, name='add_expense'),
    path('mark-paid/<int:split_id>/', mark_paid, name='mark_paid'),
]
