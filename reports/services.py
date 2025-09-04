from orders.models import SalesOrder, OrderItem
from products.models import Product
from brands.models import Brand
from django.db.models import Sum, Count
from django.utils.timezone import now
from datetime import timedelta

class SalesReportService:

    @staticmethod
    def get_sales_stats(brand_id=None, start_date=None, end_date=None):
        """
        Returns aggregated sales data filtered by optional brand and date ranges.
        
        :param brand_id: filter for specific brand
        :param start_date: filter sales from this date (inclusive)
        :param end_date: filter sales up to this date (inclusive)
        :return: dict with total_sales, total_orders, product_breakdown
        """
        orders = SalesOrder.objects.filter(status='delivered')
        if start_date:
            orders = orders.filter(created_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__date__lte=end_date)

        if brand_id:
            orders = orders.filter(items__product__brand_id=brand_id).distinct()

        total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = orders.count()

        product_stats = OrderItem.objects.filter(
            order__in=orders
        ).values('product__id', 'product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_revenue')

        return {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'product_stats': list(product_stats)
        }

    @staticmethod
    def get_monthly_sales(brand_id=None, months=12):
        """
        Returns monthly sales totals for the last 'months' number of months.
        Useful for month-over-month trend charts.

        :param brand_id: Optional brand filter
        :param months: Number of past months to include
        :return: list of dicts with 'month' and 'total_sales'
        """
        from django.db.models.functions import TruncMonth
        from django.db.models import DateTimeField

        end_date = now()
        start_date = end_date - timedelta(days=30 * months)

        orders = SalesOrder.objects.filter(
            status='delivered',
            created_at__range=(start_date, end_date)
        )

        if brand_id:
            orders = orders.filter(items__product__brand_id=brand_id).distinct()

        monthly_data = orders.annotate(
            month=TruncMonth('created_at', output_field=DateTimeField())
        ).values('month').annotate(
            total_sales=Sum('total_amount'),
            total_orders=Count('id')
        ).order_by('month')

        # Format output
        result = [
            {
                'month': data['month'].strftime('%Y-%m'),
                'total_sales': data['total_sales'] or 0,
                'total_orders': data['total_orders']
            }
            for data in monthly_data
        ]

        return result
