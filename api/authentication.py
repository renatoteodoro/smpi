from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    """DRF authentication backend that validates the X-Api-Key header.

    Returns (user, api_key_instance) so views can inspect which key was used.
    Updates last_used_at on each successful authentication.
    """

    def authenticate(self, request):
        key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        if not key:
            return None
        try:
            api_key = ApiKey.objects.select_related('user').get(key=key, is_active=True)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed('API key inválida ou inativa.')
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])
        return (api_key.user, api_key)
