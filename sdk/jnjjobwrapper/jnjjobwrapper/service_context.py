
class ServiceContext:
    def get_parameter_value(self, name: str, default: str = None) -> str:
        raise NotImplementedError()
