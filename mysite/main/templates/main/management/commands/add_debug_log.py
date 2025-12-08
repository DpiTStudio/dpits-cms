# mysite/main/management/commands/add_debug_log.py
"""
Команда для добавления файла debug.log в управляемые файлы.
Позволяет автоматически добавить лог-файл в админку для управления.
"""
import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import ManagedFile


class Command(BaseCommand):
    """
    Команда Django для добавления файла debug.log в управляемые файлы.
    """
    
    help = 'Добавляет файл debug.log в управляемые файлы'
    
    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки.
        """
        parser.add_argument(
            '--path',
            type=str,
            help='Путь к файлу debug.log (по умолчанию: mysite/logs/debug.log)',
        )
    
    def handle(self, *args, **options):
        """
        Основной метод выполнения команды.
        """
        # Определяем путь к файлу
        if options['path']:
            log_path = options['path']
        else:
            # Путь по умолчанию: mysite/logs/debug.log
            log_path = os.path.join(settings.BASE_DIR, 'logs', 'debug.log')
        
        # Нормализуем путь (убираем лишние точки и слеши)
        log_path = os.path.normpath(log_path)
        
        self.stdout.write(f"Путь к файлу: {log_path}")
        
        # Создаем директорию, если ее нет
        log_dir = os.path.dirname(log_path)
        if not os.path.exists(log_dir):
            self.stdout.write(f"Создаю директорию: {log_dir}")
            os.makedirs(log_dir, exist_ok=True)
        
        # Создаем файл, если его нет
        if not os.path.exists(log_path):
            try:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write('# Лог-файл приложения\n')
                    f.write(f'# Создан: {self.get_current_time()}\n')
                    f.write(f'# Путь: {log_path}\n')
                    f.write('\n')
                
                self.stdout.write(self.style.SUCCESS(f'✅ Создан файл: {log_path}'))
                
                # Устанавливаем правильные права доступа
                try:
                    os.chmod(log_path, 0o644)  # rw-r--r--
                    self.stdout.write('✅ Установлены права доступа 644')
                except:
                    self.stdout.write(self.style.WARNING('⚠️ Не удалось установить права доступа'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка создания файла: {e}'))
                sys.exit(1)
        else:
            self.stdout.write(f'✅ Файл уже существует: {log_path}')
            
            # Проверяем права доступа
            try:
                stat_info = os.stat(log_path)
                self.stdout.write(f'✅ Права доступа: {oct(stat_info.st_mode)[-3:]}')
            except:
                self.stdout.write(self.style.WARNING('⚠️ Не удалось проверить права доступа'))
        
        # Проверяем, не добавлен ли уже файл
        if not ManagedFile.objects.filter(file_path=log_path).exists():
            try:
                # Создаем объект ManagedFile
                managed_file = ManagedFile(
                    name='debug.log',
                    file_path=log_path,
                    category='log',
                    description='Лог-файл отладки приложения. Автоматически добавлен командой add_debug_log.',
                    is_active=True,
                    auto_backup=True,
                    max_backups=10,
                    encoding='utf-8'
                )
                
                # Сохраняем объект
                managed_file.save()
                
                # Обновляем информацию о файле
                success, message = managed_file.refresh_file_info()
                if success:
                    self.stdout.write(self.style.SUCCESS(f'✅ {message}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️ {message}'))
                
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Файл {log_path} успешно добавлен в управляемые файлы'
                ))
                self.stdout.write(self.style.SUCCESS(
                    f'✅ ID записи: {managed_file.pk}'
                ))
                
                # Показываем информацию о добавленном файле
                self.stdout.write('\n' + '='*50)
                self.stdout.write('ИНФОРМАЦИЯ О ДОБАВЛЕННОМ ФАЙЛЕ:')
                self.stdout.write('='*50)
                self.stdout.write(f'Имя: {managed_file.name}')
                self.stdout.write(f'Путь: {managed_file.file_path}')
                self.stdout.write(f'Категория: {managed_file.get_category_display()}')
                self.stdout.write(f'Размер: {managed_file.human_readable_size}')
                self.stdout.write(f'Существует на диске: {"Да" if managed_file.exists else "Нет"}')
                self.stdout.write(f'Активен: {"Да" if managed_file.is_active else "Нет"}')
                self.stdout.write(f'Авто-бэкап: {"Включен" if managed_file.auto_backup else "Выключен"}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка при создании записи: {e}'))
                self.stdout.write(self.style.ERROR('Проверьте, что модель ManagedFile корректно определена'))
                sys.exit(1)
        else:
            existing_file = ManagedFile.objects.get(file_path=log_path)
            self.stdout.write(self.style.WARNING(
                f'⚠️ Файл уже добавлен в управляемые файлы (ID: {existing_file.pk})'
            ))
            
            # Обновляем информацию о существующем файле
            success, message = existing_file.refresh_file_info()
            if success:
                self.stdout.write(self.style.SUCCESS(f'✅ {message}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ {message}'))
    
    def get_current_time(self):
        """
        Возвращает текущее время в формате строки.
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')