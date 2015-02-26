"""RAML (REST API Markup Language) errors."""

__all__ = 'RequestError ParameterError ApiError'.split()

class ApiError(Exception):
    pass

class ParameterError(ApiError):
    def __init__(self, name, message='invalid {name}', *args, **data):
        self.name = name
        self.args = args
        self.data = data
        self.status = 400
        super(ParameterError, self).__init__(message.format(*args, name=name, **data))

class RequestError(ApiError):
    def __init__(self, status, message='invalid request', *args, **data):
        self.args = args
        self.data = data
        self.status = status
        super(RequestError, self).__init__(message.format(*args, status=status, **data))
