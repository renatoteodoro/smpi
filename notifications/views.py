from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
@require_POST
def mark_read(request, pk):
    """Mark a single notification as read (scoped to the current user)."""
    Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def mark_all_read(request):
    """Mark all unread notifications as read for the current user."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})
