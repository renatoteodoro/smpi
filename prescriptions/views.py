from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import DeleteView
from django.views.decorators.http import require_POST

from .models import Prescription


class PrescriptionListView(LoginRequiredMixin, ListView):
    model = Prescription
    template_name = 'prescriptions/prescription_list.html'
    context_object_name = 'prescriptions'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'fault', 'sensor_reading__measurement_point__equipment'
        )
        date_from = self.request.GET.get('date_from')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        date_to = self.request.GET.get('date_to')
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        fault = self.request.GET.get('fault')
        if fault:
            qs = qs.filter(defect_type__icontains=fault)
        return qs


class PrescriptionDeleteView(LoginRequiredMixin, DeleteView):
    model = Prescription
    success_url = reverse_lazy('prescriptions:prescription_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Prescrição excluída.')
        return super().form_valid(form)


class PrescriptionDetailView(LoginRequiredMixin, DetailView):
    model = Prescription
    template_name = 'prescriptions/prescription_detail.html'
    context_object_name = 'prescription'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['source_chunks'] = self.object.source_chunks.select_related('document').all()
        return ctx


@login_required
@require_POST
def trigger_analysis(request, reading_id):
    """Enqueue the prescription pipeline for a SensorReading."""
    from monitoring.models import SensorReading
    from .tasks import run_prescription_pipeline

    reading = get_object_or_404(SensorReading, pk=reading_id)
    task = run_prescription_pipeline.delay(reading.pk)
    return JsonResponse({'status': 'queued', 'task_id': task.id})
