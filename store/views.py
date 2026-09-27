from django.shortcuts import render , get_object_or_404
from django.core.cache import cache
from django.views.decorators.http import require_safe
from asgiref.sync import sync_to_async
from .models import Category , Product


# Create your views here.
@require_safe
def store(request):
    products_list = Product.objects.all()
    return render(request ,"store/store.html" , context= {"products_list" :list(products_list)})


@require_safe
async def category(request):
    category_list = await cache.aget('global_categories')
    if category_list is None:
        category_list = Category.objects.all()
        await cache.aset('global_categories',list(category_list),timeout= None)

    return {"category_list" : category_list}

@require_safe
async def product_info(request , product_slug):
    product= await Product.objects.aget(slug= product_slug)
    return render(request ,"store/product-info.html", context= {"product": product})

@require_safe
async def list_category(request, category_slug):
    category= await Category.objects.aget(slug= category_slug)
    products= Product.objects.filter(category= category)
    products = [product async for product in products]
    return render(request, "store/list-category.html", context={"category": category, "products":products})
