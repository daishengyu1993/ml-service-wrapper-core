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

import urllib2

import json

class FastTextServiceBase(mlservicewrapper.services.Service):
    async def load(self, ctx: mlservicewrapper.contexts.ServiceContext):
        model_path = self.get_model_path(ctx)
        
        if not os.path.exists(model_path):
            url = self.get_model_url(ctx)
            
            filedata = urllib2.urlopen(url)
            datatowrite = filedata.read()
            
            with open(model_path, 'wb') as f:
                f.write(datatowrite)

        self.__model = fasttext.load_model(model_path)

    def get_model_path(self, ctx: mlservicewrapper.contexts.ServiceContext):
        return ctx.get_parameter_value("ModelPath", required=True)
    
    def get_model_url(self, ctx: mlservicewrapper.contexts.ServiceContext):
        return ctx.get_parameter_value("ModelUrl", required=True)

class FastTextVectorizerService(FastTextServiceBase):

    async def process(self, ctx: mlservicewrapper.contexts.ProcessContext):
        input_data = await ctx.get_input_dataframe("Data")

        if "Text" not in input_data.columns:
            raise mlservicewrapper.errors.MissingDatasetFieldError("Data", "Text")

        input_data["Vector"] = input_data["Text"].str.replace("\n", "").apply(lambda x: json.dumps(self.__model.get_sentence_vector(x).tolist()))
        input_data.drop(["Text"], inplace=True, axis="columns")

        await ctx.set_output_dataframe("Results", input_data)

class LanguageDetectionService(FastTextServiceBase):

    async def process(self, ctx: mlservicewrapper.contexts.ProcessContext):
        input_data = await ctx.get_input_dataframe("Data")

        if "Text" not in input_data.columns:
            raise mlservicewrapper.errors.MissingDatasetFieldError("Data", "Text")

        input_data["DetectedLanguage"] = input_data["Text"].str.replace("\n", "").apply(lambda x: json.dumps(self.__model.predict(x)))
        input_data.drop(["Text"], inplace=True, axis="columns")

        await ctx.set_output_dataframe("Results", input_data)

    def get_model_url(self, ctx: mlservicewrapper.contexts.ServiceContext):
        return "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
