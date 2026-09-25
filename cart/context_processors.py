# cart/context_processors.py
from asgiref.sync import sync_to_async
import asyncio
from .cart import Cart

def cart(request):
    """Safely initializes the user cart across both sync and async request lifecycles."""
    try:
        # Try standard synchronous initialization first
        return {"cart": Cart(request)}
    except RuntimeError:
        # Fallback if Daphne's active loop blocks direct session database access
        get_cart = sync_to_async(lambda: Cart(request), thread_sensitive=True)
        # Force evaluation inside a safe background worker thread
        return {"cart": asyncio.run(get_cart())}
