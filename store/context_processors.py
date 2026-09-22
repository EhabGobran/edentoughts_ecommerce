# store/context_processors.py
import asyncio
from django.core.cache import cache
from asgiref.sync import async_to_sync
from .models import Category

def global_categories(request):
    """Safe context processor to load categories across both sync and async pipelines."""
    is_async = False
    try:
        asyncio.get_running_loop()
        is_async = True
    except RuntimeError:
        pass

    if is_async:
        # 1. Async safe pipeline
        category_list = async_to_sync(cache.aget)('global_categories')
        if category_list is None:
            # Safely fetch database rows via an async closure execution
            def fetch_db_list():
                return list(Category.objects.all())
            category_list = async_to_sync(fetch_db_list)()
            async_to_sync(cache.aset)('global_categories', category_list, timeout=None)
    else:
        # 2. Standard synchronous fallback pipeline
        category_list = cache.get('global_categories')
        if category_list is None:
            category_list = list(Category.objects.all())
            cache.set('global_categories', category_list, timeout=None)

    return {"category_list": category_list}
