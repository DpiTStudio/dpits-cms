from django import template

register = template.Library()

@register.simple_tag
def get_hero_bg_url(active_hero=None, category=None, app_hero=None, site_settings=None):
    """
    Определяет фоновое изображение для hero-секции.
    Возвращает URL изображения или пустую строку, если нужно использовать градиент.
    """
    if active_hero:
        if getattr(active_hero, 'hero_image', None):
            return active_hero.hero_image.url
        if getattr(active_hero, 'image', None):
            return active_hero.image.url
        if getattr(active_hero, 'background', None):
            return active_hero.background.url
            
    if category:
        if getattr(category, 'hero_image', None):
            return category.hero_image.url
        if getattr(category, 'image', None):
            return category.image.url
        if getattr(category, 'background', None):
            return category.background.url
            
    if app_hero:
        if getattr(app_hero, 'hero_image', None):
            return app_hero.hero_image.url
        if getattr(app_hero, 'image', None):
            return app_hero.image.url
        if getattr(app_hero, 'background', None):
            return app_hero.background.url
            
    if site_settings and getattr(site_settings, 'hero_background', None):
        return site_settings.hero_background.url
        
    return ""

@register.simple_tag
def get_hero_settings(active_hero=None, category=None, app_hero=None, site_settings=None):
    """
    Разрешает настройки фонового оформления для Hero-секции.
    Возвращает словарь с параметрами:
    - bg_type: 'image', 'gradient', 'cosmic', 'solid'
    - bg_style: готовый CSS-стиль для background/background-color
    - show_particles: True / False
    - overlay_gradient: градиент для оверлея
    - blur_amount: размытие в px
    """
    # 1. Глобальные значения по умолчанию
    resolved = {
        'bg_type': 'gradient',
        'bg_value': 'linear-gradient(135deg, var(--primary-color) 0%, #1e3c72 100%)',
        'show_particles': True,
        'overlay_opacity': 0.85,
        'blur_amount': 4,
        'image_url': None
    }

    # Сначала считываем глобальные настройки из site_settings
    if site_settings:
        resolved['bg_type'] = getattr(site_settings, 'hero_bg_type', 'image')
        resolved['bg_value'] = getattr(site_settings, 'hero_bg_gradient', '') or 'linear-gradient(135deg, var(--primary-color) 0%, #1e3c72 100%)'
        resolved['show_particles'] = getattr(site_settings, 'hero_show_particles', True)
        resolved['overlay_opacity'] = getattr(site_settings, 'hero_overlay_opacity', 0.85)
        resolved['blur_amount'] = getattr(site_settings, 'hero_blur_amount', 4)
        if getattr(site_settings, 'hero_background', None):
            resolved['image_url'] = site_settings.hero_background.url
            if resolved['bg_type'] == 'image':
                resolved['bg_value'] = f"url('{resolved['image_url']}') center/cover no-repeat"
        else:
            if resolved['bg_type'] == 'image':
                resolved['bg_type'] = 'gradient'
                resolved['bg_value'] = 'linear-gradient(135deg, var(--primary-color) 0%, #1e3c72 100%)'

    # 2. Ищем переопределяющие объекты в порядке приоритета: active_hero, category, app_hero
    override_obj = None
    if active_hero and hasattr(active_hero, 'hero_is_active'):
        override_obj = active_hero
    elif category and hasattr(category, 'hero_is_active'):
        override_obj = category
    elif app_hero and hasattr(app_hero, 'hero_is_active'):
        override_obj = app_hero

    if override_obj:
        # Проверяем тип фона страницы
        bg_type = getattr(override_obj, 'hero_bg_type', 'global')
        if bg_type != 'global':
            resolved['bg_type'] = bg_type

        # Проверяем отображение бликов/частиц
        show_particles = getattr(override_obj, 'hero_show_particles', 'global')
        if show_particles == 'yes':
            resolved['show_particles'] = True
        elif show_particles == 'no':
            resolved['show_particles'] = False

        # Разрешаем значение фона в зависимости от типа
        if resolved['bg_type'] == 'image':
            img_url = None
            if getattr(override_obj, 'hero_image', None):
                img_url = override_obj.hero_image.url
            elif getattr(override_obj, 'image', None):
                img_url = override_obj.image.url
            elif getattr(override_obj, 'background', None):
                img_url = override_obj.background.url

            if img_url:
                resolved['image_url'] = img_url
                resolved['bg_value'] = f"url('{img_url}') center/cover no-repeat"
            else:
                # Если на странице нет картинки, используем картинку из site_settings
                if resolved.get('image_url'):
                    resolved['bg_value'] = f"url('{resolved['image_url']}') center/cover no-repeat"
                else:
                    # Если вообще нет картинок, падаем в градиент
                    resolved['bg_type'] = 'gradient'
                    resolved['bg_value'] = 'linear-gradient(135deg, var(--primary-color) 0%, #1e3c72 100%)'

        elif resolved['bg_type'] == 'gradient':
            grad = getattr(override_obj, 'hero_bg_gradient', None)
            if grad:
                resolved['bg_value'] = grad
            else:
                if site_settings and getattr(site_settings, 'hero_bg_gradient', None):
                    resolved['bg_value'] = site_settings.hero_bg_gradient

        elif resolved['bg_type'] == 'solid':
            color = getattr(override_obj, 'hero_bg_color', None)
            if color:
                resolved['bg_value'] = color
            else:
                if site_settings and getattr(site_settings, 'hero_bg_color', None):
                    resolved['bg_value'] = site_settings.hero_bg_color

        elif resolved['bg_type'] == 'cosmic':
            resolved['bg_value'] = 'var(--gradient-mesh-cosmic)'

    # Формируем итоговые стили
    if resolved['bg_type'] == 'solid':
        resolved['bg_style'] = f"background-color: {resolved['bg_value']};"
    else:
        resolved['bg_style'] = f"background: {resolved['bg_value']};"

    # Вычисляем вторичную прозрачность для оверлея
    op1 = resolved['overlay_opacity']
    op2 = max(0.0, op1 - 0.25)
    resolved['overlay_gradient'] = f"linear-gradient(135deg, rgba(15, 23, 42, {op1}) 0%, rgba(30, 41, 59, {op2:.2f}) 100%)"

    return resolved
