from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView, TemplateView, UpdateView, View

from base.mixins import AdminRequiredMixin
from .forms import EmailLoginForm, UserCreateForm, UserUpdateForm

User = get_user_model()


class LoginView(FormView):
    """Email-based login view. Redirects authenticated users to the dashboard."""

    template_name = 'core/landing.html'
    form_class = EmailLoginForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class LogoutView(View):
    """POST-only logout view."""

    def post(self, request):
        logout(request)
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Current user's profile page."""

    template_name = 'accounts/profile.html'


class UserListView(AdminRequiredMixin, ListView):
    """Admin-only: list all system users."""

    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    ordering = ('email',)


class UserCreateView(AdminRequiredMixin, CreateView):
    """Admin-only: create a new user."""

    model = User
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuário criado com sucesso.')
        return super().form_valid(form)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Admin-only: edit an existing user."""

    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuário atualizado.')
        return super().form_valid(form)
