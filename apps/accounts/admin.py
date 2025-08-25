"""user admin"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile
from .forms import CustomUserCreationForm, CustomUserChangeForm


class UserAdmin(BaseUserAdmin):
    """Custom user admin class"""
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ["email", "first_name", "last_name", "is_active", "is_staff", "is_superuser"]
    list_filter = ["is_active", "is_superuser", "is_staff"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name"]}),
        ("Status", {"fields": ["is_active"]}),
        ("Permissions", {"fields": ["is_staff", "is_superuser"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "last_name", "password1", "password2"]
            }
        )
    ]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["first_name", "last_name"]
    filter_horizontal = []

admin.site.register(User, UserAdmin)
admin.site.register(Profile)
