import datetime
from django.shortcuts import render
from django.db.models import Sum, Count, Q ,F
from django.db.models.functions import TruncDay

from orders.models import SalesOrder, OrderItem
from billing.models import Invoice, Expense # Assuming you have these models from previous steps
from products.models import Product
from customers.models import Customer

def sales_report(request):
    """
    Generates and displays a sales report with date filtering.
    """
    # Get the selected month from the request, defaulting to the current month
    selected_month_str = request.GET.get('month', datetime.date.today().strftime('%Y-%m'))
    try:
        selected_month = datetime.datetime.strptime(selected_month_str, '%Y-%m').date()
    except ValueError:
        selected_month = datetime.date.today()

    # Calculate the first and last day of the selected month
    first_day = selected_month.replace(day=1)
    # A reliable way to get the last day of the month
    next_month = first_day.replace(day=28) + datetime.timedelta(days=4)
    last_day = next_month - datetime.timedelta(days=next_month.day)

    # --- 1. Key Metrics Summary Cards ---
    # Total Sales (from created orders in the period)
    total_sales = SalesOrder.objects.filter(
        created_at__range=[first_day, last_day],
        status__in=['pending', 'confirmed', 'delivered', 'billed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Total Cash In (from payments recorded in the period)
    total_cash_in = Invoice.objects.filter(
        created_at__range=[first_day, last_day],
        payment_status__in=['paid', 'partial']
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    # Total Cash Out (from expenses recorded in the period)
    total_cash_out = Expense.objects.filter(
        date_incurred__range=[first_day, last_day]
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Net Income calculation
    net_income = total_cash_in - total_cash_out

    # --- 2. Sales by Day (for a table view) ---
    sales_by_day = SalesOrder.objects.filter(
        created_at__range=[first_day, last_day]
    ).annotate(day=TruncDay('created_at')).values('day').annotate(
        daily_total=Sum('total_amount')
    ).order_by('day')

    # --- 3. Top Selling Products by Quantity ---
    top_products = OrderItem.objects.filter(
        order__created_at__range=[first_day, last_day]
    ).values('product__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_quantity')[:10] # Top 10

    context = {
        'selected_month': selected_month,
        'total_sales': total_sales,
        'total_cash_in': total_cash_in,
        'total_cash_out': total_cash_out,
        'net_income': net_income,
        'sales_by_day': sales_by_day,
        'top_products': top_products,
        'month_filter_value': selected_month_str, # For pre-filling the form
    }
    return render(request, 'reports/sales_report.html', context)



def customer_report(request):
    """
    Generates a report of sales and outstanding balances for each customer.
    """
    # Get the selected month, defaulting to the current month
    selected_month_str = request.GET.get('month', datetime.date.today().strftime('%Y-%m'))
    try:
        selected_month = datetime.datetime.strptime(selected_month_str, '%Y-%m').date()
    except ValueError:
        selected_month = datetime.date.today()

    first_day = selected_month.replace(day=1)
    next_month = first_day.replace(day=28) + datetime.timedelta(days=4)
    last_day = next_month - datetime.timedelta(days=next_month.day)

    # --- Use annotations to get total sales and payments per customer ---
    customers_data = Customer.objects.annotate(
        # Total sales for the selected month
        monthly_sales=Sum(
            'salesorder__total_amount',
            filter=Q(salesorder__created_at__range=[first_day, last_day])
        ),
        # Total amount paid for invoices related to orders in the selected month
        monthly_paid=Sum(
            'salesorder__invoice__amount_paid',
            filter=Q(salesorder__created_at__range=[first_day, last_day])
        ),
        # Total outstanding balance from ALL invoices, regardless of date
        total_outstanding=Sum('salesorder__invoice__total') - Sum('salesorder__invoice__amount_paid')
    ).filter(
        # Only show customers who had sales in the selected period
        monthly_sales__gt=0
    ).order_by('-monthly_sales')

    context = {
        'customers_data': customers_data,
        'selected_month': selected_month,
        'month_filter_value': selected_month_str,
    }
    return render(request, 'reports/customer_report.html', context)



from collections import OrderedDict
from billing.models import Invoice

def ar_aging_report(request):
    """
    Generates an Accounts Receivable (A/R) Aging Report.
    """
    today = datetime.date.today()
    
    # 1. Define the aging buckets
    buckets = OrderedDict([
        ('Current', {'start': -999, 'end': 0, 'total': 0, 'customers': {}}),
        ('1-30 Days', {'start': 1, 'end': 30, 'total': 0, 'customers': {}}),
        ('31-60 Days', {'start': 31, 'end': 60, 'total': 0, 'customers': {}}),
        ('61-90 Days', {'start': 61, 'end': 90, 'total': 0, 'customers': {}}),
        ('91+ Days', {'start': 91, 'end': 9999, 'total': 0, 'customers': {}}),
    ])

    # 2. Get all invoices that are not fully paid
    unpaid_invoices = Invoice.objects.filter(payment_status__in=['unpaid', 'partial'])
    
    # 3. Process each invoice to categorize it
    for invoice in unpaid_invoices:
        days_overdue = (today - invoice.created_at.date()).days
        balance = invoice.balance

        customer_name = invoice.order.customer.name
        
        # Find the correct bucket for the invoice
        for bucket_name, bucket_data in buckets.items():
            if bucket_data['start'] <= days_overdue <= bucket_data['end']:
                # Add customer's balance to the bucket's customer dictionary
                customer_balances = bucket_data['customers']
                customer_balances[customer_name] = customer_balances.get(customer_name, 0) + balance
                
                # Update the total for the bucket
                bucket_data['total'] += balance
                break
    
    # 4. Prepare data for the template in a more structured way
    report_data = {}
    all_customers = set()
    
    # Collect all unique customers across all buckets
    for bucket_data in buckets.values():
        all_customers.update(bucket_data['customers'].keys())

    # Build the final data structure for the template
    for customer in sorted(list(all_customers)):
        report_data[customer] = {
            'buckets': {bucket_name: 0 for bucket_name in buckets},
            'total_due': 0,
        }
        for bucket_name, bucket_data in buckets.items():
            amount = bucket_data['customers'].get(customer, 0)
            if amount > 0:
                report_data[customer]['buckets'][bucket_name] = amount
                report_data[customer]['total_due'] += amount

    context = {
        'report_data': report_data,
        'buckets': buckets, # Pass bucket totals for the footer
        'report_date': today,
    }
    
    return render(request, 'reports/ar_aging_report.html', context)

