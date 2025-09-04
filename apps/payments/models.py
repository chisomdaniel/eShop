import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from apps.orders.models import Order
from common.services.payment_service import verify_payment


class Payment(models.Model):
    """manage payments"""
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    id = models.UUIDField(
        unique=True, primary_key=True, default=uuid.uuid4, editable=False
    )
    reference = models.CharField(max_length=50, unique=True, editable=False)
    amount = models.DecimalField(max_digits=50, decimal_places=2, validators=[MinValueValidator(0)])
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="The status of the payment"
    )
    verified = models.BooleanField(default=False)
    currency = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]

    @property
    def status(self):
        """get the status of the payment.
        we set a redirect url on cancel as a meta data on the request when initializing
        the payment. on cancel, the user gets redirected to that page with the order id in the url,
        an endpoint is called to cancel the payment. the payment status is updated on cancel.

        """
        if (self.payment_status == Payment.PaymentStatus.PAID
            or self.payment_status == Payment.PaymentStatus.REFUNDED):
            return self.payment_status
        response = verify_payment(self.reference)
        data = response.get("data", {})
        if response.get("status", False) and data.get("status") == "success":
            self.payment_status = Payment.PaymentStatus.PAID
            self.save()
        # elif # add for other kinds `refunded`, `cancelled`, etc # failed, abandoned

        return self.payment_status

    def __str__(self):
        """string representation"""
        return f"[Payment] {settings.STORE_CURRENCY} {self.amount} for {self.order}"
