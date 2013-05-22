
class BaseError(Exception):
    def __init__(self, message):

        Exception.__init__(self, message)
        self.message = message


class ValidationError(BaseError):

    def __init__(self, message, fields={}):

        Exception.__init__(self, message)
        self.message = message
        self.fields = fields

