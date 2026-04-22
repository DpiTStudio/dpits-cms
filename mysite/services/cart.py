# services/cart.py
# Назначение: Класс корзины для хранения выбранных услуг в сессии пользователя.
# Поддерживает добавление, удаление, очистку, подсчёт суммы и количества.

from decimal import Decimal
from .models import Service


class Cart:
    """
    Класс корзины услуг.
    Хранит данные в сессии Django (request.session).
    """

    def __init__(self, request):
        """
        Инициализация корзины.
        Загружает корзину из сессии или создаёт новую.
        """
        self.session = request.session
        cart = self.session.get('cart')  # Пытаемся получить корзину из сессии
        if not cart:
            # Если корзины нет, создаём пустой словарь
            cart = self.session['cart'] = {}
        self.cart = cart  # Привязываем к атрибуту объекта

    def add(self, service):
        """
        Добавляет услугу в корзину.
        Определяет цену в зависимости от типа цены услуги (фикс, от, до, диапазон).
        """
        product_id = str(service.id)  # Ключом в словаре будет ID услуги (как строка)
        
        if product_id not in self.cart:
            # Определение цены для отображения в корзине
            price = 0
            if service.price_type == 'fixed' and service.price_fixed:
                price = service.price_fixed
            elif service.price_type == 'from' and service.price_from:
                price = service.price_from
            elif service.price_type == 'to' and service.price_to:
                price = service.price_to
            elif service.price_type == 'range' and service.price_from:
                price = service.price_from
            
            # Получаем URL иконки с проверкой на существование файла
            icon_url = ''
            if service.icon and hasattr(service.icon, 'url') and service.icon.url:
                icon_url = service.icon.url
            
            self.cart[product_id] = {
                'name': service.name,
                'price': str(price),          # Цена хранится как строка для сериализации в JSON
                'quantity': 1,                # Количество (всегда 1 для услуг)
                'url': service.get_absolute_url(),
                'icon': icon_url,
            }
        self.save()  # Сохраняем изменения в сессии

    def remove(self, service):
        """
        Удаляет услугу из корзины по ID.
        """
        product_id = str(service.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """
        Сохраняет изменения в сессии.
        Устанавливает флаг modified = True, чтобы Django понял, что сессия изменилась.
        """
        self.session.modified = True

    def __iter__(self):
        """
        Итератор по элементам корзины.
        Загружает объекты услуг из БД и добавляет их к данным из сессии.
        """
        product_ids = self.cart.keys()
        # Получаем все услуги, которые есть в корзине, одним запросом
        services = Service.objects.filter(id__in=product_ids)
        
        # Создаём словарь {id: объект_услуги} для быстрого доступа
        services_dict = {str(s.id): s for s in services}
        
        for product_id, item_data in self.cart.items():
            item = item_data.copy()
            # Преобразуем цену из строки в Decimal для математических операций
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            
            # Добавляем объект услуги в элемент
            item['service'] = services_dict.get(product_id)
            yield item

    def __len__(self):
        """
        Возвращает общее количество услуг в корзине (сумму количеств).
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Вычисляет общую стоимость всех услуг в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Полностью очищает корзину (удаляет ключ 'cart' из сессии).
        """
        if 'cart' in self.session:
            del self.session['cart']
        self.save()