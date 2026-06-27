from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from base.mixins import MaintenanceRequiredMixin
from .models import Equipment, MeasurementPoint
from .forms import EquipmentForm, MeasurementPointForm


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'assets/equipment_list.html'
    context_object_name = 'equipments'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('measurement_points')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(sector__icontains=q)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Equipment.Status.choices
        return ctx


class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = 'assets/equipment_detail.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['measurement_points'] = self.object.measurement_points.all()
        ctx['recent_readings'] = []
        try:
            from monitoring.models import SensorReading
            ctx['recent_readings'] = SensorReading.objects.filter(
                measurement_point__equipment=self.object
            ).select_related('fault')[:10]
        except Exception:
            pass
        return ctx


class EquipmentCreateView(MaintenanceRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'assets/equipment_form.html'
    success_url = reverse_lazy('assets:equipment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Equipamento criado com sucesso.')
        return super().form_valid(form)


class EquipmentUpdateView(MaintenanceRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'assets/equipment_form.html'

    def get_success_url(self):
        return reverse_lazy('assets:equipment_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Equipamento atualizado.')
        return super().form_valid(form)


class MeasurementPointCreateView(MaintenanceRequiredMixin, CreateView):
    model = MeasurementPoint
    form_class = MeasurementPointForm
    template_name = 'assets/measurement_point_form.html'

    def get_success_url(self):
        return reverse_lazy('assets:equipment_detail', kwargs={'pk': self.object.equipment.pk})

    def get_initial(self):
        initial = super().get_initial()
        equipment_pk = self.kwargs.get('equipment_pk')
        if equipment_pk:
            initial['equipment'] = equipment_pk
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Ponto de medição criado.')
        return super().form_valid(form)


@login_required
@require_POST
def request_equipment_summary(request, pk):
    """Enqueue an AI summary for this equipment."""
    equipment = get_object_or_404(Equipment, pk=pk)
    try:
        from ai.tasks import generate_equipment_summary
        generate_equipment_summary.delay(equipment.pk, request.user.pk)
        return JsonResponse({'status': 'queued'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
