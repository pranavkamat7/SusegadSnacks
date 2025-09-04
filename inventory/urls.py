from django.urls import path
from .views import (
    StockLocationListView, InventoryListView,
    StockMovementListView, StockMovementCreateView
)

app_name = 'inventory'

urlpatterns = [
    path('locations/', StockLocationListView.as_view(), name='location_list'),
    path('inventories/', InventoryListView.as_view(), name='inventory_list'),
    path('movements/', StockMovementListView.as_view(), name='stockmovement_list'),
    path('movements/create/', StockMovementCreateView.as_view(), name='stockmovement_create'),
]
