from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Service
from .cart import Cart

@require_POST
@login_required
def cart_add(request, service_id):
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    if service.can_order:
        cart.add(service=service)
    return redirect(request.META.get('HTTP_REFERER', 'services:list'))

@login_required
def cart_remove(request, service_id):
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    cart.remove(service)
    return redirect(request.META.get('HTTP_REFERER', 'services:list'))

@login_required
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect(request.META.get('HTTP_REFERER', 'services:list'))
