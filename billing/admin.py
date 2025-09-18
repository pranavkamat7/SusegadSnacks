from django.contrib import admin, messages
from .models import Invoice
from django.db.models import Sum, F, DecimalField
from django.forms import BaseInlineFormSet
from .models import Expense, Split
import datetime
from django import forms

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'total', 'payment_status', 'payment_mode', 'created_at')
    list_filter = ('payment_status', 'payment_mode', 'created_at')
    search_fields = ('invoice_number', 'order__id')
    ordering = ('-created_at',)




# 1. Custom FormSet for Inline Validation
class SplitInlineFormSet(BaseInlineFormSet):
    """
    Custom formset for the Split inline model to add validation.
    """
    def clean(self):
        super().clean()
        if not hasattr(self.instance, 'amount'):
            # This can happen if the parent object (Expense) hasn't been saved yet.
            return

        total_split_amount = sum(
            form.cleaned_data.get('amount', 0)
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        )

        expense_amount = self.instance.amount

        if total_split_amount > expense_amount:
            raise forms.ValidationError(
                f"The sum of split amounts ({total_split_amount}) cannot exceed the total expense amount ({expense_amount})."
            )

# 2. Inline ModelAdmin for Splits
class SplitInline(admin.TabularInline):
    """
    Makes the Split model editable directly from the Expense admin page.
    """
    model = Split
    formset = SplitInlineFormSet
    extra = 1  # Show one extra blank form for adding a new split
    readonly_fields = ('balance',) # Display the calculated balance for each split
    
    fields = ('user', 'amount', 'is_paid', 'paid_amount', 'paid_date', 'balance')

    def balance(self, obj):
        """Calculated field to show the remaining amount owed for a split."""
        if obj.id: # Only calculate for existing objects
            return obj.amount - obj.paid_amount
        return 0
    balance.short_description = 'Balance Due'


# 3. Advanced ModelAdmin for Expense
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Advanced admin configuration for the Expense model.
    """
    inlines = [SplitInline]
    
    list_display = (
        'description',
        'amount',
        'paid_by',
        'date_incurred',
        'total_split_display', # Custom calculated field
        'balance_display'      # Custom calculated field
    )
    
    list_filter = ('date_incurred', 'paid_by')
    search_fields = ('description', 'paid_by__username')
    
    readonly_fields = ('total_split_amount',) # Show calculated value on the detail page

    fieldsets = (
        (None, {
            'fields': ('description', 'amount', 'date_incurred', 'paid_by')
        }),
        ('Calculated Totals', {
            'fields': ('total_split_amount',),
            'classes': ('collapse',) # Make this section collapsible
        }),
    )

    def get_queryset(self, request):
        """
        Annotate the queryset with the sum of splits to optimize display calculations.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _total_split=Sum('splits__amount', output_field=DecimalField())
        )
        return queryset

    def total_split_display(self, obj):
        """Display annotated total split amount in the list view."""
        return obj._total_split or 0
    total_split_display.short_description = 'Total Split Amount'

    def balance_display(self, obj):
        """Display the difference between expense amount and split amount."""
        total_split = obj._total_split or 0
        return obj.amount - total_split
    balance_display.short_description = 'Unassigned Balance'

# 4. Advanced ModelAdmin for Split
@admin.register(Split)
class SplitAdmin(admin.ModelAdmin):
    """
    Advanced admin configuration for the Split model.
    """
    list_display = (
        'expense_description', 
        'user', 
        'amount', 
        'paid_amount', 
        'balance', 
        'is_paid', 
        'paid_date'
    )
    
    list_filter = ('is_paid', 'user', 'expense__date_incurred')
    search_fields = ('user__username', 'expense__description')
    
    autocomplete_fields = ['user', 'expense'] # Use a search-friendly dropdown
    
    readonly_fields = ('expense_description', 'balance')
    
    actions = ['mark_as_fully_paid'] # Custom admin action

    def expense_description(self, obj):
        """Display the description of the related expense."""
        return obj.expense.description
    expense_description.short_description = 'Expense'
    
    def balance(self, obj):
        """Calculated field to show the remaining amount owed."""
        return obj.amount - obj.paid_amount
    balance.short_description = 'Balance Due'
    
    def mark_as_fully_paid(self, request, queryset):
        """
        Admin action to mark selected splits as fully paid.
        It sets the paid_amount to the full split amount and updates status.
        """
        updated_count = queryset.update(
            is_paid=True,
            paid_amount=F('amount'), # Set paid_amount equal to the amount field
            paid_date=datetime.date.today()
        )
        self.message_user(
            request,
            f'{updated_count} split(s) were successfully marked as fully paid.',
            messages.SUCCESS
        )
    mark_as_fully_paid.short_description = "Mark selected splits as fully paid"

