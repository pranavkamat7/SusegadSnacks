from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect, get_object_or_404
from .models import Invoice
from .services import BillingService

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'

class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'

class GenerateInvoiceView(View):

    def get(self, request, order_id):
        invoice = BillingService.generate_invoice(order_id)
        return redirect('billing:detail', pk=invoice.pk)
