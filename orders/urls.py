from django.urls import path
from .views import OrderListView, OrderCreateView, OrderDetailView, OrderUpdateView, confirm_order, edit_order, order_success, select_customer, select_products

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('create/', OrderCreateView.as_view(), name='create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', OrderUpdateView.as_view(), name='order-edit'),
    path('salesorder/select_customer/', select_customer, name='select_customer'),
    path('salesorder/select_products/', select_products, name='select_products'),
    path('salesorder/confirm_order/', confirm_order, name='confirm_order'),
    path('salesorder/success/<int:pk>/',order_success, name='order_success'),
    path('salesorder/edit/<int:pk>/', edit_order, name='order_edit'),
]
