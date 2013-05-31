
class BaseError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


class ValidationError(BaseError):
    def __init__(self, message, fields={}):
        super(BaseError, self).__init__(self, message)
        self.fields = fields


class ConnectionError(BaseError):
    def __init__(self, message, returned={}):
        super(BaseError, self).__init__(self, message)
        self.returned = returned
