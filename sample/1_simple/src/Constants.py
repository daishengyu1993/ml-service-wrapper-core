#!/usr/bin/env python
# encoding: utf-8
"""
Constants.py
"""

# physical_manufactured_cleaned = 'physical_manufactured_cleaned'
# license_pm_cleaned = 'license_pm_cleaned'
license_pm_wo_zip_code = 'license_pm_wo_zip_code'
license_pm_zip_code = 'license_pm_zip_code'
pm_wo_zip_code = 'pm_wo_zip_code'
pm_zip_code = 'pm_zip_code'
cleaned_pm = 'cleaned_pm'
cleaned_license_pm = 'cleaned_license_pm'
non_empty_pm_df = 'non_empty_pm_df'
non_empty_license_pm_df ='non_empty_license_pm_df'
physical_manufacture = 'Physical Manufacturer'
license_pm = 'License PM'
license_pm_error_message = 'Error-No information in license PM column'
pm_error_message = 'Error-No information in PM column'
error_message = 'Error-Similarity too low for this license product'
no_value = ''


pm_similarity_col = 'pm_similarity'
max_similarity_col = 'max_similarity_score'
pm_expectation_col = 'pm_expectation'
max_similarity_index_col = 'max_similarity_index'

# list of custom columns created

custom_cols_list =[non_empty_pm_df,non_empty_license_pm_df,license_pm_wo_zip_code,pm_wo_zip_code,max_similarity_index_col]

# Regex for zip code extarction

zip_code_regex = r'\d{5,}-\d{4,}|\d{5,}|\d{4,}|[A-Z]\d[A-Z] \d[A-Z]\d|[A-Z]+\d \d[A-Z]+|[A-Z]{2,}\d{2,} \d[A-Z]{2,}|\d{3,} \d{2,} |[A-Z]\d{2} \d[A-Z]{2}|[A-Z]{2}\d{2}[A-Z]{2}'

# Regex fro removing special characters 

spec_chars_regex = r'[.,#!;-]'
#remove_dots_regex = r'[.]'


# Threshold for similarity score 
jaccard_threshold = 80
cosine_threshold = 35
acceptance_threshold = 70

# Model file name

fastText_model_name = 'fastText_model.model'

BERT_model_name = 'BERT_model.model'

# Input file path 
input_file_path = '/Users/sdai9/rsc/RSC_Code/License Product Details (CHINA)V1.xlsx'
worksheet_name = 'connectivity'

