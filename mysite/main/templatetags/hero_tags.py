from django import template

register = template.Library()

@register.simple_tag
def get_hero_bg_url(active_hero=None, category=None, app_hero=None, site_settings=None):
    """
    Определяет фоновое изображение для hero-секции с поддержкой иерархии:
    active_hero -> category -> app_hero -> site_settings.
    """
    chain = []
    for obj in [active_hero, category, app_hero]:
        if obj and hasattr(obj, 'hero_is_active') and obj not in chain:
            chain.append(obj)

    for obj in chain:
        if getattr(obj, 'hero_image', None):
            return obj.hero_image.url
        if getattr(obj, 'image', None):
            name = obj.image.name
            if name and 'default-category' not in name:
                return obj.image.url
        if getattr(obj, 'background', None):
            return obj.background.url

    if site_settings and getattr(site_settings, 'hero_background', None):
        return site_settings.hero_background.url

    return ""

@register.simple_tag
def get_hero_settings(active_hero=None, category=None, app_hero=None, site_settings=None):
    """
    Разрешает настройки фонового оформления для Hero-секции с поддержкой
    иерархического наследования: active_hero -> category -> app_hero -> site_settings.
    Возвращает словарь с параметрами:
    - bg_type: 'image', 'gradient', 'cosmic', 'solid'
    - bg_style: готовый CSS-стиль для background/background-color
    - show_particles: True / False
    - overlay_gradient: градиент для оверлея
    - blur_amount: размытие в px
    - hero_is_active: True / False
    """
    # 1. Глобальные значения по умолчанию
    resolved = {
        'bg_type': 'gradient',
        'bg_value': 'linear-gradient(135deg, var(--primary-color) 0%, #1e3c72 100%)',
        'show_particles': True,
        'overlay_opacity': 0.85,
        'blur_amount': 4,
        'image_url': None,
        'hero_is_active': True,
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

    # Строим цепочку наследования по приоритету
    chain = []
    for obj in [active_hero, category, app_hero]:
        if obj and hasattr(obj, 'hero_is_active') and obj not in chain:
            chain.append(obj)

    # Разрешаем активность Hero (если хоть один уровень отключает - отключаем)
    hero_is_active = True
    for obj in chain:
        if getattr(obj, 'hero_is_active', True) is False:
            hero_is_active = False
            break
    resolved['hero_is_active'] = hero_is_active

    if chain:
        # Разрешаем bg_type по иерархии
        bg_type = 'global'
        for obj in chain:
            val = getattr(obj, 'hero_bg_type', 'global')
            if val != 'global':
                bg_type = val
                break
        if bg_type != 'global':
            resolved['bg_type'] = bg_type

        # Разрешаем show_particles по иерархии
        show_particles = 'global'
        for obj in chain:
            val = getattr(obj, 'hero_show_particles', 'global')
            if val != 'global':
                show_particles = val
                break
        if show_particles == 'yes':
            resolved['show_particles'] = True
        elif show_particles == 'no':
            resolved['show_particles'] = False

        # Разрешаем значение фона (bg_value) в зависимости от разрешенного bg_type
        if resolved['bg_type'] == 'solid':
            # Ищем цвет фона в иерархии
            bg_color = None
            for obj in chain:
                val = getattr(obj, 'hero_bg_color', None)
                if val:
                    bg_color = val
                    break
            if bg_color:
                resolved['bg_value'] = bg_color
            else:
                if site_settings and getattr(site_settings, 'hero_bg_color', None):
                    resolved['bg_value'] = site_settings.hero_bg_color

        elif resolved['bg_type'] == 'gradient':
            # Ищем градиент в иерархии
            bg_gradient = None
            for obj in chain:
                val = getattr(obj, 'hero_bg_gradient', None)
                if val:
                    bg_gradient = val
                    break
            if bg_gradient:
                resolved['bg_value'] = bg_gradient
            else:
                if site_settings and getattr(site_settings, 'hero_bg_gradient', None):
                    resolved['bg_value'] = site_settings.hero_bg_gradient

        elif resolved['bg_type'] == 'image':
            # Ищем изображение в иерархии
            img_url = None
            for obj in chain:
                if getattr(obj, 'hero_image', None):
                    img_url = obj.hero_image.url
                    break
                elif getattr(obj, 'image', None):
                    name = obj.image.name
                    if name and 'default-category' not in name:
                        img_url = obj.image.url
                        break
                elif getattr(obj, 'background', None):
                    img_url = obj.background.url
                    break

            if img_url:
                resolved['image_url'] = img_url
                resolved['bg_value'] = f"url('{img_url}') center/cover no-repeat"
            else:
                # Если изображение не найдено, пытаемся использовать глобальное
                if site_settings and getattr(site_settings, 'hero_background', None):
                    img_url = site_settings.hero_background.url
                    resolved['image_url'] = img_url
                    resolved['bg_value'] = f"url('{img_url}') center/cover no-repeat"
                else:
                    # Если вообще нет картинок, падаем в градиент
                    resolved['bg_type'] = 'gradient'
                    # Ищем первый доступный градиент в иерархии
                    grad_val = None
                    for obj in chain:
                        if getattr(obj, 'hero_bg_gradient', None):
                            grad_val = obj.hero_bg_gradient
                            break
                    if not grad_val and site_settings:
                        grad_val = getattr(site_settings, 'hero_bg_gradient', None)
                    resolved['bg_value'] = grad_val or 'linear-gradient(135deg, var(--primary-color) 0%, #1e3c72 100%)'

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
