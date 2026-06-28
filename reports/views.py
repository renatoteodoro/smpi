from django.contrib import messages
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
        from django.contrib import messages
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
        # Tenta Celery; se worker não estiver disponível, executa de forma síncrona
        queued = False
        try:
            from .tasks import generate_report
            generate_report.delay(report.pk)
            queued = True
        except Exception:
            pass

        if not queued:
            try:
                from .tasks import generate_report
                generate_report(report.pk)
            except Exception as exc:
                messages.error(request, f'Erro ao gerar relatório: {exc}')
                return redirect('reports:report_list')

        if queued:
            messages.success(request, 'Relatório sendo gerado em background. Você será notificado ao concluir.')
        else:
            messages.success(request, 'Relatório gerado com sucesso. Clique em Baixar.')
        return redirect('reports:report_list')


class ReportDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        from django.contrib import messages
        report = get_object_or_404(ReportRequest, pk=pk, requested_by=request.user)
        if not report.file:
            messages.error(request, 'Arquivo não disponível. Gere um novo relatório.')
            return redirect('reports:report_list')
        try:
            content = report.file.read()
        except (FileNotFoundError, OSError):
            # Arquivo sumiu (ex: gerado em outro ambiente). Regenera agora.
            report.file = None
            report.status = 'pending'
            report.save(update_fields=['file', 'status', 'updated_at'])
            try:
                from .tasks import generate_report
                generate_report.delay(report.pk)
                messages.warning(request, 'Arquivo não encontrado — foi solicitada a regeneração. Aguarde e tente novamente.')
            except Exception:
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
            else:
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
        if not queued:
            from .tasks import generate_report
            generate_report(report.pk)
        if queued:
            messages.info(request, 'Relatório sendo regenerado em background.')
        else:
            messages.success(request, 'Relatório regenerado. Clique em Baixar.')
        return redirect('reports:report_list')
