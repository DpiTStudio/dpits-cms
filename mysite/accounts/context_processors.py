# accounts/context_processors.py
from django.conf import settings


def site_settings(request):
    """
    Контекстный процессор для настроек сайта
    """
    return {
        "site_settings": {
            "logo_text": getattr(settings, "SITE_NAME", "DPITS-CMS.RU"),
            "support_email": getattr(settings, "SUPPORT_EMAIL", "admin@dpitst-cms.ru"),
        }
    }
