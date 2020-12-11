import asyncio

import pandas as pd

import mlservicewrapper
import mlservicewrapper.core.contexts
import mlservicewrapper.core.services
import mlservicewrapper.core.errors

import pandas as pd
import re
import numpy as np
from gensim.models import FastText
from scipy.spatial.distance import cosine
from unidecode import unidecode
from nltk import flatten
from utils import *
from nltk import flatten
import Constants
import string
import pickle
import os


class SampleService(mlservicewrapper.core.services.Service):
    async def load(self, ctx: mlservicewrapper.core.contexts.ServiceContext):
        relative_model_path = os.path.join(os.path.dirname(__file__), Constants.fastText_model_name)
        self.load_model = load_model_method(relative_model_path)
        
    async def process(self, ctx: mlservicewrapper.core.contexts.ProcessContext):
        # read the input
        input_data = await ctx.get_input_dataframe("Data")
        # print(input_data)

        # check input fields
        if "Physical Manufacturer" not in input_data.columns:
            raise mlservicewrapper.core.errors.MissingDatasetFieldError("Data", "Physical Manufacturer")
        if "License PM" not in input_data.columns:
            raise mlservicewrapper.core.errors.MissingDatasetFieldError("Data", "License PM")
        
        # process the input
        df_handled_empty_cell = handling_empty_cells(input_data)
        df_handled_empty_cell[Constants.non_empty_license_pm_df] = df_handled_empty_cell[Constants.non_empty_license_pm_df].apply(lambda x:replace_special_characters(x))
        dataframe_dropna = df_handled_empty_cell.drop_duplicates(subset=[Constants.license_pm,Constants.physical_manufacture], keep='first', inplace=False)
        zip_code_df = zip_code_extraction(dataframe_dropna)
        cleaned_df = data_cleaning(zip_code_df)

        # match the result
        df_jaccard_sim = distance_matrix(cleaned_df, self.load_model)
        df_jaccard_sim_final = df_jaccard_sim[df_jaccard_sim.columns[~df_jaccard_sim.columns.isin(Constants.custom_cols_list)]] 
        
        Result = df_jaccard_sim_final[[Constants.physical_manufacture, Constants.license_pm,
        Constants.max_similarity_col, Constants.pm_expectation_col]]
        Result[Constants.max_similarity_col].astype(str).replace('','NA')
        
        # print(df_jaccard_sim_final)
        await ctx.set_output_dataframe("Results", Result)

