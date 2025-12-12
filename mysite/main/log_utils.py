# log_utils.py (обновляем функцию get_log_file_path)
def get_log_file_path():
    """
    Получает путь к файлу debug.log.
    Проверяет стандартное расположение логов в Django проекте.

    Возвращает:
        str или None: Абсолютный путь к файлу debug.log или None при ошибке
    """
    # Вариант 1: Стандартный путь к логам в Django (BASE_DIR/logs)
    log_dir_standard = os.path.join(settings.BASE_DIR, "logs")

    # Вариант 2: Указанный вами путь (mysite/logs)
    # Если BASE_DIR это 'mysite', то это то же самое что вариант 1
    # Если нет, можно указать явный путь:
    log_dir_custom = os.path.join("mysite", "logs")

    # Проверяем, какой путь существует
    log_dir = None
    if os.path.exists(log_dir_standard):
        log_dir = log_dir_standard
    elif os.path.exists(log_dir_custom):
        log_dir = log_dir_custom
    else:
        # Если ни один путь не существует, пробуем создать стандартный
        log_dir = log_dir_standard

    # Создаем директорию, если она не существует
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Создана директория логов: {log_dir}")
        except Exception as e:
            logger.error(f"Ошибка создания директории логов: {e}")
            return None

    log_file = os.path.join(log_dir, "debug.log")

    # Проверяем, существует ли файл
    if not os.path.exists(log_file):
        logger.info(f"Лог-файл не существует: {log_file}")
        # Создаем пустой файл, если его нет
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(
                    f"Лог-файл создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
            logger.info(f"Создан пустой лог-файл: {log_file}")
        except Exception as e:
            logger.error(f"Ошибка создания лог-файла: {e}")
            return None

    return log_file
