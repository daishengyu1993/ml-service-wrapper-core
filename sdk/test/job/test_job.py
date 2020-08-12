
import time

from jnjjobwrapper import JobRunContext, JobService, ServiceContext, run_local
from pandas import DataFrame


class TestJob(JobService):
    def __init__(self):
        print("TestJob constructed")

    def load(self, ctx: ServiceContext) -> None:
        print("TestJob load")

        time.sleep(5)
        
        self.mod_by = int(ctx.get_parameter_value("modBy"))

        print("TestJob loaded")

    def get_results(self, ctx: JobRunContext) -> DataFrame:
        print("TestJob get_results")

        input_data = ctx.get_data()
        
        text_field = ctx.get_parameter_value("textField")

        result = DataFrame(input_data[text_field].str.len() % self.mod_by)

        result.columns = ["Result"]

        return result

    def dispose(self) -> None:
        pass

if __name__ == "__main__":
    print("Running debug mode...")

    with TestJob() as job:
        load_parameters = {
            "modBy": "3"
        }

        runtime_parameters = {
            "textField": "Text"
        }

        df = run_local(job, "./input.csv", "DocumentId", load_parameters=load_parameters, runtime_parameters=runtime_parameters, output_file_path="./output.csv")
    
    pass
