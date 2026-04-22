# services/urls.py
# Назначение: Маршруты (URL-адреса) приложения "Услуги".
# Определяет, какие функции-обработчики вызывать для каждого URL.

from django.urls import path, include
from django.shortcuts import redirect
from . import views, cart_views

app_name = 'services'  # Пространство имён для обратного резолвинга URL ({% url 'services:list' %})

urlpatterns = [
    # Главная страница услуг (список всех услуг и категорий)
    path('', views.service_list, name='list'),
    
    # Оформление заказа (страница корзины)
    path('checkout/', views.checkout, name='checkout'),
    
    # Страница успешного оформления заказа
    path('order/<int:pk>/success/', views.order_success, name='order_success'),
    
    # Страница категории услуг (фильтр по категории)
    path('category/<slug:slug>/', views.service_category, name='category'),
    
    # Детальная страница услуги (ВНИМАНИЕ: этот маршрут должен быть ПОСЛЕ 'category/' и 'checkout/',
    # иначе он перехватит URL типа 'category/...' как slug услуги)
    path('<slug:service_slug>/', views.service_detail, name='detail'),  # ИСПРАВЛЕНО: переименован параметр
    
    # === AJAX-маршруты для корзины ===
    path('cart/add/<int:service_id>/', cart_views.cart_add, name='cart_add'),
    path('cart/remove/<int:service_id>/', cart_views.cart_remove, name='cart_remove'),
    path('cart/clear/', cart_views.cart_clear, name='cart_clear'),
    path('cart/detail/', cart_views.cart_detail, name='cart_detail'),
]