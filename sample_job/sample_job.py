
import asyncio
import time

from pandas import DataFrame

import mljobwrapper
import mljobwrapper.contexts
import mljobwrapper.job_service
import sample_dal


class SampleJob(mljobwrapper.job_service.JobService):
    def __init__(self):
        print("TestJob constructed")

    async def load(self, ctx: mljobwrapper.contexts.ServiceContext):
        print("TestJob load")

        self.__mod_by = 3

        await asyncio.sleep(5)
        
        print("TestJob loaded")

    async def process(self, ctx: mljobwrapper.contexts.JobRunContext):
        print("TestJob process")

        input_data = await ctx.get_input_dataframe("data")

        text_field = ctx.get_parameter_value("textField")

        result = sample_dal.process(input_data[text_field], self.__mod_by)

        await ctx.set_output_dataframe("output", result)

service = SampleJob()
