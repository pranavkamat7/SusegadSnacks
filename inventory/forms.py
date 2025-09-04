from django import forms
from .models import StockMovement, StockLocation
from products.models import Product

class StockMovementForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True), required=True)
    location = forms.ModelChoiceField(queryset=StockLocation.objects.all(), required=True)

    class Meta:
        model = StockMovement
        fields = ['product', 'location', 'movement_type', 'quantity', 'reference', 'notes']

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty <= 0:
            raise forms.ValidationError('Quantity must be greater than zero.')
        return qty
