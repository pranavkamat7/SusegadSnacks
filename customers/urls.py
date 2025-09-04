from django.urls import path
from .views import CustomerListView, CustomerCreateView, CustomerDetailView, CustomerUpdateView

app_name = 'customers'

urlpatterns = [
    path('', CustomerListView.as_view(), name='list'),
    path('create/', CustomerCreateView.as_view(), name='create'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', CustomerUpdateView.as_view(), name='edit'),
]
