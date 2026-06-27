"""
Root URL configuration for SMPI.
Uses try/except imports so development server works even before
all apps have their url modules created.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.health import health_check
from core.views import LandingPageView, DashboardView

urlpatterns = [
    # Health check — no auth, no DB
    path('health/', health_check, name='health'),

    # Django admin
    path('admin/', admin.site.urls),

    # Landing / dashboard
    path('', LandingPageView.as_view(), name='landing'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]

# ------------------------------------------------------------------
# App URLs — wrapped in try/except so the server starts even if
# an app's urls.py does not exist yet during early development.
# ------------------------------------------------------------------
try:
    from accounts import urls as accounts_urls  # noqa: F401
    urlpatterns += [path('accounts/', include('accounts.urls', namespace='accounts'))]
except ImportError:
    pass

try:
    from assets import urls as assets_urls  # noqa: F401
    urlpatterns += [path('equipment/', include('assets.urls', namespace='assets'))]
except ImportError:
    pass

try:
    from faults import urls as faults_urls  # noqa: F401
    urlpatterns += [path('faults/', include('faults.urls', namespace='faults'))]
except ImportError:
    pass

try:
    from monitoring import urls as monitoring_urls  # noqa: F401
    urlpatterns += [path('monitoring/', include('monitoring.urls', namespace='monitoring'))]
except ImportError:
    pass

try:
    from notifications import urls as notifications_urls  # noqa: F401
    urlpatterns += [path('notifications/', include('notifications.urls', namespace='notifications'))]
except ImportError:
    pass

try:
    from api import urls as api_urls  # noqa: F401
    urlpatterns += [path('api/v1/', include('api.urls', namespace='api'))]
except ImportError:
    pass

try:
    from knowledge import urls as knowledge_urls  # noqa: F401
    urlpatterns += [path('knowledge/', include('knowledge.urls', namespace='knowledge'))]
except ImportError:
    pass

try:
    from prescriptions import urls as prescriptions_urls  # noqa: F401
    urlpatterns += [path('prescriptions/', include('prescriptions.urls', namespace='prescriptions'))]
except ImportError:
    pass

try:
    from analytics import urls as analytics_urls  # noqa: F401
    urlpatterns += [path('analytics/', include('analytics.urls', namespace='analytics'))]
except ImportError:
    pass

try:
    from reports import urls as reports_urls  # noqa: F401
    urlpatterns += [path('reports/', include('reports.urls', namespace='reports'))]
except ImportError:
    pass

try:
    from ai import urls as ai_urls  # noqa: F401
    urlpatterns += [path('ai/', include('ai.urls', namespace='ai'))]
except ImportError:
    pass

try:
    from whatsapp import urls as whatsapp_urls  # noqa: F401
    urlpatterns += [path('webhooks/', include('whatsapp.urls', namespace='whatsapp'))]
except ImportError:
    pass

# drf-spectacular schema endpoints
try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
except ImportError:
    pass

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve built MkDocs documentation
import os
from django.views.static import serve as static_serve
from django.urls import re_path
from django.views.generic import RedirectView

_docs_site = os.path.join(settings.BASE_DIR, 'docs_site')
if os.path.isdir(_docs_site):
    def _serve_docs(request, path=''):
        if not path or path.endswith('/'):
            path = (path or '') + 'index.html'
        return static_serve(request, path, document_root=_docs_site)

    urlpatterns += [
        re_path(r'^docs/(?P<path>.*)$', _serve_docs, name='docs'),
    ]
