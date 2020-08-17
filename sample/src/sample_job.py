import asyncio
import os
import time

from pandas import DataFrame

import mlservicewrapper
import mlservicewrapper.contexts
import mlservicewrapper.services
import sample_dal


class SampleService(mlservicewrapper.services.Service):
    async def load(self, ctx: mlservicewrapper.contexts.ServiceContext):
        self.__mod_by = int(ctx.get_parameter_value("ModBy", "2"))

    async def process(self, ctx: mlservicewrapper.contexts.ProcessContext):
        input_data = await ctx.get_input_dataframe("data")

        result = sample_dal.process(input_data["TextField"], self.__mod_by)
        result.insert(0, "Id", input_data["Id"])

        await ctx.set_output_dataframe("Results", result)
