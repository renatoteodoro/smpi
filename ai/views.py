from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from .models import ChatMessage, ChatSession


class SessionListView(LoginRequiredMixin, ListView):
    model = ChatSession
    template_name = 'ai/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).exclude(title='Chatbot flutuante')


class SessionDeleteView(LoginRequiredMixin, DeleteView):
    model = ChatSession
    success_url = reverse_lazy('ai:session_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # Confirma e exclui direto via POST; GET redireciona de volta
        return self.post(request, *args, **kwargs)


class SessionCreateView(LoginRequiredMixin, View):
    def post(self, request):
        session = ChatSession.objects.create(user=request.user)
        return redirect('ai:session_detail', pk=session.pk)


class SessionDetailView(LoginRequiredMixin, DetailView):
    model = ChatSession
    template_name = 'ai/chat.html'
    context_object_name = 'session'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['messages_list'] = self.object.messages.all()
        return ctx


def _trim_chatbot_history(session, keep=20):
    """Deleta mensagens antigas mantendo apenas as `keep` mais recentes."""
    ids_to_keep = session.messages.order_by('-created_at').values_list('id', flat=True)[:keep]
    session.messages.exclude(id__in=list(ids_to_keep)).delete()


def _sse_stream(session, user_message, history_limit=None):
    """Generator that yields SSE-formatted data lines."""
    from .agent import stream_chat_with_agent
    full_response = ''
    try:
        for chunk in stream_chat_with_agent(session.pk, user_message, history_limit=history_limit):
            full_response += chunk
            yield f"data: {chunk.replace(chr(10), '\\n').replace(chr(13), '')}\n\n"
    except Exception as e:
        yield f'data: [ERROR] {e}\n\n'
    finally:
        yield 'data: [DONE]\n\n'
        if full_response:
            ChatMessage.objects.create(session=session, role='assistant', content=full_response)


@login_required
@require_POST
def chat_stream(request, session_id):
    session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Mensagem vazia.'}, status=400)

    ChatMessage.objects.create(session=session, role='user', content=user_message)
    if session.title == 'Nova conversa':
        session.title = user_message[:80]
        session.save(update_fields=['title', 'updated_at'])

    response = StreamingHttpResponse(_sse_stream(session, user_message), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@login_required
@require_POST
def chatbot_stream(request):
    """SSE endpoint for the floating chatbot widget."""
    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Mensagem vazia.'}, status=400)

    session, _ = ChatSession.objects.get_or_create(
        user=request.user, title='Chatbot flutuante'
    )
    ChatMessage.objects.create(session=session, role='user', content=user_message)

    # Mantém apenas as 20 mensagens mais recentes no banco
    _trim_chatbot_history(session, keep=20)

    response = StreamingHttpResponse(_sse_stream(session, user_message, history_limit=20), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
