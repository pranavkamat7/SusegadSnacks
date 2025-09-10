from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect, get_object_or_404
from .models import Invoice, Expense, Split
from .services import BillingService
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone

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