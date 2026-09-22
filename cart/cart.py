from django.http import JsonResponse
from decimal import Decimal
from store.models import Product
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
class Cart():
    def __init__(self ,request):
        
        self.session= request.session
        cart= self.session.get('session-key')

        if 'session-key' not in self.session:
            cart=  self.session['session-key']= {}
        
        self.cart= cart

        
        
    def add(self ,product ,product_qty):

        product_id= str(product.id)

        if product_id in self.cart:
            self.cart[product_id]['qty']= product_qty

        else:
            self.cart[product_id]= {'price': str(product.price), 'qty': product_qty}

        self.session.modified= True

    def __iter__(self):
        from copy import deepcopy
        from decimal import Decimal
        from asgiref.sync import async_to_sync, sync_to_async
        import asyncio

        cart = deepcopy(self.cart)
        all_products_id = cart.keys()

        def get_evaluated_products():
            return list(Product.objects.filter(id__in=all_products_id))

        # Check if an async loop is active without letting an exception break the app
        try:
            asyncio.get_running_loop()
            # Loop exists -> Safely wrap execution on an isolated database thread
            products = async_to_sync(sync_to_async(get_evaluated_products))()
        except RuntimeError:
            # No loop -> We are in a standard sync view, fetch directly
            products = get_evaluated_products()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total'] = item['price'] * item['qty']
            yield item

        
    def get_total(self):
        return sum(Decimal(item['price'])* item['qty'] for item in self.cart.values())
    
    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())

    def delete(self, product_id):
        product_id= str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            cart_quantity= self.__len__()
            cart_total= self.get_total()
            self.session.modified= True
            return JsonResponse({'cart_quantity': cart_quantity , 'cart_total': cart_total})

    def update(self, product_id, product_quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id]['qty'] = product_quantity
            self.session.modified = True
            return JsonResponse({'product_quantity': product_quantity})
        
        # Fallback
        return JsonResponse({'error': 'Product not in cart'}, status=400)