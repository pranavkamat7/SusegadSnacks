from django.urls import path
from .views import CustomerListView, customer_add, customer_delete, customer_detail, customer_edit

app_name = 'customers'

urlpatterns = [
    path('', CustomerListView.as_view(), name='list'),
    path('create/', customer_add, name='create'),
    path('<int:pk>/', customer_detail, name='detail'),
    path('<int:customer_id>/edit/', customer_edit, name='edit'),
    path('<int:customer_id>/delete/', customer_delete, name='delete'), 
]
