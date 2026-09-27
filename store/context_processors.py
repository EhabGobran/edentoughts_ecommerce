# store/context_processors.py
from django.core.cache import cache
from asgiref.sync import sync_to_async
from .models import Category

async def global_categories(request):
    category_list = await cache.aget('global_categories')

    if category_list is None:
        category_list = [c async for c in Category.objects.all()]
        await cache.aset('global_categories', category_list, timeout=None)

    return {"category_list": category_list}
