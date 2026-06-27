from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from base.mixins import AdminRequiredMixin
from .models import Fault
from .forms import FaultForm


class FaultListView(LoginRequiredMixin, ListView):
    model = Fault
    template_name = 'faults/fault_list.html'
    context_object_name = 'faults'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        show = self.request.GET.get('type')
        if show == 'problems':
            qs = qs.filter(is_problem=True)
        elif show == 'states':
            qs = qs.filter(is_problem=False)
        return qs


class FaultCreateView(AdminRequiredMixin, CreateView):
    model = Fault
    form_class = FaultForm
    template_name = 'faults/fault_form.html'
    success_url = reverse_lazy('faults:fault_list')

    def form_valid(self, form):
        messages.success(self.request, 'Defeito/Estado cadastrado.')
        return super().form_valid(form)


class FaultUpdateView(AdminRequiredMixin, UpdateView):
    model = Fault
    form_class = FaultForm
    template_name = 'faults/fault_form.html'
    success_url = reverse_lazy('faults:fault_list')

    def form_valid(self, form):
        messages.success(self.request, 'Defeito/Estado atualizado.')
        return super().form_valid(form)
