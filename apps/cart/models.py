import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.products.models import Products


class Cart(models.Model):
    """A user's cart"""
    id = models.UUIDField(
        unique=True, default=uuid.uuid4, primary_key=True, editable=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
    
    def __str__(self):
        return f"[Cart] {self.user.first_name}'s cart"


class CartItem(models.Model):
    """Manages each item in a cart"""
    id = models.UUIDField(
        unique=True, primary_key=True, editable=False, default=uuid.uuid4
    )
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    def clean(self) -> None:
        moq = self.product.min_order_quantity
        if self.quantity < moq:
            raise ValidationError(
                {
                    "quantity": f"Min order quantity (MOQ) for this product is {moq}"
                }
            )
    
    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_per_cart"
            )
        ]

    def __str__(self):
        return f"[CartItem] {self.quantity} x {self.product.name}"
