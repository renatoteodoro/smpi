from celery import shared_task


@shared_task(bind=True, max_retries=2, default_retry_delay=15)
def process_inbound_whatsapp(self, message_id: int):
    """
    Process an inbound WhatsApp message:
    1. Parse the user query / event ID
    2. Call the AI agent for a response
    3. Send the reply back via Evolution API
    """
    try:
        from .models import WhatsAppMessage
        from .client import send_text

        msg = WhatsAppMessage.objects.get(pk=message_id)
        text = msg.content.strip()

        # Build a minimal chat history and ask the agent
        from langchain_core.messages import HumanMessage
        from prescriptions.llm import get_llm
        from ai.agent import _get_agent

        agent = _get_agent()
        result = agent.invoke({'messages': [HumanMessage(content=text)]})
        last = result['messages'][-1]
        reply = last.content if hasattr(last, 'content') else str(last)

        # Truncate to WhatsApp message limit
        if len(reply) > 4000:
            reply = reply[:3980] + '\n\n_[mensagem truncada]_'

        send_text(msg.phone, reply)

        # Save outbound record
        WhatsAppMessage.objects.create(
            direction='outbound',
            phone=msg.phone,
            message_id=f'out_{message_id}',
            content=reply,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
