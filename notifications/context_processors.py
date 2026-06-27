from .models import Notification


def unread_notifications(request):
    """Inject unread notifications into every template context.

    Returns an empty structure for anonymous users to avoid DB queries.
    """
    if request.user.is_authenticated:
        qs = Notification.objects.filter(user=request.user, is_read=False)
        return {
            'unread_notifications': qs[:10],
            'unread_count': qs.count(),
        }
    return {'unread_notifications': [], 'unread_count': 0}
