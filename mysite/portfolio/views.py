# portfolio/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
from .forms import *

def portfolio_list(request):
    """Список работ портфолио"""
    portfolio_items = PortfolioItem.objects.filter(status='published').order_by('-project_date')
    categories = PortfolioCategory.objects.filter(is_active=True)
    
    # Фильтрация по категории
    category_slug = request.GET.get('category')
    if category_slug:
        portfolio_items = portfolio_items.filter(category__slug=category_slug)
    
    # Поиск
    search_query = request.GET.get('q')
    if search_query:
        portfolio_items = portfolio_items.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(technologies__icontains=search_query)
        )
    
    paginator = Paginator(portfolio_items, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'portfolio_items': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query or '',
    }
    return render(request, 'portfolio/list.html', context)

def portfolio_detail(request, slug):
    """Детальная страница работы"""
    item = get_object_or_404(PortfolioItem, slug=slug, status='published')
    item.views += 1
    item.save(update_fields=['views'])
    
    # Похожие работы
    similar_items = PortfolioItem.objects.filter(
        category=item.category, status='published'
    ).exclude(id=item.id).order_by('-views')[:4]
    
    # Отзывы для этой работы
    reviews = Review.objects.filter(portfolio_item=item, is_approved=True)
    
    context = {
        'item': item,
        'similar_items': similar_items,
        'reviews': reviews,
    }
    return render(request, 'portfolio/detail.html', context)

@login_required
def client_dashboard(request):
    """Личный кабинет клиента"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        # Если клиент не существует, создаем его
        client = Client.objects.create(user=request.user)
    
    orders = Order.objects.filter(client=client).order_by('-created_at')
    reviews = Review.objects.filter(client=client)
    
    # Статистика
    orders_count = orders.count()
    completed_orders = orders.filter(status='completed').count()
    active_orders = orders.exclude(status__in=['completed', 'cancelled']).count()
    
    context = {
        'client': client,
        'orders': orders[:5],  # Последние 5 заказов
        'reviews': reviews[:3],  # Последние 3 отзыва
        'orders_count': orders_count,
        'completed_orders': completed_orders,
        'active_orders': active_orders,
    }
    return render(request, 'portfolio/client_dashboard.html', context)

@login_required
def create_order(request):
    """Создание нового заказа"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        client = Client.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = client
            order.save()
            
            messages.success(request, 'Заказ успешно создан! Мы свяжемся с вами в ближайшее время.')
            return redirect('portfolio:order_detail', pk=order.pk)
    else:
        form = OrderForm()
    
    context = {'form': form}
    return render(request, 'portfolio/create_order.html', context)

@login_required
def order_detail(request, pk):
    """Детальная страница заказа"""
    order = get_object_or_404(Order, pk=pk)
    
    # Проверяем, что пользователь имеет доступ к заказу
    if order.client.user != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этому заказу.')
        return redirect('portfolio:client_dashboard')
    
    if request.method == 'POST':
        form = OrderMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.order = order
            message.user = request.user
            message.is_admin_message = request.user.is_staff
            message.save()
            
            # Обновляем статус заказа если отвечает клиент
            if not request.user.is_staff and order.status == 'new':
                order.status = 'in_progress'
                order.save()
            
            messages.success(request, 'Сообщение отправлено!')
            return redirect('portfolio:order_detail', pk=order.pk)
    else:
        form = OrderMessageForm()
    
    messages_list = order.messages.all().order_by('created_at')
    
    context = {
        'order': order,
        'messages': messages_list,
        'form': form,
    }
    return render(request, 'portfolio/order_detail.html', context)

@login_required
def order_list(request):
    """Список заказов клиента"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        client = Client.objects.create(user=request.user)
    
    orders = Order.objects.filter(client=client).order_by('-created_at')
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'status_filter': status_filter or '',
    }
    return render(request, 'portfolio/order_list.html', context)

@login_required
def create_review(request, item_slug):
    """Создание отзыва для работы"""
    portfolio_item = get_object_or_404(PortfolioItem, slug=item_slug)
    client = get_object_or_404(Client, user=request.user)
    
    # Проверяем, есть ли уже отзыв от этого клиента
    existing_review = Review.objects.filter(client=client, portfolio_item=portfolio_item).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = client
            review.portfolio_item = portfolio_item
            review.save()
            
            messages.success(request, 'Отзыв успешно отправлен! Он будет опубликован после проверки.')
            return redirect('portfolio:detail', slug=item_slug)
    else:
        if existing_review:
            form = ReviewForm(instance=existing_review)
        else:
            form = ReviewForm(initial={'portfolio_item': portfolio_item})
    
    context = {
        'form': form,
        'portfolio_item': portfolio_item,
        'existing_review': existing_review,
    }
    return render(request, 'portfolio/create_review.html', context)

@login_required
def client_profile(request):
    """Редактирование профиля клиента"""
    client = get_object_or_404(Client, user=request.user)
    
    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('portfolio:client_dashboard')
    else:
        form = ClientProfileForm(instance=client)
    
    context = {'form': form, 'client': client}
    return render(request, 'portfolio/client_profile.html', context)