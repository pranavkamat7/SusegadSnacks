from django import forms
from .models import Product
from brands.models import Brand

class ProductForm(forms.ModelForm):
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=True)

    class Meta:
        model = Product
        fields = ['brand', 'name', 'description', 'mrp', 'margin', 'weight_gms', 'is_active']


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