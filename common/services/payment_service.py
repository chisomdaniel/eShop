import logging
import requests
from requests.exceptions import Timeout, HTTPError
from django.conf import settings

from common.utils.custom_exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)

PAYSTACK_URL = {
    "init_payment": "https://api.paystack.co/transaction/initialize",
    "verify_payment": "https://api.paystack.co/transaction/verify/{reference}"
}

HEADERS = {
    "Authorization": f"Bearer {settings.PAYSTACK_KEY}",
    "content-type": "application/json",
}

TIMEOUT = 20 # timeout in seconds

def initialize_payment(data: dict):
    """initialize a payment and return the redirect url"""
    if "email" not in data:
        raise KeyError("'email' should be in data when initializing payment")
    if "amount" not in data:
        raise KeyError("'amount' should be in data when initializing payment")
    if "order_id" not in data:
        raise KeyError("'order_id' should be in data when initializing payment")
    data.setdefault("currency", settings.STORE_CURRENCY)

    amount = data["amount"]
    data["amount"] *= 100 # convert to subunit (Paystack expects amount in subunit)
    order_id = data.pop("order_id")
    try:
        response = requests.post(PAYSTACK_URL["init_payment"], json=data, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except HTTPError:
        logger.error("HTTP error while initializing payment to Paystack\nStatus Code:%s\n\nResponse data:\n%s",
                     response.status_code, response.text)
        raise ServiceUnavailable("Unable to initialize payment, try again. Please contact support if issue persists")
    except Timeout:
        logger.error("Timeout error while initializing payment. Timeout after %s min", TIMEOUT)
        raise ServiceUnavailable("Unable to initialize payment, try again. Please contact support if issue persists")

    res_data = response.json()
    if not res_data["status"]:
        logger.critical("Payment initialization failed (Paystack).\nStatus Code:%s\n\nResponse data:\n%s",
                        response.status_code, response.text)
        raise ServiceUnavailable

    from apps.payments.models import Payment
    payment = Payment.objects.create(
        reference=res_data["data"]["reference"],
        amount=amount,
        order_id=order_id,
        currency=data.get("currency")
    )
    return res_data


def verify_payment(reference):
    """verify the status of a payment"""
    try:
        response = requests.get(PAYSTACK_URL["verify_payment"].format(reference=reference), headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except HTTPError:
        logger.error("HTTP error while verifying payment to Paystack\nStatus Code:%s\n\nResponse data:\n%s",
                     response.status_code, response.text)
        raise ServiceUnavailable("Unable to verifying payment, try again. Please contact support if issue persists")
    except Timeout:
        logger.error("Timeout error while verifying payment. Timeout after %s min", TIMEOUT)
        raise ServiceUnavailable("Unable to verifying payment, try again. Please contact support if issue persists")

