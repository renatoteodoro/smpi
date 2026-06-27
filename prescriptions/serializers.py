from rest_framework import serializers

from .models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    fault_code = serializers.CharField(source='fault.code', read_only=True)
    reading_external_id = serializers.IntegerField(source='sensor_reading.external_id', read_only=True)

    class Meta:
        model = Prescription
        fields = (
            'id', 'sensor_reading', 'reading_external_id', 'fault', 'fault_code',
            'defect_type', 'occurrences_count', 'occurrences_frequency',
            'instructions', 'is_grounded', 'created_at',
        )
        read_only_fields = fields
