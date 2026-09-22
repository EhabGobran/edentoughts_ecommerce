from django.shortcuts import render , get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
# Create your views here.

def cart_summary(request):
    return render(request , "cart/cart-summary.html")

def cart_update(request):
    cart= Cart(request)
    if request.POST.get('action') == 'post':
        product_id= int(request.POST.get('product_id'))
        product_quantity= int(request.POST.get('product_quantity'))
        cart.update(product_id=product_id , product_quantity=product_quantity)
        cart_quantity = cart.__len__()
        cart_total = cart.get_total()

        return JsonResponse({'qty': cart_quantity, 'total': cart_total})

def cart_delete(request):
    cart= Cart(request)
    if request.POST.get("action") == 'post':
        product_id = int(request.POST.get('product_id'))
        return cart.delete(product_id=product_id)
        
    

def cart_add(request):
    cart= Cart(request)
    if request.POST.get('action') == 'post':
        product_id= int(request.POST.get('product_id'))
        product_qty= int(request.POST.get('product_quantity'))

        product= get_object_or_404(Product, pk= product_id)

        cart.add(product , product_qty)
        cart_quantity = cart.__len__()
        cart_total = cart.get_total()

        return JsonResponse({'qty': cart_quantity, 'total': cart_total})