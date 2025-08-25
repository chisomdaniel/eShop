import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from apps.products.models import Product


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
    
    @property
    def subtotal(self):
        """The total price of all items before discount is removed
        or any other additional charges is added."""
        subtotal = sum([i.subtotal for i in self.items.all()])
        return subtotal
    
    @property
    def discounts(self):
        """Get the total deduction from the original item price
        resulting from application of discount, sale price, etc"""
        return 0.00
    
    @property
    def total_amount(self):
        """Final price the customer will pay after discount has
        been removed and all fees have been added"""
        return round(float(
            (self.subtotal - self.discounts)), 2)


class CartItem(models.Model):
    """Manages each item in a cart"""
    id = models.UUIDField(
        unique=True, primary_key=True, editable=False, default=uuid.uuid4
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    def clean(self) -> None:
        moq = self.product.min_order_quantity
        if not self.quantity:
            self.quantity = moq
        if self.quantity < moq:
            raise ValidationError(
                {
                    "quantity": f"Min order quantity (MOQ) for this product is {moq}"
                }
            )
        product = self.product
        if product.status == Product.ProductStatus.archived:
            raise ValidationError({
                "product": "Product unavailable (Archived)"
            })
        if product.status == Product.ProductStatus.draft:
            raise ValidationError({
                "product": "Can't add a product in draft to cart"
            })
        if product.stock_quantity == 0 and not product.allow_backorder:
            raise ValidationError({
                "product": "This product is out of stock"
            })
        if self.quantity < product.stock_quantity:
            raise ValidationError({
                "quantity": "Not enough stock to fufil order"
            })
    
    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_per_cart"
            )
        ]

    def __str__(self):
        return f"[CartItem] {self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        """Total amount before any discount is removed or any fee is added.
        the unit amount x the quantity"""
        return self.product.price*self.quantity

    @property
    def discounted_amount(self):
        """the amount after any product specific discount has been removed"""
        pass
