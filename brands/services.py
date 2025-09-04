from .models import Brand

class BrandService:

    @staticmethod
    def create_brand(data):
        brand = Brand.objects.create(**data)
        return brand

    @staticmethod
    def list_brands():
        return Brand.objects.all()

    @staticmethod
    def get_brand(brand_id):
        return Brand.objects.get(pk=brand_id)
