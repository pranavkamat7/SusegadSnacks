from .models import SalesOrder, OrderItem
from products.models import Product


class OrderService:

    @staticmethod
    def create_order(order_data, items_data):
        """
        Creates a SalesOrder with associated OrderItems.
        :param order_data: dict with SalesOrder fields
        :param items_data: list of dicts {'product_id': id, 'quantity': qty}
        :return: created SalesOrder instance
        """
        order = SalesOrder.objects.create(**order_data)
        total_amount = 0
        for item in items_data:
            product = Product.objects.get(pk=item['product_id'])
            quantity = item['quantity']
            price = product.mrp  # Or other pricing logic
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price * quantity
            )
            total_amount += price * quantity

        order.total_amount = total_amount
        order.save()
        return order

    @staticmethod
    def list_orders():
        return SalesOrder.objects.all()

    @staticmethod
    def get_order(order_id):
        return SalesOrder.objects.get(pk=order_id)
