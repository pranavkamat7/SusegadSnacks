from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from .models import Customer
from .forms import CustomerForm
from .services import CustomerService

class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:list')

    
    def form_valid(self, form):
        self.object = CustomerService.create_customer(form.cleaned_data)
        return HttpResponseRedirect(self.get_success_url())

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:list')
