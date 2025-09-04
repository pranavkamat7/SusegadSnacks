from django.urls import path
from .views import BrandListView, BrandCreateView, BrandDetailView, BrandUpdateView

app_name = 'brands'

urlpatterns = [
    path('', BrandListView.as_view(), name='list'),
    path('create/', BrandCreateView.as_view(), name='create'),
    path('<int:pk>/', BrandDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', BrandUpdateView.as_view(), name='edit'),
]
