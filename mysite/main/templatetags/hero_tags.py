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
