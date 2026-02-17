from decimal import Decimal

from .models import Service

class Cart:
    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Сохраняем пустую корзину в сессии
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, service):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_id = str(service.id)
        if product_id not in self.cart:
            # Определение цены
            price = 0
            if service.price_type == 'fixed' and service.price_fixed:
                price = service.price_fixed
            elif service.price_type == 'from' and service.price_from:
                price = service.price_from
            elif service.price_type == 'to' and service.price_to:
                price = service.price_to
            elif service.price_type == 'range' and service.price_from:
                price = service.price_from
                
            self.cart[product_id] = {
                'name': service.name,
                'price': str(price),
                'quantity': 1,
                'url': service.get_absolute_url(),
                'icon': service.icon.url if service.icon else '',
            }
        self.save()

    def remove(self, service):
        """
        Удаление товара из корзины.
        """
        product_id = str(service.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        # Обновление сессии cart
        self.session.modified = True
        
    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.cart.keys()
        # Получаем объекты продуктов и добавляем их в корзину
        services = Service.objects.filter(id__in=product_ids)
        
        # Создаем копию корзины для итерации, чтобы можно было добавлять объекты service
        cart_copy = self.cart.copy()
        
        for service in services:
            cart_copy[str(service.id)]['service'] = service
            
        for item in cart_copy.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # удаление корзины из сессии
        del self.session['cart']
        self.save()
