"""Evolution API client for sending WhatsApp messages."""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

EVOLUTION_API_URL = getattr(settings, 'EVOLUTION_API_URL', 'http://evolution_api:8080')
EVOLUTION_API_KEY = getattr(settings, 'EVOLUTION_API_KEY', '')
EVOLUTION_INSTANCE = getattr(settings, 'EVOLUTION_INSTANCE', 'smpi')


def _headers():
    return {'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json'}


def send_text(phone: str, text: str) -> dict:
    """Send a plain-text WhatsApp message via Evolution API v2."""
    url = f'{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}'
    payload = {
        'number': phone.lstrip('+').replace(' ', ''),
        'text': text,
        'delay': 1200,
    }
    try:
        resp = requests.post(url, json=payload, headers=_headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f'Evolution API send_text error: {e}')
        raise


def check_number(phone: str) -> bool:
    """Return True if the phone number is registered on WhatsApp."""
    url = f'{EVOLUTION_API_URL}/chat/whatsappNumbers/{EVOLUTION_INSTANCE}'
    number = phone.lstrip('+').replace(' ', '')
    try:
        resp = requests.post(url, json={'numbers': [number]}, headers=_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return bool(data and data[0].get('exists'))
    except Exception as e:
        logger.error(f'Evolution API check_number error: {e}')
        return False
