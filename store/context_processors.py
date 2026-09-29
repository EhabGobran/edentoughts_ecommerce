# store/context_processors.py
from django.core.cache import cache
from .models import Category

def global_categories(request):
    category_list = cache.get('global_categories')

    if category_list is None:
        category_list = list(Category.objects.all())
        cache.set('global_categories', category_list, timeout=None)

    return {"category_list": category_list}