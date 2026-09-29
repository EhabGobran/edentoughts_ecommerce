from django.shortcuts import render
from .models import Shipping_Address, Order, OrderItem
from cart.cart import Cart
from django.http import JsonResponse
from ecommerce.constants import MethodsEnum
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from django.http import HttpResponseNotAllowed
from ecommerce.constants import request_method_enum

def payment_success(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
        
    if 'session-key' in request.session:
        request.session.pop('session-key')
            
    return render(request, 'payment/payment_success.html')


def checkout(request):
    allowed_methods = list(request_method_enum.keys())
    if request.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)
    
    shipping = None
    if request.user.is_authenticated:
        try:
            shipping = Shipping_Address.objects.get(user_id=request.user.pk)
        except Shipping_Address.DoesNotExist:
            shipping = None
            
    context = {
        'GOOGLE_PLACES_API': settings.GOOGLE_PLACES_API,
        'shipping_info': shipping
    }
    return render(request, 'payment/checkout.html', context)


def complete_order(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
        
    fullname = request.POST.get('name')
    email = request.POST.get('email')
    address1 = request.POST.get('address1')
    address2 = request.POST.get('address2')
    city = request.POST.get('city')
    zipcode = request.POST.get('zipcode')
    state = request.POST.get('state')
    
    shipping_address = f"{fullname}\n{email}\n{address1}\n{address2}\n{city}\n{zipcode}\n{state}\n"
    
    user_defined = request.user if request.user.is_authenticated else None

    with transaction.atomic():
        cart_instance = Cart(request)
        amount_paid = cart_instance.get_total()
        
        order = Order.objects.create(
            fullname=fullname,
            email=email,
            shipping_address=shipping_address,
            amount_paid=amount_paid,
            user=user_defined
        )
        
        for item in cart_instance:
            OrderItem.objects.create(
                order_id=order.pk,
                product=item['product'],
                quantity=item['qty'],
                price=item['price'],
                user=user_defined
            )
                
    return JsonResponse({'order_success': True})


def payment_failed(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    return render(request, 'payment/payment_failed.html')


@login_required(login_url='login')
def manage_shipping(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    return render(request, 'payment/manage_shipping.html')


@login_required(login_url='login')
def track_orders(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
        
    orders = OrderItem.objects.filter(user=request.user).select_related('order', 'product')
    return render(request, 'account/track_orders.html', {'orders': list(orders)})
