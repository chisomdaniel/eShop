import logging
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

from .custom_exceptions import UserAlreadyExist
from .responses import error_response, customize_response
from .email_handler import send_user_exist_email

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """custom exception handler function to handle
    exceptions globally"""
    response = exception_handler(exc, context)

    if isinstance(exc, UserAlreadyExist) and response is not None:
        send_user_exist_email(context.get("request"))
        response.status_code = 201
        return customize_response(response)
    
    if response is not None:
        """customize response"""
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            return customize_response(response, "Authentication credentials were not provided.")
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            return customize_response(response, "Validation error while processing request.")
        else:
            return customize_response(response)

    """internal server error"""
    request = context.get("request")
    error_message = (f"\n\t\t\tINTERNAL SERVER ERROR:\n"
                    f"{"="*80}\n{exc}\n{"="*80}"
                    f"In View\t\t: {context.get("view")}\n"
                    f"Logged in user\t: {request.user} [{request.user.email}]\n"
                    f"Accessing endpoint: {request.path} ({request.resolver_match.url_name})\n"
                    f"Method\t\t: {request.method}\nPayload\t\t: {request.data}\n"
                    f"{"="*80}")

    logger.critical(error_message,exc_info=exc)

    return response
