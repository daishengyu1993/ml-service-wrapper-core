
class BadRequestError(RuntimeError):
    def __init__(self, name: str, message: str = None):
        super().__init__()
        self.name = name
        self.message = message

class BadParameterError(BadRequestError):
    def __init__(self, name: str, message: str = None):
        super().__init__(name, message)

class BadDataError(BadRequestError):
    def __init__(self, name: str, message: str = None):
        super().__init__(name, message)
