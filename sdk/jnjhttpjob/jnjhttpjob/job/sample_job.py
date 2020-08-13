
import time

from pandas import DataFrame

import sample_dal
from jnjjobwrapper import JobRunContext, JobService, ServiceContext, run_local


class SampleJob(JobService):
    def __init__(self):
        print("TestJob constructed")

    def load(self, ctx: ServiceContext) -> None:
        print("TestJob load")

        self.mod_by = 3

        time.sleep(5)
        
        print("TestJob loaded")

    def get_results(self, ctx: JobRunContext) -> DataFrame:
        print("TestJob get_results")

        input_data = ctx.get_data()

        text_field = ctx.get_parameter_value("textField")

        return sample_dal.process(input_data[text_field], self.mod_by)

    def dispose(self) -> None:
        pass
