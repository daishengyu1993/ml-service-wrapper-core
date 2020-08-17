import asyncio
import os
import time

from pandas import DataFrame

import dal
import mlservicewrapper
import mlservicewrapper.contexts
import mlservicewrapper.services
import mlservicewrapper.errors


class SampleService(mlservicewrapper.services.Service):
    async def load(self, ctx: mlservicewrapper.contexts.ServiceContext):
        self.__mod_by = int(ctx.get_parameter_value("ModBy", default="2"))

    async def process(self, ctx: mlservicewrapper.contexts.ProcessContext):
        input_data = await ctx.get_input_dataframe("Data")

        if "TextField" not in input_data.columns:
            raise mlservicewrapper.errors.MissingDatasetFieldError("Data", "TextField")

        result = dal.process(input_data, self.__mod_by)

        await ctx.set_output_dataframe("Results", result)
