"""RAML (REST API Markup Language) errors."""

__all__ = 'ApiError RequestError ParameterError AuthError'.split()

class ApiError(Exception):
    default_status = 500

    def __init__(self, message, *args, **data):
        self.args = args
        self.data = data
        self.status = data.get('status', self.default_status)
        super(ApiError, self).__init__(message.format(*args, **data))

class RequestError(ApiError):
    def __init__(self, status, message='invalid request', *args, **data):
        super(RequestError, self).__init__(message, *args, status=status, **data)

class ParameterError(ApiError):
    default_status = 400

    def __init__(self, name, message='invalid {name}', *args, **data):
        super(ParameterError, self).__init__(message, *args, name=name, **data)

class AuthError(ApiError):
    default_status = 401

    def __init__(self, message='unauthorized', *args, **data):
        super(AuthError, self).__init__(message, *args, **data)
