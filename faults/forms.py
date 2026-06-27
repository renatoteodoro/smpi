from django import forms

from .models import Fault


class FaultForm(forms.ModelForm):
    class Meta:
        model = Fault
        fields = ('code', 'name', 'description')
        help_texts = {
            'code': 'Os códigos normal, baseline, teste, acelerando, motor_desligado são estados e não geram prescrição.'
        }
