from rest_framework.response import Response
from rest_framework import status

def error_response(message: str, status_code: int):
    """Helper function to format error responses."""
    return Response({
        "status": status_code,
        "message": message
    }, status=status_code)

def success_response(data: list | dict, message: str, status_code: int=status.HTTP_200_OK):
    """Helper function to format success responses"""
    return Response({
        "status": status_code,
        "message": message,
        "data": data
    }, status=status_code)
