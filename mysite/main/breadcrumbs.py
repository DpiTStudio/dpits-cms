from django.urls import reverse

def get_breadcrumbs(items=None):
    """
    Генерирует список хлебных крошек.
    
    Args:
        items: Список кортежей (title, url, icon) или словарей {'title': ..., 'url': ..., 'icon': ...}
        
    Returns:
        list: Список словарей с хлебными крошками
    """
    breadcrumbs = []
    
    if items:
        for item in items:
            if isinstance(item, (list, tuple)):
                crumb = {
                    'title': item[0],
                    'url': item[1] if len(item) > 1 else '#',
                    'icon': item[2] if len(item) > 2 else None
                }
            else:
                crumb = item
            breadcrumbs.append(crumb)
            
    return breadcrumbs
