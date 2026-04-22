# services/cart_views.py
# Назначение: Обработчики AJAX-запросов для работы с корзиной.
# Добавление, удаление, очистка, получение данных корзины.

import json
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Service
from .cart import Cart


def _cart_json_response(request, cart, status='ok', message=''):
    """
    Вспомогательная функция: формирует JSON-ответ с полными данными корзины.
    Используется для AJAX-запросов.
    """
    items = []
    for item in cart:
        items.append({
            'id': item['service'].id if 'service' in item and item['service'] else None,
            'name': item['name'],
            'price': str(item['price']),
            'quantity': item['quantity'],
            'total_price': str(item['total_price']),
            'icon': item.get('icon', ''),
            'url': item.get('url', ''),
        })
    return JsonResponse({
        'status': status,           # 'ok', 'added', 'removed', 'cleared'
        'message': message,         # Текстовое сообщение для пользователя
        'count': len(cart),         # Количество позиций
        'total': str(cart.get_total_price()),  # Общая сумма
        'items': items,             # Список позиций
    })


@require_POST  # Только POST-запросы (для защиты от CSRF)
@login_required  # Только авторизованные пользователи
def cart_add(request, service_id):
    """
    Добавляет услугу в корзину.
    Поддерживает обычные и AJAX-запросы.
    """
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if service.can_order:
        cart.add(service=service)
        if is_ajax:
            return _cart_json_response(request, cart, 'added', f'«{service.name}» добавлено в корзину')
    else:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Услуга недоступна для заказа'}, status=400)

    # Для обычных (не AJAX) запросов возвращаемся на предыдущую страницу
    return redirect(request.META.get('HTTP_REFERER', 'services:list'))


@login_required
def cart_remove(request, service_id):
    """
    Удаляет услугу из корзины.
    """
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    cart.remove(service)

    if is_ajax:
        return _cart_json_response(request, cart, 'removed', f'«{service.name}» удалено из корзины')

    return redirect(request.META.get('HTTP_REFERER', 'services:list'))


@login_required
def cart_clear(request):
    """
    Полностью очищает корзину.
    """
    cart = Cart(request)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    cart.clear()

    if is_ajax:
        return JsonResponse({
            'status': 'cleared',
            'message': 'Корзина очищена',
            'count': 0,
            'total': '0',
            'items': []
        })

    return redirect(request.META.get('HTTP_REFERER', 'services:list'))


@login_required
def cart_detail(request):
    """
    AJAX-эндпоинт для получения текущего состояния корзины.
    Используется для обновления виджета корзины на странице.
    """
    cart = Cart(request)
    return _cart_json_response(request, cart)