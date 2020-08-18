import asyncio
import os
import time

from pandas import DataFrame

import dal
import mlservicewrapper
import mlservicewrapper.contexts
import mlservicewrapper.services
import mlservicewrapper.errors

import fasttext

class LanguageIdentificationService(mlservicewrapper.services.Service):
    async def load(self, ctx: mlservicewrapper.contexts.ServiceContext):
        self.__model_path = ctx.get_parameter_value("ModelPath", required=False)
        self.__model_url = ctx.get_parameter_value("ModelUrl", required=False)

    async def process(self, ctx: mlservicewrapper.contexts.ProcessContext):
        input_data = await ctx.get_input_dataframe("Data")

        if "TextField" not in input_data.columns:
            raise mlservicewrapper.errors.MissingDatasetFieldError("Data", "TextField")

        result = dal.process(input_data, self.__mod_by)

        await ctx.set_output_dataframe("Results", result)
