import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone

from apps.products.models import Product, Category


class Discounts(models.Model):
    """Manage all coupons and discount"""
    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Percent"
        FIXED =  "fixed", "Fixed"
        SHIPPING = "free_shipping", "Free shipping"
        NEW_USER = "new_user", "New user discount"
        FIRST_ORDER = "first_order", "First order"

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False
    )
    code = models.CharField(max_length=100, null=True, blank=True, unique=True,
                            help_text="Leave as Null for automatic discount")
    name = models.CharField(max_length=100, blank=True)
    type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.FIXED,
        help_text="Choose the type of discount"
    )
    value = models.DecimalField(max_digits=50, decimal_places=2)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField()
    total_usage_limit = models.PositiveIntegerField(null=True)
    usage_count = models.PositiveIntegerField(default=0)
    per_customer_limit = models.PositiveIntegerField(null=True)
    min_amount = models.PositiveIntegerField(
        default=0,
        help_text="Minimum purchase amount the discount can be applied to"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    products = models.ManyToManyField(Product, related_name="discounts")
    categories = models.ManyToManyField(Category, related_name="discounts")

    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        ordering = ["-updated_at"]
    
    def __str__(self):
        return f"[Discount] code: {self.code}, ends at: {self.ends_at}"
    
    @property
    def active(self):
        """Check if discount is still active. Use this instead of the `is_active`
        attribute to check if the discount is still valid.
        """
        if (self.is_active
        and self.total_usage_limit
        and self.usage_count < self.total_usage_limit
        and self.starts_at < timezone.now()
        and self.ends_at > timezone.now()):
            return True
        
        return False

