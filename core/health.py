"""
Simple health check endpoint.
No authentication, no database queries — returns 200 immediately.
Used by load balancers and container orchestrators.
"""

from django.http import JsonResponse


def health_check(request):
    """Return HTTP 200 with a simple status payload."""
    return JsonResponse({'status': 'ok'}, status=200)
