from rest_framework.response import Response
from rest_framework import status


def customize_response(response: Response, message=""):
    """customize the response object"""
    # DRF repr str error messages as a dict with the key `detail`
    res_data = response.data
    if isinstance(res_data, dict):
        res_data = res_data.get("detail", res_data)
        
    if isinstance(res_data, str):
        if not message:
            message = res_data
        res_data = None

    data = {
            "status": response.status_code,
            "message": message,
            "data": res_data
        }
    response.data = data
    return response


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
