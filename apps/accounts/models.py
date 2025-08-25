from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, unique=True, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    image = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        """meta class"""
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
    
    @property
    def full_name(self):
        """returns the user first name and last name"""
        return f"{self.first_name.capitalize()} {self.last_name.capitalize()}".strip()

    def get_short_name(self):
        """returns the short name for the user"""
        return self.first_name

    def __str__(self):
        """return the str representation"""
        return f"{self.first_name} {self.last_name}"


class Profile(models.Model):
    """Profile model. Carries other necessary user-specific informations"""
    date_of_birth = models.DateField(null=True, blank=True)

    delivery_address_line1 = models.TextField(blank=True)
    delivery_address_line2 = models.TextField(blank=True)
    delivery_address_closest_busstop = models.TextField(blank=True)
    delivery_address_city = models.TextField(blank=True)
    delivery_address_state = models.TextField(blank=True)
    delivery_address_country = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"[User Profile] {self.user.full_name}"

