from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, phone=None, email=None, password=None, **extra_fields):
        if not phone and not email:
            raise ValueError(_("At least phone or email must be provided"))

        if email:
            email = self.normalize_email(email)

        # If username is not provided, generate one or leave blank
        username = extra_fields.pop('username', None)
        if not username and phone:
            username = phone  # or generate random, or leave None if blank=True

        user = self.model(
            phone=phone,
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone=None, email=None, password=None, **extra_fields):
        """
        Override to make createsuperuser work without forcing username
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Allow creating superuser with phone or email only
        # We pass phone as the main identifier
        return self.create_user(
            phone=phone,
            email=email,
            password=password,
            **extra_fields
        )

class CustomUser(AbstractUser):
    """
    Custom user model using phone as primary login for customers,
    email for managers/owners.
    """
    # Make username optional (not used for login)
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Optional username"),
    )

    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=True,
        null=True,
        help_text=_("Required for managers/owners"),
    )

    phone = models.CharField(
        _("phone number"),
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Required for normal users/customers"),
    )

    # Role to differentiate behavior (you can expand later)
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('MANAGER', 'Restaurant Manager'),
        ('OWNER', 'Restaurant Owner'),
        ('STAFF', 'Staff'),
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER',
    )

    # For managers/owners: link to restaurants
    managed_restaurants = models.ManyToManyField(
        'menu.Restaurant',  # adjust 'menu' to your app name
        related_name='managers_and_staff',
        blank=True,
    )

    objects = CustomUserManager()
    
    # Required for AbstractUser
    USERNAME_FIELD = 'phone'          # default login field = phone
    REQUIRED_FIELDS = ['email']       # when createsuperuser asks for more

    # Use email as alternative login for managers
    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.phone or self.email or self.username or f"User {self.id}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.phone or self.email

    @property
    def is_manager_or_owner(self):
        return self.role in ('MANAGER', 'OWNER', 'STAFF')