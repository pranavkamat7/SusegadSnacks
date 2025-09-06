from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from .models import Customer, CustomerAddress, CustomerType
from .services import CustomerService
from django.views.decorators.http import require_http_methods
class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

def customer_add(request):
    customer_types = CustomerType.objects.all()
    # Provide two blank address forms by default
    addresses = [CustomerAddress()]

    if request.method == "POST":
        name = request.POST.get("name", "")
        phone = request.POST.get("phone", "")
        email = request.POST.get("email", "")
        customer_type_id = request.POST.get("customer_type", "")
        customer = Customer.objects.create(
            name=name,
            phone=phone,
            email=email,
            customer_type_id=customer_type_id
        )
        # Save each address if any input given
        i = 0
        while True:
            addr_line1 = request.POST.get(f"address_line1_{i}", "")
            addr_line2 = request.POST.get(f"address_line2_{i}", "")
            city = request.POST.get(f"city_{i}", "")
            state = request.POST.get(f"state_{i}", "")
            pincode = request.POST.get(f"pincode_{i}", "")
            country = request.POST.get(f"country_{i}", "")
            is_primary = True if request.POST.get(f"is_primary_{i}") == "on" else False
            if not addr_line1 and not city and not pincode:
                break  # No more addresses
            CustomerAddress.objects.create(
                customer=customer,
                address_line1=addr_line1,
                address_line2=addr_line2,
                city=city,
                state=state,
                pincode=pincode,
                country=country,
                is_primary=is_primary,
            )
            i += 1
        return redirect("customers:list")
    return render(request, "customers/customer_form.html", {
        "customer": None,
        "customer_types": customer_types,
        "addresses": list(enumerate(addresses))
    })


def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customers/customer_detail.html', {
        'customer': customer
    })

def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    existing = list(customer.addresses.all())
    min_forms = 1
    to_add = max(0, min_forms - len(existing))
    addresses = existing + [CustomerAddress() for _ in range(to_add)]
    customer_types = CustomerType.objects.all()

    if request.method == "POST":
        customer.name = request.POST.get("name", "")
        customer.phone = request.POST.get("phone", "")
        customer.email = request.POST.get("email", "")
        customer_type_id = request.POST.get("customer_type", "")
        customer.customer_type_id = customer_type_id
        customer.save()
        # Handle addresses
        i = 0
        updated_ids = []
        while True:
            addr_id = request.POST.get(f"address_id_{i}", "")
            addr_line1 = request.POST.get(f"address_line1_{i}", "")
            addr_line2 = request.POST.get(f"address_line2_{i}", "")
            city = request.POST.get(f"city_{i}", "")
            state = request.POST.get(f"state_{i}", "")
            pincode = request.POST.get(f"pincode_{i}", "")
            country = request.POST.get(f"country_{i}", "")
            is_primary = True if request.POST.get(f"is_primary_{i}") == "on" else False
            is_delete = True if request.POST.get(f"delete_{i}") == "on" else False
            # No more addresses if these are empty
            if not addr_line1 and not city and not pincode and not addr_id:
                break
            if addr_id:
                addr = CustomerAddress.objects.filter(id=addr_id, customer=customer).first()
                if addr:
                    if is_delete:
                        addr.delete()
                    else:
                        addr.address_line1 = addr_line1
                        addr.address_line2 = addr_line2
                        addr.city = city
                        addr.state = state
                        addr.pincode = pincode
                        addr.country = country
                        addr.is_primary = is_primary
                        addr.save()
                        updated_ids.append(addr.id)
            else:
                # Create new address if not marked for delete
                if addr_line1 or city or pincode:
                    if not is_delete:
                        addr = CustomerAddress.objects.create(
                            customer=customer,
                            address_line1=addr_line1,
                            address_line2=addr_line2,
                            city=city,
                            state=state,
                            pincode=pincode,
                            country=country,
                            is_primary=is_primary
                        )
                        updated_ids.append(addr.id)
            i += 1
        return redirect("customers:list")
    return render(request, "customers/customer_form.html", {
        "customer": customer,
        "customer_types": customer_types,
        "addresses": list(enumerate(addresses))
    })


@require_http_methods(["GET", "POST"])
def customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == "POST":
        customer.delete()
        return redirect("customers:list")
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})