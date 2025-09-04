from .models import Customer, CustomerType

class CustomerService:

    @staticmethod
    def create_customer(data):
        customer_type = data.pop('customer_type')
        if isinstance(customer_type, str):
            customer_type_obj = CustomerType.objects.get(name=customer_type)
        else:
            customer_type_obj = customer_type
        customer = Customer.objects.create(customer_type=customer_type_obj, **data)
        return customer

    @staticmethod
    def list_customers(customer_type=None):
        queryset = Customer.objects.all()
        if customer_type:
            queryset = queryset.filter(customer_type__name=customer_type)
        return queryset

    @staticmethod
    def get_customer(customer_id):
        return Customer.objects.get(pk=customer_id)
