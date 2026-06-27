from rest_framework import serializers

from faults.serializers import FaultSerializer
from .models import SensorReading


class SensorReadingSerializer(serializers.ModelSerializer):
    fault_detail = FaultSerializer(source='fault', read_only=True)
    equipment_name = serializers.CharField(
        source='measurement_point.equipment.name', read_only=True
    )

    class Meta:
        model = SensorReading
        fields = (
            'id', 'external_id', 'measurement_point', 'equipment_name',
            'metrics', 'fault', 'fault_detail', 'status_class',
            'rpm', 'event_created_at', 'created_at',
        )
        read_only_fields = ('feature_vector', 'status_class', 'created_at')
