import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.utils.responses import error_response, success_response
from common.services.payment_service import verify_payment
from apps.payments.models import Payment
from apps.orders.serializers import OrderSerializer

from .serializers import VerifyPaymentSerializer

logger = logging.getLogger(__name__)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request, reference):
        serializer = VerifyPaymentSerializer(data={"reference": reference})
        serializer.is_valid(raise_exception=True)
        try:
            response = verify_payment(reference)
            payment = Payment.objects.get(reference=reference, order__customer=request.user)
            data = response.get("data", {})

            if response.get("status", False) and data.get("status") == "success":
                payment.payment_status = Payment.PaymentStatus.PAID
                payment.verified = True
                payment.save(update_fields=["payment_status", "verified"])
            
            order = OrderSerializer(payment.order).data
            res_data = {
                "reference": data.get("reference"),
                "status": data.get("status"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "paid_at": data.get("paid_at"),
                "channel": data.get("channel"),
                "gateway_response": data.get("gateway_response"),
                "order": order
            }
            return success_response(
                data=res_data,
                message=data.get("message"),
                status_code=status.HTTP_200_OK
            )
        except Payment.DoesNotExist:
            logger.error(f"Error while verifying payment. Invalid payment with ref: {reference} for user: {request.user.email}")
            return error_response(
                "Unable to verify payment. Please verify reference",
                status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Exception in VerifyPaymentView.get: {e}", exc_info=True)
            return error_response(
                "Unable to verify payment at this time. Please try again later or contact support if issue persists.",
                status.HTTP_503_SERVICE_UNAVAILABLE
            )


class WebhookView(APIView):
    http_method_names = ["post"]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        if not self._is_valid_ip(request):
            return error_response("Forbidden: Invalid IP.", status.HTTP_403_FORBIDDEN)
        if not self._is_valid_signature(request):
            return error_response("Invalid signature", status.HTTP_400_BAD_REQUEST)
        event = self._parse_event(request)
        if event is None:
            return error_response("Invalid Payload", status.HTTP_400_BAD_REQUEST)
        result = self._handle_event(event)
        return result or success_response({}, "Verified successfully", status_code=status.HTTP_200_OK)

    def _is_valid_ip(self, request):
        """check that the request came from a valid IP"""
        ip = request.META.get("REMOTE_ADDR")
        logger.info(f"Webhook request from IP: {ip}")
        return ip in settings.IP_WHITELIST
    
    def _is_valid_signature(self, request):
        """verify the signature"""
        paystack_signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE")
        secret = settings.PAYSTACK_KEY.encode("utf-8")
        body = request.body
        computed_signature = hmac.new(secret, body, hashlib.sha512).hexdigest()
        return hmac.compare_digest(computed_signature, paystack_signature or "")
    
    def _parse_event(self, request):
        try:
            return (
                request.data
                if isinstance(request.data, dict)
                else json.loads(request.body)
            )
        except Exception as e:
            logger.error(f"Exception in WebhookView._parse_event: {e}", exc_info=True)
            return None
    
    def _handle_event(self, event):
        event_type = event.get("event")
        data = event.get("data", {})
        reference = data.get("reference")
        if not reference:
            return error_response("Missing transaction reference.", status.HTTP_400_BAD_REQUEST)
        if event_type == "charge.success":
            try:
                payment = Payment.objects.get(reference=reference)
                payment.verified = True
                payment.save(update_fields=["verified"])

                if payment.payment_status != Payment.PaymentStatus.PAID:
                    payment.payment_status = Payment.PaymentStatus.PAID
                    payment.save(update_fields=["payment_status"])
            except Payment.DoesNotExist as e:
                logger.warning(f"Payment.DoesNotExist in WebhookView._handle_event: {e}\n\nEvent data: {data}")
                return error_response("Transaction not found", status_code=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error handling charge.success event: {e}", exc_info=True)
                return error_response("Error handling charge.success event.", status_code=status.HTTP_400_BAD_REQUEST)
            
        return None
