from django.urls import path
from .views import InvoiceListView, InvoiceDetailView, GenerateInvoiceView

app_name = 'billing'

urlpatterns = [
    path('', InvoiceListView.as_view(), name='list'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='detail'),
    path('generate/<int:order_id>/', GenerateInvoiceView.as_view(), name='generate'),
]
