from django import forms
from .models import Product
from brands.models import Brand

class ProductForm(forms.ModelForm):
    # This explicit field definition is not strictly necessary if you just want a standard dropdown,
    # but it's good practice for clarity and customization.
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}) # Apply Bootstrap class
    )

    class Meta:
        model = Product
        # --- Add 'ptr' to the fields list ---
        fields = ['brand', 'name', 'description', 'mrp', 'ptr', 'margin', 'weight_gms', 'is_active']
        
        # --- (Optional but Recommended) Add widgets for Bootstrap styling ---
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control'}),
            'ptr': forms.NumberInput(attrs={'class': 'form-control'}),
            'margin': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight_gms': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SelectProductsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group products by brand
        for brand in Product.objects.values_list('brand', flat=True).distinct():
            products = Product.objects.filter(brand=brand, is_active=True)
            for product in products:
                field_name = f"product_{product.pk}"
                self.fields[field_name] = forms.IntegerField(
                    label=f"{brand} - {product.name}", min_value=0, initial=0, required=False
                )