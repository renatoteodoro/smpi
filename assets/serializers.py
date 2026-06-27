from rest_framework import serializers

from .models import Equipment, MeasurementPoint


class MeasurementPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementPoint
        fields = '__all__'


class EquipmentSerializer(serializers.ModelSerializer):
    measurement_points = MeasurementPointSerializer(many=True, read_only=True)

    class Meta:
        model = Equipment
        fields = '__all__'
