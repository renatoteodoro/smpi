import re

from django.conf import settings
from django.http import HttpResponseForbidden


class MediaProtectionMiddleware:
    """
    Blocks unauthenticated access to MEDIA_URL paths.

    In production, authenticated requests should be proxied through
    X-Accel-Redirect (nginx) for efficient file serving.
    In development (DEBUG=True), Django serves the file directly via
    the static() helper in urls.py — this middleware just enforces auth.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        media_url = settings.MEDIA_URL
        if media_url and media_url != '/' and request.path.startswith(media_url):
            if not request.user.is_authenticated:
                return HttpResponseForbidden('Acesso restrito.')
        return self.get_response(request)
