from django import forms

from .models import KnowledgeDocument


class KnowledgeDocumentForm(forms.ModelForm):
    class Meta:
        model = KnowledgeDocument
        fields = ('title', 'file', 'fault', 'tags', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'Ex: vibração, rolamento, manutenção'}),
        }
