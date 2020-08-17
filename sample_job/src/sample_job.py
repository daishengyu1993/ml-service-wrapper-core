import asyncio
import os
import time

from pandas import DataFrame

import mljobwrapper
import mljobwrapper.contexts
import mljobwrapper.services
import sample_dal


class SampleJob(mljobwrapper.services.JobService):
    async def load(self, ctx: mljobwrapper.contexts.ServiceContext):
        self.__mod_by = int(ctx.get_parameter_value("ModBy", "2"))

    async def process(self, ctx: mljobwrapper.contexts.JobRunContext):
        input_data = await ctx.get_input_dataframe("data")

        result = sample_dal.process(input_data["TextField"], self.__mod_by)
        result.insert(0, "Id", input_data["Id"])

        await ctx.set_output_dataframe("Results", result)
