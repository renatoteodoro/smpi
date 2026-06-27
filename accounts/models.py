from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from base.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Custom manager that uses email as the unique identifier (no username)."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Custom user model with email authentication and role-based access.

    Roles:
        admin       — full access, can manage users and system configuration
        maintenance — can view and act on readings, prescriptions, and documents
        viewer      — read-only access to monitoring data
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        MAINTENANCE = 'maintenance', 'Técnico de Manutenção'
        VIEWER = 'viewer', 'Visualizador'

    email = models.EmailField(unique=True)
    name = models.CharField('Nome', max_length=200, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        """Returns name if set, falls back to email."""
        return self.name or self.email


class Organization(TimeStampedModel):
    """Singleton model holding the FIESC organization profile.

    Use Organization.get_instance() to retrieve the single record.
    """

    corporate_name = models.CharField('Razão Social', max_length=300)
    cnpj = models.CharField(max_length=14, blank=True)
    logo = models.ImageField(upload_to='organization/', blank=True, null=True)

    class Meta:
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'

    def __str__(self):
        return self.corporate_name

    @classmethod
    def get_instance(cls):
        """Return (or create) the single Organization record."""
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'corporate_name': 'SMPI — Sistema de Manutenção Prescritiva Inteligente'
            },
        )
        return obj
