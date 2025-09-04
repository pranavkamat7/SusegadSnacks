from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy

from customers.forms import SelectCustomerForm
from customers.models import Customer
from products.forms import SelectProductsForm
from products.models import Product
from .models import OrderItem, SalesOrder
from .forms import ConfirmOrderForm, SalesOrderForm, OrderItemFormSet


class OrderListView(ListView):
    model = SalesOrder
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'


class OrderCreateView(View):
    template_name = 'orders/order_form.html'

    def get(self, request):
        order_form = SalesOrderForm()
        formset = OrderItemFormSet()
        return render(request, self.template_name, {
            'order_form': order_form,
            'formset': formset
        })

    def post(self, request):
        order_form = SalesOrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if order_form.is_valid() and formset.is_valid():
            order = order_form.save(commit=False)
            order.total_amount = 0  # will calculate shortly
            order.save()

            total = 0
            instances = formset.save(commit=False)
            for item in instances:
                item.order = order
                item.price = item.product.mrp * item.quantity
                item.save()
                total += item.price

            order.total_amount = total
            order.save()

            return redirect('orders:list')

        return render(request, self.template_name, {
            'order_form': order_form,
            'formset': formset
        })


class OrderDetailView(DetailView):
    model = SalesOrder
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'


class OrderUpdateView(View):
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:list')

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(SalesOrder, pk=pk)
        order_form = SalesOrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)
        return render(request, self.template_name, {
            'order_form': order_form,
            'formset': formset,
        })

    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(SalesOrder, pk=pk)
        order_form = SalesOrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)

        if order_form.is_valid() and formset.is_valid():
            saved_order = order_form.save(commit=False)
            formset.instance = saved_order

            # Save formset but do not commit DB write inside formset.save()
            order_items = formset.save(commit=False)

            # Delete items marked for deletion
            for obj in formset.deleted_objects:
                obj.delete()

            # Save/update each formset item and calculate total
            total_amount = 0
            for item in order_items:
                item.order = saved_order
                item.price = item.product.mrp * item.quantity
                item.save()
                total_amount += item.price

            # Save order with updated total
            saved_order.total_amount = total_amount
            saved_order.save()

            return redirect(self.success_url)

        # If form is invalid, re-render with errors for correction
        return render(request, self.template_name, {
            'order_form': order_form,
            'formset': formset,
        })

from django.shortcuts import render, redirect

# Step 1: Select Customer
def select_customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        if customer_id:
            request.session['customer_id'] = customer_id
            return redirect('orders:select_products')
    customers = Customer.objects.all()
    return render(request, 'orders/select_customer.html', {'customers': customers})

# Step 2: Select Products by Brand with quantities
def select_products(request):
    if 'customer_id' not in request.session:
        return redirect('orders:select_customer')

    if request.method == 'POST':
        selected_products = {}
        for key, val in request.POST.items():
            if key.startswith('product_') and val.isdigit():
                qty = int(val)
                if qty > 0:
                    prod_id = key.split('_')[1]
                    selected_products[prod_id] = qty
        if not selected_products:
            error = "Please select at least one product with quantity."
            # Reload product data for rendering with error
            products_by_brand = {}
            for p in Product.objects.filter(is_active=True).order_by('brand', 'name'):
                products_by_brand.setdefault(p.brand, []).append(p)
            return render(request, 'orders/select_products.html', {'products_by_brand': products_by_brand, 'error': error})

        request.session['selected_products'] = selected_products
        return redirect('orders:confirm_order')

    products_by_brand = {}
    for product in Product.objects.filter(is_active=True).order_by('brand', 'name'):
        products_by_brand.setdefault(product.brand, []).append(product)
    return render(request, 'orders/select_products.html', {'products_by_brand': products_by_brand})

# Step 3: Confirm Order
def confirm_order(request):
    if 'customer_id' not in request.session or 'selected_products' not in request.session:
        return redirect('orders:select_customer')

    customer = get_object_or_404(Customer, pk=request.session['customer_id'])
    selected_products = request.session['selected_products']
    products = Product.objects.filter(id__in=selected_products.keys())

    if request.method == 'POST':
        order = SalesOrder.objects.create(customer=customer, status='Pending', remarks='')
        total = 0
        for product in products:
            qty = selected_products[str(product.id)]
            price = product.mrp * qty
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)
            total += price
        order.total_amount = total
        order.save()

        # Clear session data
        request.session.pop('customer_id', None)
        request.session.pop('selected_products', None)

        return redirect('orders:order_success', pk=order.pk)

    return render(request, 'orders/confirm_order.html', {
        'customer': customer,
        'products': products,
        'quantities': selected_products,
    })

# Order creation success page
def order_success(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    return render(request, 'orders/order_success.html', {'order': order})

# Edit existing order — shows and allows update of order items and quantities
def edit_order(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    products = order.items.all()

    if request.method == 'POST':
        # Update quantities
        updated_quantities = {}
        for key, val in request.POST.items():
            if key.startswith('quantity_') and val.isdigit():
                item_id = key.split('_')[1]
                qty = int(val)
                updated_quantities[item_id] = qty

        # Update total price for items
        total = 0
        for item in products:
            if str(item.id) in updated_quantities:
                new_qty = updated_quantities[str(item.id)]
                item.quantity = new_qty
                item.price = item.product.mrp * new_qty
                item.save()
                total += item.price
            else:
                total += item.price  # unchanged if not in POST

        # Update SalesOrder status from POST data
        new_status = request.POST.get('status')
        if new_status and new_status != order.status:
            order.status = new_status

        order.total_amount = total
        order.save()
        return redirect('orders:order_success', pk=order.pk)

    # If GET, pass available statuses to template (assuming SalesOrder.STATUS_CHOICES exists)
    status_choices = getattr(order, 'STATUS_CHOICES', [])
    return render(request, 'orders/edit_order.html', {
        'order': order,
        'products': products,
        'status_choices': status_choices,
    })