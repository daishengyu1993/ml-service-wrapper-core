
from pandas import DataFrame

from .service_context import ServiceContext


class JobRunContext:
    def get_parameter_value(self, name: str, default: str = None) -> str:
        raise NotImplementedError()
    
    def get_data(self) -> DataFrame:
        raise NotImplementedError()
