import json
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


def get_breadcrumbs_jsonld(breadcrumbs, request=None):
    """
    Генерирует JSON-LD разметку schema.org для хлебных крошек (SEO).

    Args:
        breadcrumbs: Список словарей хлебных крошек из get_breadcrumbs()
        request: HTTP-запрос (для построения абсолютных URL)

    Returns:
        str: JSON-LD строка для вставки в <script type="application/ld+json">
    """
    if not breadcrumbs:
        return ""

    items = []
    # Добавляем "Главная" как первый элемент если breadcrumbs не начинаются с неё
    home_url = "/"
    try:
        home_url = reverse("main:index")
    except Exception:
        pass

    # Абсолютный URL для главной
    if request:
        base = f"{request.scheme}://{request.get_host()}"
    else:
        base = ""

    # Позиция 1 — главная страница (всегда)
    items.append({
        "@type": "ListItem",
        "position": 1,
        "name": "Главная",
        "item": base + home_url,
    })

    # Остальные крошки
    position = 2
    for crumb in breadcrumbs:
        title = crumb.get("title", "")
        url = crumb.get("url", "")
        if title and title != "Главная":
            item = {
                "@type": "ListItem",
                "position": position,
                "name": title,
            }
            if url and url != "#" and url is not None:
                item["item"] = base + url if url.startswith("/") else url
            items.append(item)
            position += 1

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
    return json.dumps(schema, ensure_ascii=False)
