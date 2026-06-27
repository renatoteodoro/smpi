from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class EmailLoginForm(AuthenticationForm):
    """Login form that uses email field instead of username."""

    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'autofocus': True,
                'class': 'form-control',
                'placeholder': 'seu@email.com',
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class UserCreateForm(forms.ModelForm):
    """Form for admin creation of new users with password confirmation."""

    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar senha', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'name', 'role', 'phone')

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não coincidem.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Form for admin updates of existing users (no password change here)."""

    class Meta:
        model = User
        fields = ('email', 'name', 'role', 'phone', 'is_active')
