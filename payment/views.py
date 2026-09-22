from django.shortcuts import render
from .models import Shipping_Address, Order, OrderItem
from cart.cart import Cart
from django.http import JsonResponse
from ecommerce.constants import MethodsEnum
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_safe, require_http_methods, require_POST
from django.db import transaction
from django.conf import settings
from asgiref.sync import sync_to_async

# =========================================================================
# ASYNC VIEWS
# =========================================================================

@require_safe
async def payment_success(request):
    # Mutating session keys is done synchronously; wrapped inline
    def clear_session():
        if 'session-key' in request.session:
            request.session.pop('session-key')
            
    await sync_to_async(clear_session)()
    return render(request, 'payment/payment_success.html')


@require_http_methods([MethodsEnum.GET.value, MethodsEnum.POST.value])
async def checkout(request):
    shipping = None
    # Use sync_to_async to evaluate user attributes safely
    is_auth = await sync_to_async(lambda: request.user.is_authenticated)()
    
    if is_auth:
        try:
            user_pk = await sync_to_async(lambda: request.user.pk)()
            shipping = await Shipping_Address.objects.aget(user_id=user_pk)
        except Shipping_Address.DoesNotExist:
            shipping = None
            
    context = {
        'GOOGLE_PLACES_API': settings.GOOGLE_PLACES_API,
        'shipping_info': shipping
    }
    return render(request, 'payment/checkout.html', context)


@require_POST
async def complete_order(request):
    fullname = request.POST.get('name')
    email = request.POST.get('email')
    address1 = request.POST.get('address1')
    address2 = request.POST.get('address2')
    city = request.POST.get('city')
    zipcode = request.POST.get('zipcode')
    state = request.POST.get('state')
    
    shipping_address = f"{fullname}\n{email}\n{address1}\n{address2}\n{city}\n{zipcode}\n{state}\n"
    
    # We fetch user authentication status cleanly inline
    is_auth = await sync_to_async(lambda: request.user.is_authenticated)()
    user_defined = await sync_to_async(lambda: request.user if is_auth else None)()

    # FIX: Encapsulate Cart and atomic transactions inside a synchronous execution block
    def process_order_transaction():
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
                
    await sync_to_async(process_order_transaction)()
    return JsonResponse({'order_success': True})


# =========================================================================
# SYNC VIEWS (Kept sync for decorators and direct relational lookups)
# =========================================================================

@require_safe
def payment_failed(request):
    return render(request, 'payment/payment_failed.html')


@require_safe
@login_required(login_url='login')
def manage_shipping(request):
    return render(request, 'payment/manage_shipping.html')


@require_safe
@login_required(login_url='login')
def track_orders(request):
    # Kept synchronous so select_related evaluates flawlessly inside standard database querysets
    orders = OrderItem.objects.filter(user=request.user).select_related('order', 'product')
    return render(request, 'account/track_orders.html', {'orders': list(orders)})
