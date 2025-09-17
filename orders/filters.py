import django_filters
from django import forms
from .models import SalesOrder
from customers.models import Customer

class OrderFilter(django_filters.FilterSet):
    # Filter by customer name
    customer = django_filters.CharFilter(
        field_name='customer__name', 
        lookup_expr='icontains',
        label='Customer Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'})
    )

    # --- This is the corrected 'status' filter ---
    status = django_filters.ChoiceFilter(
        # The choices are now correctly concatenated as two tuples
        choices=(('', 'All Statuses'),) + tuple(SalesOrder.STATUS_CHOICES),
        label='Status',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Date range filters
    start_date = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='From Date',
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'placeholder': 'YYYY-MM-DD'})
    )
    end_date = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='To Date',
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'placeholder': 'YYYY-MM-DD'})
    )

    class Meta:
        model = SalesOrder
        # We define all fields explicitly above, so this can be empty
        fields = [] 
