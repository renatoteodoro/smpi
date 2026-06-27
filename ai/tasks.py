from celery import shared_task


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_equipment_summary(self, equipment_id: int, requested_by_id: int):
    """Generate an AI summary for an Equipment and notify the requesting user."""
    try:
        from assets.models import Equipment
        from accounts.models import User
        from notifications.models import Notification
        from prescriptions.llm import get_llm
        from langchain_core.messages import HumanMessage, SystemMessage
        from monitoring.models import SensorReading

        equipment = Equipment.objects.get(pk=equipment_id)
        user = User.objects.get(pk=requested_by_id)

        readings_qs = SensorReading.objects.filter(
            measurement_point__equipment=equipment
        ).select_related('fault')
        total = readings_qs.count()
        problems = readings_qs.filter(status_class='problem').count()
        top_faults = list(
            readings_qs.filter(status_class='problem', fault__isnull=False)
            .values('fault__code', 'fault__name')
            .annotate(count=__import__('django.db.models', fromlist=['Count']).Count('id'))
            .order_by('-count')[:5]
        )

        context = (
            f'Equipamento: {equipment.name} ({equipment.equipment_type}, {equipment.sector})\n'
            f'Status: {equipment.get_status_display()}\n'
            f'Total de leituras: {total}\n'
            f'Leituras com problema: {problems}\n'
            f'Defeitos mais frequentes: ' +
            ', '.join([f"{f['fault__code']} ({f['count']}x)" for f in top_faults]) or 'nenhum'
        )

        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content='Você é um assistente de manutenção industrial. Responda em português, em Markdown, de forma técnica e objetiva.'),
            HumanMessage(content=f'Gere um resumo de situação para o seguinte equipamento:\n\n{context}'),
        ])
        summary = response.content if hasattr(response, 'content') else str(response)

        Notification.objects.create(
            user=user,
            title=f'Resumo: {equipment.name}',
            message=summary[:200] + '...' if len(summary) > 200 else summary,
            level='info',
            link=f'/equipment/{equipment.pk}/',
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_event_summary(self, reading_id: int, requested_by_id: int):
    """Generate an AI summary for a SensorReading event and notify the user."""
    try:
        from monitoring.models import SensorReading
        from accounts.models import User
        from notifications.models import Notification
        from prescriptions.llm import get_llm
        from langchain_core.messages import HumanMessage, SystemMessage

        reading = SensorReading.objects.select_related(
            'fault', 'measurement_point__equipment'
        ).get(pk=reading_id)
        user = User.objects.get(pk=requested_by_id)

        context = (
            f'Equipamento: {reading.measurement_point.equipment.name}\n'
            f'Ponto: {reading.measurement_point.name}\n'
            f'Data: {reading.event_created_at}\n'
            f'Defeito: {reading.fault.code if reading.fault else "não identificado"}\n'
            f'Status: {reading.status_class}\n'
            f'RPM: {reading.rpm}'
        )
        try:
            p = reading.prescription
            context += f'\n\nPrescrição disponível: {p.defect_type} — fundamentada: {"sim" if p.is_grounded else "não"}'
        except Exception:
            pass

        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content='Você é um assistente de manutenção industrial. Responda em português, de forma técnica, em até 3 parágrafos.'),
            HumanMessage(content=f'Resuma este evento de sensor para um técnico de manutenção:\n\n{context}'),
        ])
        summary = response.content if hasattr(response, 'content') else str(response)

        Notification.objects.create(
            user=user,
            title=f'Resumo evento #{reading.external_id or reading_id}',
            message=summary[:200] + '...' if len(summary) > 200 else summary,
            level='info',
            link=f'/monitoring/{reading_id}/',
        )
    except Exception as exc:
        raise self.retry(exc=exc)
