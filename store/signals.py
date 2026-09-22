from django.db.models.signals import post_delete , post_save 
from django.dispatch import receiver
from .models import Category
from django.core.cache import cache

@receiver(post_delete , sender= Category)
@receiver(post_save , sender= Category)
def clear_category_cache(sender ,instance ,**kwargs):
    cache.clear("global_categories")
