from django import forms

from .models import Equipment, MeasurementPoint


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ('name', 'equipment_type', 'sector', 'status', 'description', 'image')


class MeasurementPointForm(forms.ModelForm):
    class Meta:
        model = MeasurementPoint
        fields = ('equipment', 'name', 'axis', 'sensor_type', 'location')
