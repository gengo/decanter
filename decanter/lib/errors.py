
class BaseError(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


class ValidationError(BaseError):

    def __init__(self, message, fields={}):
        super(ValidationError, self).__init__(message)
        self.fields = fields


class ConnectionError(BaseError):

    def __init__(self, message, returned={}):
        super(ConnectionError, self).__init__(message)
        self.returned = returned
