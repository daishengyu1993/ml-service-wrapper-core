
from pandas import DataFrame


class ServiceContext:
    def get_parameter_value(self, name: str, default: str = None) -> str:
        raise NotImplementedError()

class JobRunContext:
    def get_parameter_value(self, name: str, default: str = None) -> str:
        raise NotImplementedError()
    
    def get_data(self) -> DataFrame:
        raise NotImplementedError()
