import re

from celery import shared_task


def _md_to_whatsapp(text: str) -> str:
    """Convert Markdown to WhatsApp formatting."""
    # Bold: **text** → *text*
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
    # Italic: _text_ stays (WhatsApp already uses _)
    # Headings: ## Heading → *Heading*
    text = re.sub(r'^#{1,6}\s+(.+)$', r'*\1*', text, flags=re.MULTILINE)
    # Horizontal rule
    text = re.sub(r'\n---+\n', '\n', text)
    # Inline code: `code` → stays (WhatsApp renders backtick mono)
    # Links: [text](url) → text (url)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1 (\2)', text)
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


@shared_task(bind=True, max_retries=2, default_retry_delay=15)
def process_inbound_whatsapp(self, message_id: int):
    """
    Process an inbound WhatsApp message with conversation history,
    same behavior as the site's floating chatbot.
    """
    try:
        from .models import WhatsAppMessage
        from .client import send_text
        from langchain_core.messages import HumanMessage, AIMessage
        from ai.agent import _get_agent

        msg = WhatsAppMessage.objects.get(pk=message_id)
        phone = msg.phone
        text = msg.content.strip()

        # Build conversation history from last 20 messages with this phone
        recent = list(
            WhatsAppMessage.objects
            .filter(phone=phone)
            .exclude(pk=msg.pk)
            .order_by('-created_at')[:20]
        )
        history = []
        for m in reversed(recent):
            if m.direction == 'inbound':
                history.append(HumanMessage(content=m.content))
            else:
                history.append(AIMessage(content=m.content))
        history.append(HumanMessage(content=text))

        agent = _get_agent()
        result = agent.invoke({'messages': history})
        last = result['messages'][-1]
        reply = last.content if hasattr(last, 'content') else str(last)

        reply = _md_to_whatsapp(reply)
        if len(reply) > 4000:
            reply = reply[:3980] + '\n\n_(mensagem truncada)_'

        # Usa reply_jid (remoteJid original) para responder ao chat correto
        reply_to = msg.reply_jid or phone
        send_text(reply_to, reply)

        WhatsAppMessage.objects.create(
            direction='outbound',
            phone=phone,
            message_id=f'out_{message_id}',
            content=reply,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
