from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import SensorReading
from .forms import ManualReadingForm


class ReadingListView(LoginRequiredMixin, ListView):
    model = SensorReading
    template_name = 'monitoring/reading_list.html'
    context_object_name = 'readings'
    paginate_by = 30

    def get_queryset(self):
        qs = SensorReading.objects.select_related(
            'fault', 'measurement_point__equipment'
        )
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status_class=status)
        equipment = self.request.GET.get('equipment')
        if equipment:
            qs = qs.filter(measurement_point__equipment_id=equipment)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_count'] = SensorReading.objects.count()
        ctx['problem_count'] = SensorReading.objects.filter(status_class='problem').count()
        ctx['state_count'] = SensorReading.objects.filter(status_class='state').count()
        ctx['pending_count'] = SensorReading.objects.filter(status_class='pending').count()
        return ctx


class ReadingDetailView(LoginRequiredMixin, DetailView):
    model = SensorReading
    template_name = 'monitoring/reading_detail.html'
    context_object_name = 'reading'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx['prescription'] = self.object.prescription
        except Exception:
            ctx['prescription'] = None
        return ctx


class ReadingCreateView(LoginRequiredMixin, CreateView):
    model = SensorReading
    form_class = ManualReadingForm
    template_name = 'monitoring/reading_form.html'
    success_url = reverse_lazy('monitoring:reading_list')

    def form_valid(self, form):
        from monitoring.preprocessing import extract_features, normalize_features

        obj = form.save(commit=False)
        try:
            raw = extract_features(obj.metrics)
            obj.feature_vector = normalize_features(raw)
        except Exception:
            pass
        obj.save()

        messages.success(self.request, 'Leitura registrada. Análise em andamento...')
        try:
            from .tasks import analyse_reading
            analyse_reading.delay(obj.pk)
        except Exception:
            pass
        return redirect(self.success_url)


@login_required
@require_POST
def trigger_analysis(request, pk):
    """
    Enqueue re-analysis of an existing SensorReading.
    Pass ?sync=1 to run synchronously (useful without a Celery worker).
    """
    reading = get_object_or_404(SensorReading, pk=pk)
    force_sync = request.GET.get('sync') == '1'

    if not force_sync:
        try:
            from .tasks import analyse_reading
            analyse_reading.delay(reading.pk)
            return JsonResponse({'status': 'queued'})
        except Exception:
            pass

    # Synchronous execution
    try:
        from prescriptions.pipeline import execute_pipeline
        p = execute_pipeline(reading)
        return JsonResponse({
            'status': 'done',
            'prescription_id': p.pk,
            'is_grounded': p.is_grounded,
            'defect_type': p.defect_type,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def request_event_summary(request, pk):
    """Enqueue an AI summary for a SensorReading event."""
    reading = get_object_or_404(SensorReading, pk=pk)
    try:
        from ai.tasks import generate_event_summary
        generate_event_summary.delay(reading.pk, request.user.pk)
        return JsonResponse({'status': 'queued'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
