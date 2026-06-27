from django import forms

from .models import SensorReading


class ManualReadingForm(forms.ModelForm):
    class Meta:
        model = SensorReading
        fields = ('measurement_point', 'metrics', 'rpm', 'event_created_at')
        widgets = {
            'metrics': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': '{"z_rms_velocity_mm_s": 1.5, ...}',
            }),
            'event_created_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
