# mysite/main/admin_utils.py
from django.contrib import admin
from django.db import connection


class ResetAutoIncrementMixin:
    """
    Миксин для сброса автоинкремента в SQLite после удаления записей.
    """

    def delete_queryset(self, request, queryset):
        """
        Переопределяем метод удаления для сброса автоинкремента.
        """
        # Получаем модель
        model = self.model

        # Удаляем выбранные объекты
        super().delete_queryset(request, queryset)

        # Сбрасываем автоинкремент для SQLite
        if connection.vendor == 'sqlite':
            table_name = model._meta.db_table
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name = %s",
                    [table_name]
                )