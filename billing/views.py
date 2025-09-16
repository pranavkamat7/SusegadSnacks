from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from orders.models import SalesOrder
from .models import Invoice, Expense, Split
from .services import BillingService
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
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



@login_required
def expense_list(request):
    expenses = Expense.objects.filter(paid_by=request.user).order_by('-date_incurred')
    return render(request, 'billing/expense_list.html', {'expenses': expenses})


@login_required
def add_expense(request):
    users = User.objects.all()
    errors = {}
    selected_user_ids = []
    posted_data = {}
    manual_splits = {}

    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        amount = request.POST.get('amount', '').strip()
        date_incurred = request.POST.get('date_incurred', '').strip()
        paid_by = request.user
        involved_users = request.POST.getlist('users')
        splits_input = request.POST.getlist('splits')

        posted_data = request.POST.copy()
        selected_user_ids = involved_users

        # Basic validations
        if not description:
            errors['description'] = "Description is required."
        try:
            amount_val = float(amount)
            if amount_val <= 0:
                errors['amount'] = "Amount must be positive."
        except:
            errors['amount'] = "Invalid amount."
        if not date_incurred:
            errors['date_incurred'] = "Date is required."
        if not involved_users:
            errors['users'] = "Select at least one user."

        # Build splits dict and fallback to equal split if missing or invalid
        split_amounts = {}
        try:
            for user_id, split_str in zip(involved_users, splits_input):
                split_amounts[user_id] = float(split_str) if split_str.strip() else 0
        except:
            errors['splits'] = "Invalid split amount."

        # If sum differs from total amount, override splits to equal fallback silently
        if not errors:
            total_splits = round(sum(split_amounts.values()), 2)
            if abs(total_splits - amount_val) > 0.01:
                # Override splits to equal share
                equal_share = round(amount_val / len(involved_users), 2)
                for user_id in involved_users:
                    split_amounts[user_id] = equal_share

        if errors:
            return render(request, 'billing/add_expense.html', {
                'errors': errors,
                'users': users,
                'selected_user_ids': selected_user_ids,
                'posted': posted_data,
                'manual_splits': split_amounts,
            })

        # Save data
        with transaction.atomic():
            expense = Expense.objects.create(description=description, amount=amount_val, date_incurred=date_incurred, paid_by=paid_by)
            for user_id, sa in split_amounts.items():
                try:
                    user_obj = User.objects.get(id=user_id)
                    Split.objects.create(expense=expense, user=user_obj, amount=sa)
                except User.DoesNotExist:
                    continue
        return redirect('billing:expense_list')

    # GET request
    return render(request, 'billing/add_expense.html', {
        'users': users,
        'errors': errors,
        'selected_user_ids': [],
        'posted': {},
        'manual_splits': {},
    })
    
    
@login_required
def mark_paid(request, split_id):
    split = get_object_or_404(Split, id=split_id, user=request.user)
    if request.method == "POST":
        split.is_paid = True
        split.paid_amount = split.amount
        split.paid_date = timezone.now().date()
        split.save()
        return redirect('billing:expense_list')
    return render(request, 'billing/mark_paid_confirm.html', {'split': split})


def generate_invoice(request, order_id):
    """
    Generates an invoice for a delivered order.
    """
    order = get_object_or_404(SalesOrder, id=order_id)

    # 1. Check if the order is ready to be billed
    if order.status != 'delivered':
        messages.error(request, "Invoice can only be generated for delivered orders.")
        return redirect('orders:order_detail', pk=order_id) # Redirect to your order detail page

    # 2. Check if an invoice already exists
    if hasattr(order, 'invoice'):
        messages.info(request, "An invoice for this order already exists.")
        return redirect('billing:invoice_detail', invoice_id=order.invoice.id)

    # 3. Generate the invoice
    invoice = Invoice.objects.create(
        order=order,
        invoice_number=f"INV-{order.id}-{timezone.now().strftime('%Y%m%d')}",
        total=order.total_amount
    )

    # 4. Update order status to 'billed'
    order.status = 'billed'
    order.save()

    messages.success(request, f"Invoice {invoice.invoice_number} generated successfully.")
    return redirect('billing:invoice_detail', invoice_id=invoice.id)


def invoice_detail(request, invoice_id):
    """
    Displays the details of a single invoice and calculates item totals.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Calculate total quantity and weight for the table footer
    total_quantity = 0
    total_weight = 0
    for item in invoice.order.items.all():
        total_quantity += item.quantity
        # Calculate total weight by multiplying item weight by its quantity
        total_weight += (item.product.weight_gms * item.quantity)
        
    context = {
        'invoice': invoice,
        'total_quantity': total_quantity,
        'total_weight': total_weight,
    }
    
    return render(request, 'billing/invoice_detail.html', context)


def mark_invoice_as_paid(request, invoice_id):
    """
    Marks an invoice as paid and records the payment mode.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        payment_mode = request.POST.get('payment_mode')
        
        if not payment_mode:
            messages.error(request, "Please select a payment mode.")
            return redirect('billing:invoice_detail', invoice_id=invoice.id)

        # Update the invoice status
        invoice.payment_status = 'paid'
        invoice.payment_mode = payment_mode
        invoice.save()
        
        messages.success(request, f"Invoice {invoice.invoice_number} has been marked as paid.")
        return redirect('billing:invoice_detail', invoice_id=invoice.id)

    return redirect('billing:invoice_detail', invoice_id=invoice.id)


def record_payment(request, invoice_id):
    """
    Records a full or partial payment for an invoice.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        payment_amount_str = request.POST.get('payment_amount')
        payment_mode = request.POST.get('payment_mode')

        # --- Validation ---
        if not payment_amount_str or not payment_mode:
            messages.error(request, "Please provide both payment amount and mode.")
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
        
        try:
            payment_amount = Decimal(payment_amount_str)
        except:
            messages.error(request, "Invalid payment amount entered.")
            return redirect('billing:invoice_detail', invoice_id=invoice.id)

        if payment_amount <= 0:
            messages.error(request, "Payment amount must be a positive number.")
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
            
        if payment_amount > invoice.balance:
            messages.error(request, f"Payment cannot exceed the remaining balance of ₹{invoice.balance}.")
            return redirect('billing:invoice_detail', invoice_id=invoice.id)

        # --- Update Invoice ---
        invoice.amount_paid += payment_amount
        invoice.payment_mode = payment_mode

        if invoice.amount_paid >= invoice.total:
            invoice.payment_status = 'paid'
        else:
            invoice.payment_status = 'partial'
        
        invoice.save()

        messages.success(request, f"Payment of ₹{payment_amount} recorded successfully.")
        return redirect('billing:invoice_detail', invoice_id=invoice.id)

    # Redirect if not a POST request
    return redirect('billing:invoice_detail', invoice_id=invoice.id)


def invoice_list(request):
    """
    Displays a list of all invoices.
    """
    invoices = Invoice.objects.all().order_by('-created_at')
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Invoice

def render_pdf_view(request, invoice_id):
    """
    Renders an invoice as a PDF, including calculated totals.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Calculate total quantity and weight for the PDF context
    total_quantity = 0
    total_weight = 0
    for item in invoice.order.items.all():
        total_quantity += item.quantity
        total_weight += (item.product.weight_gms * item.quantity)

    # Prepare the context for the template
    template_path = 'billing/invoice_pdf.html'
    context = {
        'invoice': invoice,
        'total_quantity': total_quantity,
        'total_weight': total_weight,
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'

    # Find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # If error, show an error message
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
