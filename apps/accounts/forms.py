"""User django admin dashboard forms"""
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating users on django admin"""
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class CustomUserChangeForm(UserChangeForm):
    """Custom form to update user info on django admin"""
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "is_active", "is_staff", "is_superuser")
