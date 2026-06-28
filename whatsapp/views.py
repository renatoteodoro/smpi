import json
import logging

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import WhatsAppMessage

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    """Receive Evolution API webhook events and dispatch async processing."""

    def post(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        event = payload.get('event', '')
        data = payload.get('data', {})

        if event == 'messages.upsert':
            msg_data = data.get('message', {})
            key = data.get('key', {})

            # Ignore messages sent by us (fromMe=True)
            if key.get('fromMe'):
                return JsonResponse({'status': 'ignored'})

            remote_jid = key.get('remoteJid', '')
        sender_pn = key.get('senderPn', '')
        # remoteJid com @lid é ID interno do WhatsApp — usa senderPn para o número real
        if remote_jid.endswith('@lid') and sender_pn:
            phone = sender_pn.split('@')[0]
        else:
            phone = remote_jid.split('@')[0]
            message_id = key.get('id', '')
            content = (
                msg_data.get('conversation')
                or msg_data.get('extendedTextMessage', {}).get('text', '')
                or '[mídia]'
            )

            if message_id and content != '[mídia]':
                msg, created = WhatsAppMessage.objects.get_or_create(
                    message_id=message_id,
                    defaults={
                        'direction': 'inbound',
                        'phone': phone,
                        'content': content,
                        'raw_payload': payload,
                    }
                )
                if created:
                    try:
                        from .tasks import process_inbound_whatsapp
                        process_inbound_whatsapp.delay(msg.pk)
                    except Exception as e:
                        logger.error(f'Failed to queue WhatsApp processing: {e}')

        return JsonResponse({'status': 'ok'})
