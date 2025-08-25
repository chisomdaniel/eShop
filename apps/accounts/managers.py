from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Custom ser manager class"""

    def create_user(
            self, email: str, password: str, first_name: str, last_name: str, **extra_fields
            ):
        """
        Creates and saves a user with the given email, password and other fields
        """
        extra_fields.setdefault("is_superuser", False)

        if not email:
            raise ValueError("The email must be set")
        if not first_name and not last_name:
            raise ValueError("first_name and last_name must be provided")

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(
            self, email: str, password: str, first_name: str, last_name: str, **extra_fields
            ):
        """Create a superuser"""
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(email, password, first_name, last_name, **extra_fields)
