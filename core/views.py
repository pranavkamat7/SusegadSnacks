from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from orders.models import SalesOrder

def dashboard(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            filter_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            filter_date = timezone.localdate()
    else:
        filter_date = timezone.localdate()

    # Filter orders by the selected date
    orders = SalesOrder.objects.filter(created_at__date=filter_date).order_by('-created_at')

    # Calculate the sum of total_amount for the filtered orders
    total_amount_sum = orders.aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'orders': orders,
        'filter_date': filter_date.strftime('%Y-%m-%d'),
        'total_amount_sum': total_amount_sum,
    }
    
    return render(request, 'includes/dashboard.html', context)