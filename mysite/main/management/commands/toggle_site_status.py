"""
Команда управления Django для изменения статуса сайта (открыт/закрыт)

Использование:
    python manage.py toggle_site_status         # Переключить статус
    python manage.py toggle_site_status --open  # Открыть сайт
    python manage.py toggle_site_status --close # Закрыть сайт
    python manage.py toggle_site_status --status # Показать текущий статус
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from main.models import SiteSettings


class Command(BaseCommand):
    help = 'Управление статусом сайта (открыт/закрыт)'

    def add_arguments(self, parser):
        """Добавляем аргументы командной строки"""
        parser.add_argument(
            '--open',
            action='store_true',
            help='Открыть сайт для всех пользователей',
        )
        parser.add_argument(
            '--close',
            action='store_true',
            help='Закрыть сайт (показывать страницу обслуживания)',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Показать текущий статус сайта',
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Сообщение для отображения при закрытии сайта',
        )

    def handle(self, *args, **options):
        """Основная логика команды"""
        site_settings = SiteSettings.load()

        # Показать текущий статус
        if options['status']:
            self.show_status(site_settings)
            return

        # Открыть сайт
        if options['open']:
            site_settings.site_closed = False
            site_settings.save()
            cache.clear()  # Очищаем весь кэш
            self.stdout.write(
                self.style.SUCCESS('✓ Сайт успешно ОТКРЫТ для всех пользователей')
            )
            self.show_status(site_settings)
            return

        # Закрыть сайт
        if options['close']:
            message = options.get('message')
            if message:
                site_settings.closure_message = message
            elif not site_settings.closure_message:
                site_settings.closure_message = (
                    'Мы проводим плановые работы для улучшения вашего '
                    'пользовательского опыта. Совсем скоро всё заработает '
                    'в штатном режиме. Благодарим за терпение!'
                )
            
            site_settings.site_closed = True
            site_settings.save()
            cache.clear()  # Очищаем весь кэш
            self.stdout.write(
                self.style.WARNING('⚠ Сайт успешно ЗАКРЫТ (режим обслуживания)')
            )
            self.show_status(site_settings)
            return

        # Если не указаны флаги, переключаем статус
        site_settings.site_closed = not site_settings.site_closed
        
        if site_settings.site_closed and not site_settings.closure_message:
            site_settings.closure_message = (
                'Мы проводим плановые работы для улучшения вашего '
                'пользовательского опыта. Совсем скоро всё заработает '
                'в штатном режиме. Благодарим за терпение!'
            )
        
        site_settings.save()
        cache.clear()  # Очищаем весь кэш
        
        status_text = 'ЗАКРЫТ' if site_settings.site_closed else 'ОТКРЫТ'
        style = self.style.WARNING if site_settings.site_closed else self.style.SUCCESS
        self.stdout.write(
            style(f'✓ Статус сайта изменен на: {status_text}')
        )
        self.show_status(site_settings)

    def show_status(self, site_settings):
        """Показывает текущий статус сайта"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('ТЕКУЩИЙ СТАТУС САЙТА')
        self.stdout.write('=' * 60)
        
        if site_settings.site_closed:
            self.stdout.write(
                self.style.WARNING('Статус: ЗАКРЫТ (режим обслуживания)')
            )
            self.stdout.write(f'Сообщение: {site_settings.closure_message}')
            self.stdout.write('\nДоступ разрешен только для персонала (is_staff=True)')
        else:
            self.stdout.write(
                self.style.SUCCESS('Статус: ОТКРЫТ (работает нормально)')
            )
            self.stdout.write('Сайт доступен для всех пользователей')
        
        self.stdout.write('=' * 60)
        
        # Проверяем кэш
        cached_settings = cache.get('site_settings')
        if cached_settings:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ ВНИМАНИЕ: Настройки найдены в кэше '
                    f'(site_closed={cached_settings.site_closed})'
                )
            )
            self.stdout.write('Кэш будет очищен автоматически при сохранении')
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Настройки не закэшированы (актуальные данные)')
            )
        
        self.stdout.write('')
