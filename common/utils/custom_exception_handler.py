from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

from .custom_exceptions import UserAlreadyExist
from .responses import error_response, customize_response

def custom_exception_handler(exc, context):
    """custom exception handler function to handle
    exceptions globally"""
    # TODO: handle permission denied and 404 error. turn off debug to test
    response = exception_handler(exc, context)

    if isinstance(exc, UserAlreadyExist) and response is not None:
        send_user_exist_email(context.get("request"))
        response.status_code = 201
        response = customize_response(response)

    if not response:
        # server error
        # TODO: use a logger here
        return response # remove this line
    else:
        response = customize_response(response)

    return response

def send_user_exist_email(request):
    # TODO: fill this
    email = request.data.get("email")
    print("Email: user already exist")
    return


# TODO: catch permission denied exception and log it
# TODO: add a message for 400 Bad request error

