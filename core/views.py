"""
Core views: landing page and root redirect.
"""

from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import NoReverseMatch, reverse


class LandingPageView(TemplateView):
    """
    Public landing page.
    Authenticated users are redirected to the main dashboard.
    """

    template_name = 'core/landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Root dashboard — redirects to the first available app dashboard.
    Falls back to rendering the placeholder template if no app URL exists yet.
    """

    template_name = 'core/dashboard.html'

    def get(self, request, *args, **kwargs):
        for url_name in ('analytics:dashboard', 'monitoring:reading_list'):
            try:
                return redirect(reverse(url_name))
            except NoReverseMatch:
                continue
        # No app URLs wired yet — render the placeholder template
        return super().get(request, *args, **kwargs)
