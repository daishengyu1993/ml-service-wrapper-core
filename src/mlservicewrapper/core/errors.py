
class BadRequestError(RuntimeError):
    def __init__(self, message: str = None):
        super().__init__(message)
        self.message = message or "The request was not valid"

class BadDatasetError(BadRequestError):
    def __init__(self, dataset_name: str, message: str = None):
        super().__init__(message or "The input dataset '{}' was not valid".format(dataset_name))
        self.name = dataset_name

class DatasetFieldError(BadDatasetError):
    def __init__(self, dataset_name: str, field_name: str, message: str = None):
        super().__init__(dataset_name, message or "The field '{}' was not valid for input dataset '{}'".format(field_name, dataset_name))
        self.field_name = field_name

class MissingDatasetFieldError(DatasetFieldError):
    def __init__(self, dataset_name: str, field_name: str, message: str = None):
        super().__init__(dataset_name, field_name, message or "The field '{}' on input dataset '{}' is required but could not be found!".format(field_name, dataset_name))

class MissingDatasetError(BadDatasetError):
    def __init__(self, dataset_name: str, message: str = None):
        super().__init__(dataset_name, message or "The input dataset '{}' was not found.".format(dataset_name))


class BadParameterError(BadRequestError):
    def __init__(self, name: str, message: str = None):
        super().__init__(message or "The request parameter '{}' was not valid".format(name))
        self.name = name

class MissingParameterError(BadParameterError):
    def __init__(self, name: str, message: str = None):
        super().__init__(name, message or "The input parameter '{}' was not found.".format(name))
