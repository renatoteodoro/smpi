from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import DeleteView

from base.mixins import MaintenanceRequiredMixin

from .forms import KnowledgeDocumentForm
from .models import KnowledgeDocument


class DocumentListView(LoginRequiredMixin, ListView):
    model = KnowledgeDocument
    template_name = 'knowledge/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('fault')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(tags__icontains=q)
        return qs


class DocumentCreateView(MaintenanceRequiredMixin, CreateView):
    model = KnowledgeDocument
    form_class = KnowledgeDocumentForm
    template_name = 'knowledge/document_form.html'
    success_url = reverse_lazy('knowledge:document_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Trigger async ingestion
        try:
            from .tasks import ingest_document_task
            ingest_document_task.delay(self.object.pk)
            messages.success(
                self.request,
                'Documento enviado. Ingestão em andamento — você será notificado.'
            )
        except Exception:
            messages.info(
                self.request,
                'Documento salvo. Execute ingest_documents para indexar.'
            )
        return response


class DocumentDeleteView(MaintenanceRequiredMixin, DeleteView):
    model = KnowledgeDocument
    success_url = reverse_lazy('knowledge:document_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Documento excluído.')
        return super().form_valid(form)


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = KnowledgeDocument
    template_name = 'knowledge/document_detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['chunks'] = self.object.chunks.all()[:20]
        return ctx
