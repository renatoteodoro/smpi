"""CSV and PDF report generators for SensorReading + Prescription data."""
import csv
import io


def generate_csv(queryset) -> bytes:
    """Return CSV bytes for a SensorReading queryset."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        'ID', 'External ID', 'Equipamento', 'Ponto', 'Data evento',
        'Defeito', 'Status', 'RPM',
    ])
    for r in queryset.select_related('fault', 'measurement_point__equipment'):
        writer.writerow([
            r.pk,
            r.external_id or '',
            r.measurement_point.equipment.name if r.measurement_point else '',
            r.measurement_point.name if r.measurement_point else '',
            r.event_created_at.isoformat() if r.event_created_at else '',
            r.fault.code if r.fault else '',
            r.status_class,
            r.rpm or '',
        ])
    return buf.getvalue().encode('utf-8-sig')


def generate_pdf(queryset) -> bytes:
    """Return PDF bytes for a SensorReading queryset using ReportLab."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph('SMPI — Relatório de Leituras de Sensor', styles['Title']))
    elements.append(Spacer(1, 0.5*cm))

    data = [['ID', 'Equipamento', 'Data', 'Defeito', 'Status', 'RPM']]
    for r in queryset.select_related('fault', 'measurement_point__equipment'):
        data.append([
            str(r.external_id or r.pk),
            r.measurement_point.equipment.name if r.measurement_point else '—',
            r.event_created_at.strftime('%d/%m/%Y %H:%M') if r.event_created_at else '—',
            r.fault.code if r.fault else '—',
            r.status_class,
            str(round(r.rpm or 0)),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#CCCCCC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    doc.build(elements)
    return buf.getvalue()
