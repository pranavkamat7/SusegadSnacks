from django.urls import path
from .views import sales_report, customer_report, ar_aging_report

app_name = 'reports'

urlpatterns = [
    path('', sales_report, name='sales_report'),
    path('customers/', customer_report, name='customer_report'),
    path('ar-aging/', ar_aging_report, name='ar_aging_report'),
]
