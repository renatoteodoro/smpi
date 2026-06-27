"""Evolution API client for sending WhatsApp messages."""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

EVOLUTION_API_URL = getattr(settings, 'EVOLUTION_API_URL', 'http://evolution_api:8080')
EVOLUTION_API_KEY = getattr(settings, 'EVOLUTION_API_KEY', '')
EVOLUTION_INSTANCE = getattr(settings, 'EVOLUTION_INSTANCE', 'smpi')


def send_text(phone: str, text: str) -> dict:
    """Send a plain-text WhatsApp message via Evolution API."""
    url = f'{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}'
    payload = {
        'number': phone.lstrip('+').replace(' ', ''),
        'text': text,
    }
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={'apikey': EVOLUTION_API_KEY},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f'Evolution API send_text error: {e}')
        raise
