from django import forms
from django.forms import inlineformset_factory
from .models import SalesOrder, OrderItem
from products.models import Product


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'status', 'remarks']
        widgets = {
            'status': forms.Select(),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True))

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }


OrderItemFormSet = inlineformset_factory(
    SalesOrder, OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True
)

class ConfirmOrderForm(forms.Form):
    confirm = forms.BooleanField(label="Confirm sales order?", required=True)
