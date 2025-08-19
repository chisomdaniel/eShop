from typing import Iterable
import uuid
from django.db import models, IntegrityError, transaction
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.products.models import Product
from apps.discounts.models import Discounts
from utils.generate_unique_id import generate_unique_id


class Order(models.Model):
    """Manage users order"""
    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    id = models.UUIDField(
        unique=True, default=uuid.uuid4, primary_key=True, editable=False
    )
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        help_text="The status of the order"
    )
    delivery_address_line1 = models.TextField()
    delivery_address_line2 = models.TextField(blank=True)
    delivery_address_closest_busstop = models.TextField()
    delivery_address_city = models.TextField()
    delivery_address_state = models.TextField()
    delivery_address_country = models.TextField()
    """delivery address info. the user can use the same address in their profile.
    Idealy, we can have a model or a TextChoice model to define a set of countries
    or states we are specifically open to, to automatically blockout the rest.
    """
    # delivery_option # pick up from our store in your location. delivery fee will be removed
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    applied_discount = models.ForeignKey(Discounts, on_delete=models.SET_NULL, null=True, related_name="orders_applied")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"[Order] {self.user.first_name}'s Order"
    
    def save(self, *args, **kwargs) -> None:
        if not self.order_number:
            self.order_number = generate_unique_id()

        max_retries = 5
        for _ in range(max_retries):
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                self.order_number = generate_unique_id()
        raise RuntimeError(f"Failed to generate unique order_number after {max_retries} retries")

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
    def delivery_fee(self):
        """Get the delivery/shipping fee for the order based on the user's location"""
        return 0.00

    @property
    def other_fees(self):
        """Place logic for other fees here. Includes taxes, service fee, etc
        Implement this if you need to use it.
        """
        return 0.00

    @property
    def total_amount(self):
        """Final price the customer will pay after discount has
        been removed and all fees have been added"""
        return round(float(
            (self.subtotal - self.discounts) + self.delivery_fee + self.other_fees), 2)

    @property
    def payment_status(self):
        """Easily check the payment status from the model"""
        return "UNPAID"
    
    @property
    def delivery_stauts(self):
        """Get the order delivery status"""
        return "Not Delivered"


class OrderItem(models.Model):
    """Manages each item/product in an order"""
    id = models.UUIDField(
        unique=True, default=uuid.uuid4, primary_key=True, editable=False
    )
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    applied_discount = models.ForeignKey(Discounts, on_delete=models.SET_NULL, null=True, related_name="items_applied")

    def clean(self) -> None:
        moq = self.product.min_order_quantity
        if self.quantity < moq:
            raise ValidationError(
                {
                    "quantity": f"Min order quantity (MOQ) for this product is {moq}"
                }
            )
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_product_per_order",
            )
        ]

    @property
    def title(self):
        """snapshot"""
        return f"{self.quantity} unit(s) of {self.product.name}"

    @property
    def subtotal(self):
        """Total amount before any discount is removed or any fee is added.
        the unit amount x the quantity"""
        return self.product.price*self.quantity

    @property
    def discounted_amount(self):
        """the amount after any product specific discount has been removed"""
        pass

    def __str__(self):
        return f"[OrderItem] {self.quantity} x {self.product.name}"
