from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from .models import Brand
from .forms import BrandForm
from .services import BrandService

class BrandListView(ListView):
    model = Brand
    template_name = 'brands/brand_list.html'
    context_object_name = 'brands'

class BrandCreateView(CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'brands/brand_form.html'
    success_url = reverse_lazy('brands:list')

    def form_valid(self, form):
        self.object = BrandService.create_brand(form.cleaned_data)
        return HttpResponseRedirect(self.get_success_url())

class BrandDetailView(DetailView):
    model = Brand
    template_name = 'brands/brand_detail.html'
    context_object_name = 'brand'

class BrandUpdateView(UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'brands/brand_form.html'
    success_url = reverse_lazy('brands:list')

    def form_valid(self, form):
        # Optional: Add custom update logic here if needed
        return super().form_valid(form)
