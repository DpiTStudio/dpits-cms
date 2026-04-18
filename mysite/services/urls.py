from django.urls import path, include
from django.shortcuts import redirect
from . import views, cart_views

app_name = 'services'


urlpatterns = [
    path('', views.service_list, name='list'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:pk>/success/', views.order_success, name='order_success'),
    path('category/<slug:slug>/', views.service_category, name='category'),
    path('<slug:slug>/', views.service_detail, name='detail'),
    path('cart/add/<int:service_id>/', cart_views.cart_add, name='cart_add'),
    path('cart/remove/<int:service_id>/', cart_views.cart_remove, name='cart_remove'),
    path('cart/clear/', cart_views.cart_clear, name='cart_clear'),
    path('cart/detail/', cart_views.cart_detail, name='cart_detail'),
]
