from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('success', views.payment_success, name='payment_success'),
    path('failed', views.payment_failed, name='payment_failed'),
    path('checkout', views.checkout, name= 'checkout'),
    path('complete_order', views.complete_order, name= 'complete_order'),
    path('track_orders', views.track_orders, name='track_orders'),

]