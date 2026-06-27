from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin):
    """Allow access only to users with role='admin'."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'admin':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MaintenanceRequiredMixin(LoginRequiredMixin):
    """Allow access to users with role='admin' or role='maintenance'."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in ('admin', 'maintenance'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
