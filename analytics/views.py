from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from monitoring.models import SensorReading
        from prescriptions.models import Prescription
        from assets.models import Equipment

        ctx['total_readings'] = SensorReading.objects.count()
        ctx['problem_count'] = SensorReading.objects.filter(status_class='problem').count()
        ctx['state_count'] = SensorReading.objects.filter(status_class='state').count()
        ctx['pending_count'] = SensorReading.objects.filter(status_class='pending').count()
        ctx['total_prescriptions'] = Prescription.objects.count()
        ctx['grounded_count'] = Prescription.objects.filter(is_grounded=True).count()
        ctx['equipment_count'] = Equipment.objects.filter(status='active').count()
        return ctx


class DashboardDataView(LoginRequiredMixin, View):
    """JSON endpoint for Chart.js — readings per day (last 30 days) and fault distribution."""

    def get(self, request):
        from monitoring.models import SensorReading
        from django.utils import timezone
        import datetime

        since = timezone.now() - datetime.timedelta(days=30)

        readings_by_day = list(
            SensorReading.objects.filter(event_created_at__gte=since, event_created_at__isnull=False)
            .annotate(day=TruncDay('event_created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        fault_dist = list(
            SensorReading.objects.filter(status_class='problem', fault__isnull=False)
            .values('fault__code')
            .annotate(count=Count('id'))
            .order_by('-count')[:15]
        )

        return JsonResponse({
            'readings_by_day': [
                {'day': r['day'].strftime('%d/%m'), 'count': r['count']}
                for r in readings_by_day
            ],
            'fault_distribution': [
                {'fault': f['fault__code'], 'count': f['count']}
                for f in fault_dist
            ],
        })
