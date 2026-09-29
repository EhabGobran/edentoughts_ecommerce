from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.http import HttpResponseNotAllowed

def store(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    products_list = Product.objects.all()
    return render(request, "store/store.html", context={"products_list": list(products_list)})

def product_info(request, product_slug):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    product = Product.objects.get(slug=product_slug)
    return render(request, "store/product-info.html", context={"product": product})

def list_category(request, category_slug):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    category = Category.objects.get(slug=category_slug)
    products = list(Product.objects.filter(category=category))
    return render(request, "store/list-category.html", context={"category": category, "products": products})
