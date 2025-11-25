# accounts/utils.py
import logging
from django.db import transaction

logger = logging.getLogger(__name__)


def get_user_statistics(user):
    """
    Получение статистики пользователя из различных приложений
    """
    stats = {"reviews_count": 0, "comments_count": 0, "tickets_count": 0}

    try:
        from reviews.models import Review

        stats["reviews_count"] = Review.objects.filter(author=user).count()
    except ImportError:
        logger.warning("Приложение reviews не найдено")

    try:
        from comments.models import Comment

        stats["comments_count"] = Comment.objects.filter(author=user).count()
    except ImportError:
        logger.warning("Приложение comments не найдено")

    return stats


def handle_form_submission(request, form_class, success_message, success_redirect):
    """
    Универсальная обработка отправки форм
    """
    try:
        with transaction.atomic():
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, success_message)
                return redirect(success_redirect)
            else:
                return form
    except Exception as e:
        logger.error(f"Ошибка при обработке формы: {e}")
        messages.error(request, "Произошла ошибка при обработке формы")
        return None
