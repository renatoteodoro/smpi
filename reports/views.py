from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from .models import ReportRequest


class ReportListView(LoginRequiredMixin, ListView):
    model = ReportRequest
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().filter(requested_by=self.request.user)


class ReportCreateView(LoginRequiredMixin, View):
    def post(self, request):
        from .tasks import generate_report
        fmt = request.POST.get('format', 'csv')
        filters = {}
        if request.POST.get('status'):
            filters['status'] = request.POST.get('status')
        if request.POST.get('fault'):
            filters['fault'] = request.POST.get('fault')
        report = ReportRequest.objects.create(
            requested_by=request.user,
            format=fmt,
            filters=filters,
        )
        generate_report.delay(report.pk)
        from django.contrib import messages
        messages.success(request, 'Relatório sendo gerado. Você será notificado ao concluir.')
        return redirect('reports:report_list')


class ReportDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        report = get_object_or_404(ReportRequest, pk=pk, requested_by=request.user)
        if not report.file:
            from django.contrib import messages
            messages.error(request, 'Arquivo não disponível.')
            return redirect('reports:report_list')
        content_type = 'text/csv' if report.format == 'csv' else 'application/pdf'
        response = HttpResponse(report.file.read(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{report.file.name.split("/")[-1]}"'
        return response
