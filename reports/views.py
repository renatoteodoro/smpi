from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import DeleteView

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
        fmt = request.POST.get('format', 'csv')
        filters = {}
        if request.POST.get('status'):
            filters['status'] = request.POST.get('status')
        if request.POST.get('fault'):
            filters['fault'] = request.POST.get('fault')
        if request.POST.get('date_from'):
            filters['date_from'] = request.POST.get('date_from')
        if request.POST.get('date_to'):
            filters['date_to'] = request.POST.get('date_to')
        report = ReportRequest.objects.create(
            requested_by=request.user,
            format=fmt,
            filters=filters,
        )
        queued = False
        try:
            from .tasks import generate_report
            generate_report.delay(report.pk)
            queued = True
        except Exception:
            pass

        if queued:
            messages.info(
                request,
                'Relatório sendo gerado em segundo plano. '
                'Você receberá uma notificação quando estiver pronto e poderá navegar normalmente.'
            )
        else:
            # Celery indisponível — executa de forma síncrona
            try:
                from .tasks import _run_generation
                _run_generation(report)
                messages.success(request, 'Relatório gerado. Clique em Baixar.')
            except Exception as exc:
                messages.error(request, f'Erro ao gerar relatório: {exc}')
        return redirect('reports:report_list')


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = ReportRequest
    success_url = reverse_lazy('reports:report_list')

    def get_queryset(self):
        return super().get_queryset().filter(requested_by=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Relatório excluído.')
        return super().form_valid(form)


class ReportDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        report = get_object_or_404(ReportRequest, pk=pk, requested_by=request.user)
        if not report.file:
            messages.error(request, 'Arquivo não disponível. Gere um novo relatório.')
            return redirect('reports:report_list')
        try:
            content = report.file.read()
        except (FileNotFoundError, OSError):
            report.file = None
            report.status = 'pending'
            report.save(update_fields=['file', 'status', 'updated_at'])
            from .tasks import generate_report
            generate_report(report.pk)
            report.refresh_from_db()
            if report.status == 'done':
                try:
                    content = report.file.read()
                except Exception:
                    messages.error(request, 'Não foi possível gerar o arquivo.')
                    return redirect('reports:report_list')
            else:
                messages.error(request, f'Erro ao gerar o relatório: {report.error}')
                return redirect('reports:report_list')
        content_type = 'text/csv' if report.format == 'csv' else 'application/pdf'
        filename = report.file.name.split('/')[-1]
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ReportRetryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        report = get_object_or_404(ReportRequest, pk=pk, requested_by=request.user)
        report.file = None
        report.status = 'pending'
        report.error = ''
        report.save(update_fields=['file', 'status', 'error', 'updated_at'])
        queued = False
        try:
            from .tasks import generate_report
            generate_report.delay(report.pk)
            queued = True
        except Exception:
            pass

        if queued:
            messages.info(request, 'Relatório sendo regenerado. Você será notificado quando estiver pronto.')
        else:
            try:
                from .tasks import _run_generation
                _run_generation(report)
                messages.success(request, 'Relatório regenerado. Clique em Baixar.')
            except Exception as exc:
                messages.error(request, f'Erro ao regenerar relatório: {exc}')
        return redirect('reports:report_list')
