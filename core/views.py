from django.shortcuts import render
from django.utils import timezone

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

    orders = SalesOrder.objects.filter(created_at__date=filter_date).order_by('-created_at')
    return render(request, 'includes/dashboard.html', {
        'orders': orders,
        'filter_date': filter_date.strftime('%Y-%m-%d'),
    })
