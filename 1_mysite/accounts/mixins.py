# accounts/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class TicketAccessMixin(LoginRequiredMixin):
    """
    Миксин для проверки доступа к тикетам
    """

    def dispatch(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.can_user_access(request.user):
            raise PermissionDenied("У вас нет доступа к этому тикету")
        return super().dispatch(request, *args, **kwargs)
