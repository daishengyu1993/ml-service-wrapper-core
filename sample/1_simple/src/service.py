import asyncio

import pandas as pd

import mlservicewrapper
import mlservicewrapper.core.contexts
import mlservicewrapper.core.services
import mlservicewrapper.core.errors

class SampleService(mlservicewrapper.core.services.Service):
    async def load(self, ctx: mlservicewrapper.core.contexts.ServiceContext):
        self.__mod_by = int(ctx.get_parameter_value("ModBy", default="2"))

    async def process(self, ctx: mlservicewrapper.core.contexts.ProcessContext):
        input_data = await ctx.get_input_dataframe("Data")

        if "TextField" not in input_data.columns:
            raise mlservicewrapper.core.errors.MissingDatasetFieldError("Data", "TextField")

        result = pd.DataFrame(input_data["TextField"].str.len() % self.__mod_by)

        result.columns = ["Result"]
        result.insert(0, "Id", input_data["Id"])

        await ctx.set_output_dataframe("Results", result)
