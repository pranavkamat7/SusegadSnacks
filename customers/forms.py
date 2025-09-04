from django import forms
from .models import Customer, CustomerType

class CustomerForm(forms.ModelForm):
    customer_type = forms.ModelChoiceField(queryset=CustomerType.objects.all(), required=True)

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'customer_type']


class SelectCustomerForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all())