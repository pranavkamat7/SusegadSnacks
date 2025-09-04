from .models import Product

class ProductService:

    @staticmethod
    def create_product(data):
        product = Product.objects.create(**data)
        return product

    @staticmethod
    def list_products(brand_id=None):
        queryset = Product.objects.filter(is_active=True)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        return queryset

    @staticmethod
    def get_product(product_id):
        return Product.objects.get(pk=product_id)
