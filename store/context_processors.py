# store/context_processors.py
from django.core.cache import cache
from asgiref.sync import sync_to_async
from .models import Category

def global_categories(request):
    """
    Completely safe context processor. Uses native synchronous cache 
    and standard fallbacks which Django/Daphne handle seamlessly.
    """
    # 1. Look for the categories in the cache using the standard sync getter
    category_list = cache.get('global_categories')
    
    # 2. If the cache is empty, query the database safely
    if category_list is None:
        try:
            # Standard database query
            category_list = list(Category.objects.all())
        except RuntimeError:
            # Fallback if Daphne blocks a direct database evaluation on the thread loop
            fetch_db = sync_to_async(lambda: list(Category.objects.all()), thread_sensitive=True)
            import asyncio
            category_list = asyncio.run(fetch_db())
            
        # 3. Save the results back into the cache
        cache.set('global_categories', category_list, timeout=None)

    return {"category_list": category_list}
