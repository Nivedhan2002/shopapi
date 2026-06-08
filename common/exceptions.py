from rest_framework import status
from rest_framework.exceptions import APIException


class ServiceError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Unable to process request"
    default_code = "service_error"


class NotFoundError(ServiceError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"
    default_code = "not_found"


class ConflictError(ServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Request conflicts with current state"
    default_code = "conflict"
