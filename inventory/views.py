from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import StockLocation, Inventory, StockMovement
from .forms import StockMovementForm

class StockLocationListView(ListView):
    model = StockLocation
    template_name = 'inventory/stocklocation_list.html'
    context_object_name = 'locations'

class InventoryListView(ListView):
    model = Inventory
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'inventories'

    def get_queryset(self):
        # Optionally filter by location from URL query params
        location_id = self.request.GET.get('location')
        if location_id:
            return Inventory.objects.filter(location_id=location_id)
        return super().get_queryset()

class StockMovementListView(ListView):
    model = StockMovement
    template_name = 'inventory/stockmovement_list.html'
    context_object_name = 'movements'
    paginate_by = 50

    def get_queryset(self):
        # Optionally filter by product or location
        qs = super().get_queryset().order_by('-timestamp')
        product_id = self.request.GET.get('product')
        location_id = self.request.GET.get('location')
        if product_id:
            qs = qs.filter(product_id=product_id)
        if location_id:
            qs = qs.filter(location_id=location_id)
        return qs

class StockMovementCreateView(CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'inventory/stockmovement_form.html'
    success_url = reverse_lazy('inventory:stockmovement_list')

    def form_valid(self, form):
        # Optional: Add custom validation or business logic here
        return HttpResponseRedirect(self.get_success_url())
    